#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Split the tagged wordlist into core-word chunks for the selection pass.

Input : data/tagged_*.tsv   (word, phonetic, meaning, tier, root, roots, note)
Output: data/core/<prefix>_core_NN.tsv   (word <TAB> tier <TAB> root <TAB> meaning)
        with an index header file data/core/<prefix>_core_index.tsv

Usage: py -3 scripts/split_core.py AS 145
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUTDIR = os.path.join(DATA, "core")


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "AS"
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 145

    rows = []
    with io.open(os.path.join(DATA, "tagged_%s.tsv" % prefix), "r", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            rows.append(p)

    core = [r for r in rows if r[3] in ("1", "2")]
    os.makedirs(OUTDIR, exist_ok=True)

    # wipe old chunks for this prefix
    for old in glob.glob(os.path.join(OUTDIR, "%s_core_*.tsv" % prefix.lower())):
        os.remove(old)

    index = []
    n = 0
    for i in range(0, len(core), size):
        n += 1
        part = core[i:i + size]
        name = "%s_core_%02d.tsv" % (prefix.lower(), n)
        path = os.path.join(OUTDIR, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            for r in part:
                fh.write("%s\t%s\t%s\t%s\n" % (r[0], r[3], r[4], r[2]))
        index.append((name, len(part), part[0][0], part[-1][0]))

    print("prefix=%s core=%d chunks=%d size=%d" % (prefix, len(core), n, size))
    for name, cnt, first, last in index:
        print("  %s  %3d  %s .. %s" % (name, cnt, first, last))
    print("TOTAL_CORE=%d" % len(core))


if __name__ == "__main__":
    main()
