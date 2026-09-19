#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Assemble the final combined wordlist.

Sources
  data/final_AS.tsv          word, phonetic, meaning, tier, root, roots, note
  data/newkeep/new_keep_*.tsv word, tier, root, keep, gloss
  data/cet4_new.tsv          word, phonetic, meaning   (source of phonetic/meaning)

Output
  data/final_ALL.tsv         word, phonetic, meaning, tier, root, roots, note
"""
import glob
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def norm(w):
    return w.replace("\ufeff", "").strip().lower()


TIER_MAP = {"1": "1", "t1": "1", "2": "2", "t2": "2", "3": "3", "t3": "3"}


def norm_tier(v):
    return TIER_MAP.get(v.strip().lower(), "2")


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
    as_rows = [r for r in read_rows(os.path.join(DATA, "final_AS.tsv"), 7) if len(r) >= 7]

    src_new = {}
    order_new = []
    for r in read_rows(os.path.join(DATA, "cet4_new.tsv"), 3):
        k = norm(r[0])
        if k not in src_new:
            src_new[k] = r
            order_new.append(k)

    decisions = {}
    problems = 0
    for f in sorted(glob.glob(os.path.join(DATA, "newkeep", "new_keep_*.tsv"))):
        for r in read_rows(f, 5):
            if len(r) < 4:
                problems += 1
                continue
            decisions[norm(r[0])] = r

    new_out = []
    kept = dropped = nogloss = 0
    for k in order_new:
        s = src_new[k]
        d = decisions.get(k)
        if d is None:
            dropped += 1
            continue
        root = d[2].strip()
        keep = d[3].strip()
        gloss = (d[4] if len(d) > 4 else "").strip()
        if keep != "1":
            dropped += 1
            continue
        kept += 1
        meaning = s[2].strip() or gloss
        if not meaning:
            nogloss += 1
        new_out.append([s[0], s[1].strip(), meaning, norm_tier(d[1]), root, "", ""])

    print("A-S final rows        : %d" % len(as_rows))
    print("new block: kept       : %d (dropped %d, no-decision %d, bad rows %d)"
          % (kept, dropped, len(order_new) - len(decisions), problems))
    print("new block: still no meaning : %d" % nogloss)

    merged = {}
    prior = []
    for r in as_rows + new_out:
        k = norm(r[0])
        if k in merged:
            continue
        merged[k] = r
        prior.append(k)

    # ---- top-up: words added back by the second selection pass -------------
    topdec = {}
    for f in sorted(glob.glob(os.path.join(DATA, "topupkeep", "topup_keep_*.tsv"))):
        for r in read_rows(f, 4):
            if len(r) >= 3:
                topdec[norm(r[0])] = r

    added = 0
    for f in sorted(glob.glob(os.path.join(DATA, "topup", "topup_*.tsv"))):
        for r in read_rows(f, 4):
            k = norm(r[0])
            d = topdec.get(k)
            if d is None or d[2].strip() != "1" or k in merged:
                continue
            root = d[1].strip() or (r[2].strip() if len(r) > 2 else "")
            gloss = (d[3] if len(d) > 3 else "").strip()
            meaning = (r[3].strip() if len(r) > 3 else "") or gloss
            tier = norm_tier(r[1]) if len(r) > 1 else "2"
            merged[k] = [r[0], "", meaning, tier, root, "", ""]
            prior.append(k)
            added += 1
    print("top-up words added    : %d" % added)

    out = [merged[k] for k in prior]
    out.sort(key=lambda r: norm(r[0]))

    total = len(out)
    with_root = sum(1 for r in out if r[4].strip())
    multi = sum(1 for r in out if r[5].strip())
    nogloss = sum(1 for r in out if not r[2].strip())
    print("")
    print("TOTAL WORDS           : %d" % total)
    print("  with root           : %d (%.1f%%)" % (with_root, 100.0 * with_root / total))
    print("  multi-root (annot.) : %d" % multi)
    print("  without meaning     : %d" % nogloss)
    tb = {}
    for r in out:
        tb[r[3]] = tb.get(r[3], 0) + 1
    print("  tier breakdown      : %s" % tb)

    dst = os.path.join(DATA, "final_ALL.tsv")
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for r in out:
            fh.write("\t".join(x.replace("\t", " ") for x in r) + "\n")
    print("wrote %s" % dst)


if __name__ == "__main__":
    main()
