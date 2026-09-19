#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Build the 'new words' chunk files: headwords present in cet4_full_source.tsv
but absent from the truncated cet4_AS.tsv extract (i.e. the sh..sy tail of S plus T-Z).

Output: data/new/new_NN.tsv  (word <TAB> phonetic <TAB> meaning)
        data/cet4_new.tsv    (same, un-chunked, for records)
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "new")
SIZE = 130


def load(path):
    d = {}
    order = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if not p or not p[0].strip():
                continue
            while len(p) < 3:
                p.append("")
            k = p[0].strip().lower()
            if k in d:
                continue
            d[k] = (p[0].strip(), p[1].strip(), p[2].strip())
            order.append(k)
    return d, order


def main():
    old, _ = load(os.path.join(DATA, "cet4_AS.tsv"))
    full, order = load(os.path.join(DATA, "cet4_full_source.tsv"))
    new = [full[k] for k in order if k not in old]
    print("full=%d old=%d new=%d" % (len(full), len(old), len(new)))

    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".tsv"):
            os.remove(os.path.join(OUT, f))

    with io.open(os.path.join(DATA, "cet4_new.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        for w, p, m in new:
            fh.write("%s\t%s\t%s\n" % (w, p, m))

    n = 0
    for i in range(0, len(new), SIZE):
        n += 1
        part = new[i:i + SIZE]
        name = "new_%02d.tsv" % n
        with io.open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as fh:
            for w, p, m in part:
                fh.write("%s\t%s\t%s\n" % (w, p, m))
        print("  %s  %3d  %s .. %s" % (name, len(part), part[0][0], part[-1][0]))
    print("chunks=%d  TOTAL_NEW=%d" % (n, len(new)))


if __name__ == "__main__":
    main()
