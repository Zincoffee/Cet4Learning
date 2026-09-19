#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Apply the final root-fill pass onto final_words.tsv.

Inputs : data/final_words.tsv, data/fill/fill_NN.tsv, data/fillkeep/fill_NN.tsv
Output : data/final_words.tsv (rewritten in place)
"""
import glob
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def norm(w):
    return w.replace("\ufeff", "").strip().lower()


def load_canon():
    canon = {}
    with io.open(os.path.join(DATA, "roots_canonical.tsv"), "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            p = line.split("\t")
            if len(p) >= 2:
                canon[p[0].strip()] = p[1].strip()
    return canon


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
    canon = load_canon()
    rows = [r for r in read_rows(os.path.join(DATA, "final_words.tsv"), 7) if len(r) >= 7]
    by = {}
    order = []
    for r in rows:
        k = norm(r[0])
        by[k] = r
        order.append(k)

    assigned = {}
    misaligned = 0
    for f in sorted(glob.glob(os.path.join(DATA, "fillkeep", "fill_*.tsv"))):
        for r in read_rows(f, 4):
            if len(r) < 2:
                continue
            assigned[norm(r[0])] = r

    # alignment check against the fill input chunks
    for f in sorted(glob.glob(os.path.join(DATA, "fill", "fill_*.tsv"))):
        for r in read_rows(f, 2):
            k = norm(r[0])
            v = assigned.get(k)
            if v is not None and norm(v[0]) != k:
                misaligned += 1

    filled = multi_added = bad_root = 0
    for k in order:
        r = by[k]
        v = assigned.get(k)
        if v is None or not v[1].strip():
            continue
        root = v[1].strip()
        if root not in canon:
            bad_root += 1
            continue
        if r[4].strip():
            continue
        r[4] = root
        filled += 1
        if len(v) > 2 and v[2].strip():
            comps = [c.strip() for c in v[2].split(",") if c.strip()]
            if len(comps) >= 2 and all(c in canon for c in comps):
                r[5] = ",".join(comps)
                r[6] = v[3].strip() or "+".join("%s(%s)" % (c, canon[c]) for c in comps)
                multi_added += 1

    dst = os.path.join(DATA, "final_words.tsv")
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for k in order:
            fh.write("\t".join(x.replace("\t", " ") for x in by[k]) + "\n")

    total = len(order)
    with_root = sum(1 for k in order if by[k][4].strip())
    multi = sum(1 for k in order if by[k][5].strip())
    print("roots filled         : %d" % filled)
    print("non-canonical roots  : %d" % bad_root)
    print("multi-root added     : %d" % multi_added)
    print("misaligned rows      : %d" % misaligned)
    print("with root            : %d/%d (%.1f%%)" % (with_root, total, 100.0 * with_root / total))
    print("total annotated      : %d" % multi)
    print("wrote %s" % dst)


if __name__ == "__main__":
    main()
