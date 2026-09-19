#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Split the rootless words into chunks for a final root-assignment pass.

Input : data/final_words.tsv
Output: data/fill/fill_NN.tsv (word <TAB> meaning)
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "fill")
SIZE = 120


def main():
    rows = []
    with io.open(os.path.join(DATA, "final_words.tsv"), "r", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 7 and not p[4].strip():
                rows.append((p[0], p[2]))

    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".tsv"):
            os.remove(os.path.join(OUT, f))

    n = 0
    for i in range(0, len(rows), SIZE):
        n += 1
        part = rows[i:i + SIZE]
        with io.open(os.path.join(OUT, "fill_%02d.tsv" % n), "w", encoding="utf-8", newline="\n") as fh:
            for w, m in part:
                fh.write("%s\t%s\n" % (w, m))
        print("  fill_%02d.tsv  %3d  %s .. %s" % (n, len(part), part[0][0], part[-1][0]))
    print("rootless=%d chunks=%d" % (len(rows), n))


if __name__ == "__main__":
    main()
