#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Build the top-up candidate list.

Candidates = new-block words that the classifier rated tier 1 or 2 (i.e. it agreed
they are CET-4 core) but that were rejected by the 50% quota. We ask a second pass
to add back the best ~N of these to reach the 2000-word target.

Inputs : data/cet4_new.tsv, data/newkeep/new_keep_*.tsv
Output : data/topup/topup_NN.tsv  (word <TAB> tier <TAB> root <TAB> meaning <TAB> gloss)
"""
import glob
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "topup")
SIZE = 130


def norm(w):
    return w.replace("\ufeff", "").strip().lower()


def read_rows(path, minlen=1):
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip() or line.startswith("```"):
                continue
            p = [x.strip() for x in line.split("\t")]
            while len(p) < minlen:
                p.append("")
            rows.append(p)
    return rows


def main():
    src = {}
    order = []
    for r in read_rows(os.path.join(DATA, "cet4_new.tsv"), 3):
        k = norm(r[0])
        if k not in src:
            src[k] = r
            order.append(k)

    dec = {}
    for f in sorted(glob.glob(os.path.join(DATA, "newkeep", "new_keep_*.tsv"))):
        for r in read_rows(f, 5):
            if len(r) >= 4:
                dec[norm(r[0])] = r

    cands = []
    for k in order:
        d = dec.get(k)
        if d is None:
            continue
        tier = d[1].strip().lower()
        keep = d[3].strip()
        if keep == "1":
            continue
        if tier not in ("1", "2", "t1", "t2"):
            continue
        s = src[k]
        gloss = (d[4] if len(d) > 4 else "").strip()
        cands.append([s[0], tier.lstrip("t"), d[2].strip(), s[2].strip() or gloss])

    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".tsv"):
            os.remove(os.path.join(OUT, f))

    n = 0
    for i in range(0, len(cands), SIZE):
        n += 1
        part = cands[i:i + SIZE]
        with io.open(os.path.join(OUT, "topup_%02d.tsv" % n), "w", encoding="utf-8", newline="\n") as fh:
            for r in part:
                fh.write("\t".join(r) + "\n")
        print("  topup_%02d.tsv  %3d  %s .. %s" % (n, len(part), part[0][0], part[-1][0]))
    print("candidates=%d chunks=%d" % (len(cands), n))


if __name__ == "__main__":
    main()
