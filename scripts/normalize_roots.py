#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Normalise a handful of root assignments on data/final_words.tsv.

Fixes three classes of problem found by scripts/audit_roots.py:
  1. two canonical roots sharing a key ("cur 跑/流" vs "cur 关心/照料",
     "sol 太阳" vs "sol 单独") - resolved by renaming one of each pair;
  2. root spellings that are *variants* in the canonical table rather than keys
     (spect -> spec, sta -> sist);
  3. roots that were genuinely missing from the table (rat, rot, urg) - added there.
Overrides live in data/root_fix.tsv (word <TAB> root).
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def main():
    fix = {}
    with io.open(os.path.join(DATA, "root_fix.tsv"), "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) >= 2 and p[1].strip():
                fix[p[0].strip().lower()] = p[1].strip()

    path = os.path.join(DATA, "final_words.tsv")
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 7:
                rows.append(p)

    changed = 0
    notfound = []
    seen = set()
    for r in rows:
        k = r[0].lower()
        if k in fix and r[4].strip() != fix[k]:
            r[4] = fix[k]
            changed += 1
            seen.add(k)
    for k in fix:
        if k not in seen and k not in set(r[0].lower() for r in rows):
            notfound.append(k)

    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write("\t".join(x.replace("\t", " ") for x in r) + "\n")

    print("override entries: %d   rows changed: %d" % (len(fix), changed))
    if notfound:
        print("override words not in the table: %s" % notfound)


if __name__ == "__main__":
    main()
