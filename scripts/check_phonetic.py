#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Sanity-check every 音标 in data/final_words.tsv.

NOTE: IPA is written with Latin letters, so *do not* flag values merely because
they contain A-Z characters. Only structurally broken values are flagged:
  * a '/' or '\\' (a field separator leaked in from the source)
  * a CJK character (a gloss leaked in)
  * length > 26 characters

Report-only unless --fix is passed; --fix blanks the flagged values
(a blank cell is better than a wrong one).
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

CJK = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
MAXLEN = 26


def main():
    fix = "--fix" in sys.argv
    path = os.path.join(DATA, "final_words.tsv")
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 7:
                rows.append(p)

    bad = []
    for r in rows:
        ph = r[1]
        if not ph:
            continue
        if "/" in ph or "\\" in ph:
            bad.append((r[0], ph, "contains slash"))
        elif CJK.search(ph):
            bad.append((r[0], ph, "contains CJK"))
        elif len(ph) > MAXLEN:
            bad.append((r[0], ph, "too long (%d)" % len(ph)))

    total = sum(1 for r in rows if r[1])
    print("phonetic values: %d / %d" % (total, len(rows)))
    print("flagged: %d" % len(bad))
    for w, ph, why in bad:
        print("   %-16s %-40s %s" % (w, ph, why))

    if fix and bad:
        changed = 0
        cleared = []
        for r in rows:
            for w, ph, why in bad:
                if r[0] != w:
                    continue
                head = ph.split("/")[0].split("\\")[0].strip()
                if 2 < len(head) <= MAXLEN and not CJK.search(head):
                    r[1] = head          # salvage the valid leading phonetic
                else:
                    r[1] = ""
                    cleared.append(w)
                changed += 1
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write("\t".join(x.replace("\t", " ") for x in r) + "\n")
        print("repaired %d flagged phonetics (cleared %d outright)" % (changed, len(cleared)))
        print("remaining with phonetic: %d / %d" % (sum(1 for r in rows if r[1]), len(rows)))
    elif bad:
        print("(report only - re-run with --fix to repair them)")


if __name__ == "__main__":
    main()
