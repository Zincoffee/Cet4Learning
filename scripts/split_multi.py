#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Split rooted words into chunks for the multi-root verification pass.

Input : data/final_<PX>.tsv (word, phonetic, meaning, tier, root, roots, note)
Output: data/multi/<px>_multi_NN.tsv (word <TAB> root <TAB> roots <TAB> note <TAB> meaning)
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "multi")


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "AS"
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 125
    path = os.path.join(DATA, "final_%s.tsv" % prefix)
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 7 and p[4].strip():
                rows.append(p)

    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "%s_multi_*.tsv" % prefix.lower())):
        os.remove(old)

    n = 0
    index = []
    for i in range(0, len(rows), size):
        n += 1
        part = rows[i:i + size]
        name = "%s_multi_%02d.tsv" % (prefix.lower(), n)
        with io.open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as fh:
            for r in part:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (r[0], r[4], r[5], r[6], r[2]))
        index.append((name, len(part)))
    print("prefix=%s rooted=%d chunks=%d" % (prefix, len(rows), n))
    for name, cnt in index:
        print("  %s  %d" % (name, cnt))


if __name__ == "__main__":
    main()
