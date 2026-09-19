#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Minimal, dependency-free .xlsx writer (stdlib zipfile + XML).

Only the features this project needs: inline strings, a fixed style table,
column widths, frozen header row, autofilter, merged cells, row heights.
"""
import io
import re
import zipfile

ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def esc(s):
    s = ILLEGAL.sub("", str(s))
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def col_name(i):
    """1-based column index -> A, B, ... AA"""
    name = ""
    while i > 0:
        i, r = divmod(i - 1, 26)
        name = chr(65 + r) + name
    return name


# ---------------------------------------------------------------- styles ----
FONT = (
    '<font><sz val="11"/><name val="微软雅黑"/><charset val="134"/></font>',
    '<font><b/><sz val="14"/><name val="微软雅黑"/><charset val="134"/></font>',
    '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="微软雅黑"/><charset val="134"/></font>',
    '<font><b/><sz val="12"/><name val="微软雅黑"/><charset val="134"/></font>',
    '<font><b/><sz val="11"/><name val="微软雅黑"/><charset val="134"/></font>',
    '<font><sz val="9"/><name val="微软雅黑"/><charset val="134"/></font>',
)

FILL = (
    '<fill><patternFill patternType="none"/></fill>',
    '<fill><patternFill patternType="gray125"/></fill>',
    '<fill><patternFill patternType="solid"><fgColor rgb="FF2F5597"/><bgColor indexed="64"/></patternFill></fill>',
    '<fill><patternFill patternType="solid"><fgColor rgb="FFFFFFFF"/><bgColor indexed="64"/></patternFill></fill>',
    '<fill><patternFill patternType="solid"><fgColor rgb="FFEAF1FB"/><bgColor indexed="64"/></patternFill></fill>',
    '<fill><patternFill patternType="solid"><fgColor rgb="FFFFE699"/><bgColor indexed="64"/></patternFill></fill>',
    '<fill><patternFill patternType="solid"><fgColor rgb="FFF2F2F2"/><bgColor indexed="64"/></patternFill></fill>',
)

BORDER = (
    '<border><left/><right/><top/><bottom/><diagonal/></border>',
    '<border><left style="thin"><color rgb="FFD0D7E5"/></left><right style="thin"><color rgb="FFD0D7E5"/></right>'
    '<top style="thin"><color rgb="FFD0D7E5"/></top><bottom style="thin"><color rgb="FFD0D7E5"/></bottom><diagonal/></border>',
)

# (font, fill, border, alignment)
XF = (
    (0, 0, 0, None),                                                    # 0 default
    (1, 0, 0, ("left", "center", 0)),                                   # 1 title
    (2, 2, 1, ("center", "center", 1)),                                 # 2 header
    (3, 5, 1, ("left", "center", 0)),                                   # 3 section
    (0, 3, 1, ("center", "center", 0)),                                 # 4 num A
    (0, 4, 1, ("center", "center", 0)),                                 # 5 num B
    (4, 3, 1, ("center", "center", 1)),                                 # 6 root A
    (4, 4, 1, ("center", "center", 1)),                                 # 7 root B
    (0, 3, 1, ("center", "center", 1)),                                 # 8 rootmean A
    (0, 4, 1, ("center", "center", 1)),                                 # 9 rootmean B
    (4, 3, 1, ("left", "center", 0)),                                   # 10 word A
    (4, 4, 1, ("left", "center", 0)),                                   # 11 word B
    (5, 3, 1, ("left", "center", 0)),                                   # 12 phon A
    (5, 4, 1, ("left", "center", 0)),                                   # 13 phon B
    (0, 3, 1, ("left", "top", 1)),                                      # 14 mean A
    (0, 4, 1, ("left", "top", 1)),                                      # 15 mean B
    (0, 3, 1, ("left", "top", 1)),                                      # 16 note A
    (0, 4, 1, ("left", "top", 1)),                                      # 17 note B
    (0, 6, 1, ("center", "center", 0)),                                 # 18 num gray
    (4, 6, 1, ("left", "center", 0)),                                   # 19 word gray
    (5, 6, 1, ("left", "center", 0)),                                   # 20 phon gray
    (0, 6, 1, ("left", "top", 1)),                                      # 21 mean gray
    (0, 6, 1, ("left", "top", 1)),                                      # 22 note gray
    (4, 0, 0, ("left", "center", 0)),                                   # 23 plain bold label
    (0, 0, 0, ("left", "top", 1)),                                      # 24 plain wrapped text
    (2, 2, 1, ("left", "center", 0)),                                   # 25 index header
)

ALIGN_ATTR = {0: "", 1: ' wrapText="1"'}


def _alignment(spec):
    if not spec:
        return ""
    h, v, wrap = spec
    return '<alignment horizontal="%s" vertical="%s"%s/>' % (h, v, ALIGN_ATTR[wrap])


def styles_xml():
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    out.append('<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')
    out.append('<fonts count="%d">%s</fonts>' % (len(FONT), "".join(FONT)))
    out.append('<fills count="%d">%s</fills>' % (len(FILL), "".join(FILL)))
    out.append('<borders count="%d">%s</borders>' % (len(BORDER), "".join(BORDER)))
    out.append('<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>')
    out.append('<cellXfs count="%d">' % len(XF))
    for f, fl, b, al in XF:
        out.append(
            '<xf numFmtId="0" fontId="%d" fillId="%d" borderId="%d" xfId="0" '
            'applyFont="1" applyFill="1" applyBorder="1"%s>%s</xf>'
            % (f, fl, b, ' applyAlignment="1"' if al else "", _alignment(al))
        )
    out.append("</cellXfs>")
    out.append('<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>')
    out.append("</styleSheet>")
    return "".join(out)


# ---------------------------------------------------------------- sheets ----
class Sheet(object):
    def __init__(self, name, widths, freeze_row=0, autofilter=None):
        self.name = name
        self.widths = widths          # list of (width, ) per column
        self.freeze_row = freeze_row
        self.autofilter = autofilter  # e.g. "A1:G1200"
        self.rows = []                # list of (height|None, [ (style, value) ])
        self.merges = []

    def add(self, height, cells):
        self.rows.append((height, cells))

    def merge(self, ref):
        self.merges.append(ref)

    def xml(self):
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
        out.append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')
        out.append('<sheetViews><sheetView workbookViewId="0">')
        if self.freeze_row:
            out.append(
                '<pane ySplit="%d" topLeftCell="A%d" activePane="bottomLeft" state="frozen"/>'
                % (self.freeze_row, self.freeze_row + 1)
            )
        out.append("</sheetView></sheetViews>")
        out.append('<sheetFormatPr defaultRowHeight="15"/>')
        if self.widths:
            out.append("<cols>")
            for i, w in enumerate(self.widths, 1):
                out.append('<col min="%d" max="%d" width="%s" customWidth="1"/>' % (i, i, w))
            out.append("</cols>")
        out.append("<sheetData>")
        for r, (height, cells) in enumerate(self.rows, 1):
            attrs = ' ht="%s" customHeight="1"' % height if height else ""
            out.append('<row r="%d"%s>' % (r, attrs))
            for c, cell in enumerate(cells, 1):
                if cell is None:
                    continue
                style, value = cell
                if value is None or value == "":
                    if style:
                        out.append('<c r="%s%d" s="%d"/>' % (col_name(c), r, style))
                    continue
                out.append(
                    '<c r="%s%d" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                    % (col_name(c), r, style, esc(value))
                )
            out.append("</row>")
        out.append("</sheetData>")
        if self.autofilter:
            out.append('<autoFilter ref="%s"/>' % self.autofilter)
        if self.merges:
            out.append('<mergeCells count="%d">' % len(self.merges))
            for m in self.merges:
                out.append('<mergeCell ref="%s"/>' % m)
            out.append("</mergeCells>")
        out.append("</worksheet>")
        return "".join(out)


def write_xlsx(path, sheets):
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    ct.append('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">')
    ct.append('<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>')
    ct.append('<Default Extension="xml" ContentType="application/xml"/>')
    ct.append('<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>')
    ct.append('<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>')
    for i in range(len(sheets)):
        ct.append('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1))
    ct.append("</Types>")

    rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'

    wb = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    wb.append('<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>')
    for i, s in enumerate(sheets, 1):
        wb.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (esc(s.name), i, i))
    wb.append("</sheets></workbook>")

    wbrels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i in range(len(sheets)):
        wbrels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i + 1, i + 1))
    wbrels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' % (len(sheets) + 1))
    wbrels.append("</Relationships>")

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", "".join(wb))
        z.writestr("xl/_rels/workbook.xml.rels", "".join(wbrels))
        z.writestr("xl/styles.xml", styles_xml())
        for i, s in enumerate(sheets, 1):
            z.writestr("xl/worksheets/sheet%d.xml" % i, s.xml())
    return path
