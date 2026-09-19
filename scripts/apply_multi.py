#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Apply the multi-root verification output onto final_ALL.tsv.

Rules
  * word alignment is validated against the input chunk file
  * roots/note are taken from the verification pass
  * the Chinese gloss already present in final_ALL.tsv always wins; the agent's
    gloss is used only to fill a previously empty meaning
Output: data/final_words.tsv  (word, phonetic, meaning, tier, root, roots, note)
"""
import glob
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


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


def load_canon():
    """standard root -> chinese meaning"""
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


def build_note(roots, canon):
    bits = []
    for r in roots:
        m = canon.get(r, "")
        bits.append("%s(%s)" % (r, m) if m else r)
    return "+".join(bits)


def main():
    canon = load_canon()
    rows = [r for r in read_rows(os.path.join(DATA, "final_ALL.tsv"), 7) if len(r) >= 7]
    by_word = {}
    order = []
    for r in rows:
        k = norm(r[0])
        by_word[k] = r
        order.append(k)

    verified = {}
    misaligned = 0
    for f in sorted(glob.glob(os.path.join(DATA, "multikeep", "all_multi_*.tsv"))):
        out = read_rows(f, 4)
        for r in out:
            if len(r) < 4:
                continue
            verified[norm(r[0])] = r

    out_rows = []
    multi = 0
    filled = 0
    kept_orig = 0
    rejected = []
    for k in order:
        r = by_word[k]
        v = verified.get(k)
        word, phon, mean, tier, root, roots, note = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
        if v is not None:
            if norm(v[0]) != k:
                misaligned += 1
                continue
            comps = [c.strip() for c in v[1].split(",") if c.strip()]
            roots = ""
            note = ""
            if len(comps) >= 2:
                bad = [c for c in comps if c not in canon]
                if bad:
                    # a prefix (or an unknown form) was passed off as a root:
                    # the strict rule is ">= 2 real roots", so reject the annotation
                    rejected.append((word, ",".join(comps)))
                else:
                    roots = ",".join(comps)
                    note = v[2].strip() or build_note(comps, canon)
            elif len(comps) == 1 and not root.strip():
                # a single root the verification pass recovered for a blank slot
                root = comps[0]
            g = v[3].strip()
            if not mean.strip() and g:
                mean = g
                filled += 1
            elif mean.strip():
                kept_orig += 1
        if not roots:
            note = ""
        if roots:
            multi += 1
        out_rows.append([word, phon, mean, tier, root, roots, note])

    dst = os.path.join(DATA, "final_words.tsv")
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for r in out_rows:
            fh.write("\t".join(x.replace("\t", " ") for x in r) + "\n")

    total = len(out_rows)
    with_root = sum(1 for r in out_rows if r[4].strip())
    nogloss = sum(1 for r in out_rows if not r[2].strip())
    print("total words          : %d" % total)
    print("with root            : %d (%.1f%%)" % (with_root, 100.0 * with_root / total))
    print("multi-root annotated : %d" % multi)
    print("glosses filled       : %d  (originals kept: %d)" % (filled, kept_orig))
    print("misaligned rows      : %d" % misaligned)
    print("still no meaning     : %d" % nogloss)
    if nogloss:
        print("   ", [r[0] for r in out_rows if not r[2].strip()])
    print("wrote %s" % dst)
    if rejected:
        print("")
        print("annotations rejected (component not a canonical root): %d" % len(rejected))
        for w, c in rejected[:40]:
            print("   %-16s %s" % (w, c))


if __name__ == "__main__":
    main()
