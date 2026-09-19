#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Apply the selection/root-completion pass, producing the final wordlist per prefix.

Inputs : data/core/<px>_core_NN.tsv   (word, tier, root, meaning)
         data/keep/<px>_keep_NN.tsv   (word, root, keep)
         data/tagged_<PX>.tsv         (word, phonetic, meaning, tier, root, roots, note)
Output : data/final_<PX>.tsv          (word, phonetic, meaning, tier, root, roots, note)
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def norm(w):
    return w.replace("\ufeff", "").strip().lower()


def read_tsv(path):
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip() or line.startswith("```"):
                continue
            rows.append([p.strip() for p in line.split("\t")])
    return rows


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "AS"
    px = prefix.lower()

    tagged = {}
    order = []
    for r in read_tsv(os.path.join(DATA, "tagged_%s.tsv" % prefix)):
        if len(r) < 7:
            continue
        order.append(norm(r[0]))
        tagged[norm(r[0])] = r

    keep_files = sorted(glob.glob(os.path.join(DATA, "keep", "%s_keep_*.tsv" % px)))
    decisions = {}
    problems = []
    for f in keep_files:
        rows = read_tsv(f)
        for r in rows:
            if len(r) < 3:
                problems.append("%s: short row %r" % (os.path.basename(f), r))
                continue
            w = norm(r[0])
            decisions[w] = (r[1].strip(), r[2].strip())

    print("tagged: %d   decisions: %d   from %d files" % (len(tagged), len(decisions), len(keep_files)))
    for p in problems[:10]:
        print("  PROBLEM:", p)

    kept = 0
    dropped = 0
    missing = []
    root_filled = 0
    root_changed = 0
    out = []
    for w in order:
        r = tagged[w]
        d = decisions.get(w)
        if d is None:
            missing.append(w)
            continue
        root_new, keep = d
        root_old = r[4].strip()
        if root_old and root_new and norm(root_old) != norm(root_new):
            root_changed += 1
        if not root_old and root_new:
            root_filled += 1
        root = root_old or root_new
        if keep != "1":
            dropped += 1
            continue
        kept += 1
        out.append([r[0], r[1], r[2], r[3], root, r[5], r[6]])

    print("kept=%d dropped=%d words-without-decision=%d" % (kept, dropped, len(missing)))
    print("roots newly filled=%d  roots changed by pass2=%d" % (root_filled, root_changed))
    if missing:
        print("  e.g.", missing[:20])

    with_root = sum(1 for r in out if r[4])
    print("root coverage of kept: %d/%d = %.1f%%" % (with_root, kept, 100.0 * with_root / max(kept, 1)))
    multi = sum(1 for r in out if r[5].strip())
    print("words with multiple roots (annotated): %d" % multi)

    dst = os.path.join(DATA, "final_%s.tsv" % prefix)
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for r in out:
            fh.write("\t".join(x.replace("\t", " ") for x in r) + "\n")
    print("wrote %s" % dst)


if __name__ == "__main__":
    main()
