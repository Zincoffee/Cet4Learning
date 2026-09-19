#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Analysis: how many 'core' words are transparent derivatives of another
list word? Used to decide the trimming policy for the ~2000-word target.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

SUFFIXES = [
    ("ly", ""), ("ness", ""), ("ment", ""), ("ments", ""),
    ("tion", "e"), ("tion", ""), ("sion", "d"), ("sion", "de"), ("ation", "e"), ("ation", ""),
    ("er", "e"), ("er", ""), ("or", "e"), ("or", ""), ("ist", ""), ("ism", ""),
    ("ful", ""), ("less", ""), ("able", "e"), ("able", ""), ("ible", "t"), ("ible", ""),
    ("ing", "e"), ("ing", ""), ("ed", "e"), ("ed", ""),
    ("al", "e"), ("al", ""), ("ial", ""), ("ual", ""),
    ("ity", "e"), ("ity", ""), ("ety", ""),
    ("ance", "e"), ("ance", ""), ("ence", "e"), ("ence", ""),
    ("ant", "e"), ("ant", ""), ("ent", "e"), ("ent", ""),
    ("ive", "e"), ("ive", ""), ("ous", "e"), ("ous", ""), ("ious", ""),
    ("ize", "e"), ("ize", ""), ("ise", "e"), ("ise", ""),
    ("y", ""),
    ("th", ""),
    ("ic", "e"), ("ic", ""), ("ical", "e"), ("ical", ""),
    ("ish", ""), ("en", ""), ("en", "e"),
]


def norm(w):
    return w.replace("\ufeff", "").strip().lower()


def bases(w):
    out = set()
    for suf, add in SUFFIXES:
        if w.endswith(suf) and len(w) > len(suf) + 2:
            stem = w[: len(w) - len(suf)]
            out.add(stem + add if add else stem)
    # multi-suffix stripping (e.g. -fully -> -ful -> "")
    for b in list(out):
        for suf, add in SUFFIXES:
            if b.endswith(suf) and len(b) > len(suf) + 2:
                stem = b[: len(b) - len(suf)]
                out.add(stem + add if add else stem)
    out.discard(w)
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, "tagged_AS.tsv")
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            rows.append(p)

    allwords = set(norm(r[0]) for r in rows)
    stats = {}

    for r in rows:
        w, tier = norm(r[0]), r[3]
        if tier == "3":
            continue
        bs = [b for b in bases(w) if b in allwords]
        if bs:
            stats[w] = (tier, bs[0])

    print("total rows: %d" % len(rows))
    for t in ("1", "2"):
        n = sum(1 for r in rows if r[3] == t)
        d = sum(1 for w, (tt, b) in stats.items() if tt == t)
        print("tier%s: %d  (derivative of another list word: %d)" % (t, n, d))

    core = [r for r in rows if r[3] in ("1", "2")]
    keep_if_tier1_only = [r for r in core if r[3] == "1" or norm(r[0]) not in stats]
    print("core=%d  ; core minus ALL derivatives = %d" % (len(core), len(keep_if_tier1_only)))

    print("\nsample tier2 derivatives:")
    shown = 0
    for r in core:
        w = norm(r[0])
        if r[3] == "2" and w in stats:
            print("   %-18s <- %s" % (r[0], stats[w][1]))
            shown += 1
            if shown >= 40:
                break


if __name__ == "__main__":
    main()
