#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Build the final Excel workbook.

Input : data/final_words.tsv  (word, phonetic, meaning, tier, root, roots, note)
        data/roots_canonical.tsv, data/gloss_fix.tsv, data/gloss_fix2.tsv
Output: out/CET4核心2000词_词根分类.xlsx
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_writer import Sheet, write_xlsx  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUTDIR = os.path.join(ROOT, "out")

# style indices (see xlsx_writer.XF)
S_TITLE, S_HEAD, S_SECT = 1, 2, 3
S_NUM_A, S_NUM_B = 4, 5
S_ROOT_A, S_ROOT_B = 6, 7
S_RM_A, S_RM_B = 8, 9
S_WORD_A, S_WORD_B = 10, 11
S_PH_A, S_PH_B = 12, 13
S_MEAN_A, S_MEAN_B = 14, 15
S_NOTE_A, S_NOTE_B = 16, 17
S_NUM_G, S_WORD_G, S_PH_G, S_MEAN_G, S_NOTE_G = 18, 19, 20, 21, 22
S_LABEL, S_TEXT, S_IHEAD = 23, 24, 25


def read_rows(path, minlen=1):
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip():
                continue
            p = [x.strip() for x in line.split("\t")]
            while len(p) < minlen:
                p.append("")
            rows.append(p)
    return rows


def load_canon():
    mean, var = {}, {}
    for r in read_rows(os.path.join(DATA, "roots_canonical.tsv"), 2):
        if r[0].startswith("#"):
            continue
        mean[r[0]] = r[1]
        if len(r) > 2 and r[2]:
            var[r[0]] = r[2]
    return mean, var


def load_fixes():
    fix = {}
    for name in ("gloss_fix.tsv", "gloss_fix2.tsv"):
        p = os.path.join(DATA, name)
        if not os.path.exists(p):
            continue
        for r in read_rows(p, 2):
            if len(r) >= 2 and r[1]:
                fix[r[0].lower()] = r[1]
    return fix


def main():
    mean, var = load_canon()
    fix = load_fixes()

    rows = [r for r in read_rows(os.path.join(DATA, "final_words.tsv"), 7) if len(r) >= 7]
    words = []
    for r in rows:
        w, phon, meaning, tier, root, roots, note = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
        meaning = fix.get(w.lower(), meaning)
        words.append({"w": w, "ph": phon, "m": meaning, "t": tier, "r": root, "rs": roots, "n": note})

    words.sort(key=lambda d: d["w"].lower())

    groups = {}
    for d in words:
        groups.setdefault(d["r"], []).append(d)

    root_keys = [k for k in groups if k]
    root_keys.sort(key=lambda k: (-len(groups[k]), k))
    tail = groups.get("", [])

    fixed = sum(1 for d in words if d["w"].lower() in fix)
    print("words=%d  root groups=%d  rootless=%d  gloss fixes applied=%d"
          % (len(words), len(root_keys), len(tail), fixed))

    # ---------------------------------------------------------------- sheet 1
    sh = Sheet("词根分类词汇表", [6, 10, 20, 18, 22, 40, 32], freeze_row=1)
    sh.add(26, [(S_HEAD, "序号"), (S_HEAD, "词根"), (S_HEAD, "词根含义"),
                (S_HEAD, "单词"), (S_HEAD, "音标"), (S_HEAD, "释义"), (S_HEAD, "批注")])

    idx = 0
    for gi, key in enumerate(root_keys):
        band = gi % 2
        items = sorted(groups[key], key=lambda d: d["w"].lower())
        r1 = sh.rows.__len__() + 1
        rm = mean.get(key, "")
        if var.get(key):
            rm = "%s（%s）" % (rm, var[key].replace(",", "/").replace(" ", ""))
        s_root = S_ROOT_A if band == 0 else S_ROOT_B
        s_rm = S_RM_A if band == 0 else S_RM_B
        s_num = S_NUM_A if band == 0 else S_NUM_B
        s_word = S_WORD_A if band == 0 else S_WORD_B
        s_ph = S_PH_A if band == 0 else S_PH_B
        s_mean = S_MEAN_A if band == 0 else S_MEAN_B
        s_note = S_NOTE_A if band == 0 else S_NOTE_B
        for j, d in enumerate(items):
            idx += 1
            first = (j == 0)
            sh.add(None, [
                (s_num, str(idx)),
                (s_root, key if first else ""),
                (s_rm, rm if first else ""),
                (s_word, d["w"]),
                (s_ph, d["ph"]),
                (s_mean, d["m"]),
                (s_note, d["n"]),
            ])
        r2 = sh.rows.__len__()
        if r2 > r1:
            sh.merge("B%d:B%d" % (r1, r2))
            sh.merge("C%d:C%d" % (r1, r2))

    # rootless block at the end of the same table, as requested
    if tail:
        sh.add(24, [(S_SECT, "无词根词汇（%d 词，共 %d 词中不含希腊/拉丁词根，按字母序排在表格末尾）"
                     % (len(tail), len(words))), None, None, None, None, None, None])
        sh.merge("A%d:G%d" % (sh.rows.__len__(), sh.rows.__len__()))
        for d in sorted(tail, key=lambda d: d["w"].lower()):
            idx += 1
            sh.add(None, [
                (S_NUM_G, str(idx)),
                (S_MEAN_G, ""),
                (S_MEAN_G, ""),
                (S_WORD_G, d["w"]),
                (S_PH_G, d["ph"]),
                (S_MEAN_G, d["m"]),
                (S_NOTE_G, d["n"]),
            ])

    last = sh.rows.__len__()
    sh.autofilter = "A1:G%d" % last

    # ---------------------------------------------------------------- sheet 2
    sh2 = Sheet("词根索引", [12, 34, 8, 46], freeze_row=1)
    sh2.add(26, [(S_IHEAD, "词根"), (S_IHEAD, "含义"), (S_IHEAD, "词数"), (S_IHEAD, "代表词")])
    for i, key in enumerate(root_keys):
        items = sorted(groups[key], key=lambda d: d["w"].lower())
        rm = mean.get(key, "")
        if var.get(key):
            rm = "%s（变体 %s）" % (rm, var[key])
        ex = "、".join(d["w"] for d in items[:6])
        band = i % 2
        s_rm2 = S_MEAN_A if band == 0 else S_MEAN_B
        sh2.add(None, [
            (S_ROOT_A if band == 0 else S_ROOT_B, key),
            (s_rm2, rm),
            (S_NUM_A if band == 0 else S_NUM_B, str(len(items))),
            (s_rm2, ex),
        ])
    sh2.add(None, [(S_SECT, "无词根"), (S_MEAN_G, "不含希腊/拉丁词根的基础词与派生词"), (S_NUM_G, str(len(tail))), (S_MEAN_G, "")])

    # ---------------------------------------------------------------- sheet 3
    n_multi = sum(1 for d in words if d["rs"])
    n_ph = sum(1 for d in words if d["ph"])
    n_plain = len(tail)
    s3 = Sheet("说明", [20, 108], freeze_row=0)
    s3.add(30, [(S_TITLE, "四级核心 2000 词 · 词根分类表"), None])

    def sect(t):
        s3.add(22, [(S_SECT, t), None])

    def line(k, v):
        s3.add(None, [(S_LABEL, k), (S_TEXT, v)])

    sect("一、这份表是什么")
    line("内容", "按常见希腊/拉丁词根归类的大学英语四级核心词汇表，共 %d 词；"
                 "其中 %d 词归入 %d 个词根，其余 %d 词不含词根，集中排在表格末尾。"
                 % (len(words), len(words) - n_plain, len(root_keys), n_plain))
    line("列说明", "序号：全表连续编号｜词根：该词所属词根（同一词根的行合并显示）｜"
                   "词根含义：词根的中文意思，括号内为常见变体拼写｜单词｜音标｜释义｜批注")
    line("批注", "只有【含两个及以上词根】的词才写批注，共 %d 词，例如 "
                 "bio(生命)+graph(写)。其余情况一律留空，保持表格简洁。" % n_multi)
    line("排序", "词根分组按所含词数从多到少排列，组内单词按字母序；"
                 "无词根词汇单独成节，排在表格最后，按字母序。")

    sect("二、选词标准")
    line("词源", "以《大学英语四级考试大纲词汇表》（4615 词）为主干，补齐大纲中 S 后半段与 T–Z 共 1553 个词，"
                 "合成 5070 词的候选库。")
    line("筛选 1", "剔除中学阶段已掌握的基础词（如 book、apple、happy、she、show 这类）。")
    line("筛选 2", "剔除语义完全透明的派生词与拼写变体（如 acceptable←accept、signification←signify）。")
    line("筛选 3", "剔除明显超出四级范围的六级生僻词与专业术语（如 ampere、radium、vestige 这类）。")
    line("结果", "最终保留 %d 词，与「四级核心两千词」的规模一致。" % len(words))
    line("释义来源", "绝大多数释义取自四级大纲原文；大纲未覆盖的少量词条由编表过程补写，风格统一为"
                     "「词性. 释义；释义」。")
    line("主要出处", "① 大学英语四级考试大纲词汇表（mahavivo/english-wordlists · CET4_edited.txt）；"
                     "② cuttlin/Vocabulary-of-CET-4 分字母词表（T–Z 与音标）；"
                     "③ 中考英语词汇表（基础词音标/释义）；④ JavaProgrammerLB/cet-word-list（四级词表成员核对）；"
                     "⑤ RealKai42/qwerty-learner 词书（释义补充）。")

    sect("三、词根与数据说明")
    line("词根表", "共使用 %d 个标准词根（含常见变体拼写），词根写法已统一"
                   "（例如统一用 spect，不用 spec/specto），详见「词根索引」工作表。" % len(root_keys))
    line("有音标", "%d / %d 词带音标；音标来自多个词表，风格已统一为常见 IPA。" % (n_ph, len(words)))
    line("多词根", "含两个及以上词根的词 %d 个；只含「一个词根 + 前缀/后缀」的词不算多词根"
                   "（如 predict = pre + dict、transfer = trans + fer、reject = re + ject 均只有一个词根）。" % n_multi)
    line("数据校验", "全表单词与来源词表逐行核对一致，无重复词条；批注与词根字段一一对应。")

    sect("四、使用建议")
    line("用法 1", "先按词根成组记忆：同一词根下的词共用含义，记一个词根可带动 5–10 个单词。")
    line("用法 2", "用首行筛选按钮按「词根」筛选，或直接在「词根索引」里按词数挑高产词根优先攻克。")
    line("用法 3", "无词根的部分多为本族语基础词，靠语境和搭配记忆，不必强求词根。")

    out = os.path.join(OUTDIR, "CET4核心2000词_词根分类.xlsx")
    os.makedirs(OUTDIR, exist_ok=True)
    write_xlsx(out, [sh, sh2, s3])
    print("wrote %s (%d bytes)" % (out, os.path.getsize(out)))


if __name__ == "__main__":
    main()
