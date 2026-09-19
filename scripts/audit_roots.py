#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Audit the canonical root table: duplicate keys, and roots used by the wordlist
that are missing from (or ambiguous in) the table."""
import io
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def main():
    entries = []
    for line in io.open(os.path.join(DATA, "roots_canonical.tsv"), "r", encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            entries.append((p[0].strip(), p[1].strip(), p[2].strip() if len(p) > 2 else ""))

    c = Counter(e[0] for e in entries)
    dups = {k: v for k, v in c.items() if v > 1}
    print("root entries: %d   distinct keys: %d" % (len(entries), len(c)))
    print("DUPLICATE keys: %d" % len(dups))
    for k in sorted(dups):
        print("   %-10s %s" % (k, [(e[1], e[2]) for e in entries if e[0] == k]))

    canon = {}
    for k, m, v in entries:
        canon[k] = m

    rows = [l.rstrip("\n").split("\t") for l in io.open(os.path.join(DATA, "final_words.tsv"), "r", encoding="utf-8")]
    rows = [r for r in rows if len(r) >= 7]
    used = Counter(r[4].strip() for r in rows if r[4].strip())
    missing = sorted(k for k in used if k not in canon)
    print("")
    print("roots used by the wordlist: %d" % len(used))
    print("used but NOT canonical: %s" % (missing if missing else "none"))

    print("")
    print("words per duplicated key:")
    for k in sorted(dups):
        ws = [r[0] for r in rows if r[4].strip() == k]
        print("   %-8s (%d): %s" % (k, len(ws), ", ".join(ws)))


if __name__ == "__main__":
    main()
