#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Validate + merge per-chunk TSV annotations against the source wordlist.

Chunk TSV line format:  w <TAB> t <TAB> r <TAB> rs <TAB> n
Source TSV line format: w <TAB> phonetic <TAB> meaning

Output: data/tagged_<PREFIX>.tsv
    word <TAB> phonetic <TAB> meaning <TAB> tier <TAB> root <TAB> roots <TAB> note
"""
import glob
import io
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def norm_word(w):
    w = w.replace("\ufeff", "").strip().lower()
    w = w.replace("\u2019", "'")
    return w


def read_src(prefix):
    path = os.path.join(DATA, "cet4_%s.tsv" % prefix)
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip():
                continue
            parts = line.split("\t")
            while len(parts) < 3:
                parts.append("")
            rows.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
    return rows


def read_chunks(pattern):
    files = sorted(glob.glob(os.path.join(DATA, "chunks", pattern)))
    recs = []
    problems = []
    for f in files:
        base = os.path.basename(f)
        with io.open(f, "r", encoding="utf-8") as fh:
            n = 0
            for lineno, line in enumerate(fh, 1):
                raw = line.rstrip("\n").rstrip("\r")
                if not raw.strip():
                    continue
                if raw.strip().startswith("#"):
                    continue
                if raw.startswith("```"):
                    continue
                parts = raw.split("\t")
                if len(parts) < 5:
                    # try to salvage: allow fewer fields
                    if len(parts) == 4:
                        parts.append("")
                    else:
                        problems.append("%s:%d bad field count %d" % (base, lineno, len(parts)))
                        continue
                w, t, r, rs, note = (p.strip() for p in parts[:5])
                recs.append((base, w, t, r, rs, note))
                n += 1
        print("  %s -> %d records" % (base, n))
    return recs, problems


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "AS"
    src = read_src(prefix)
    print("source %s: %d words" % (prefix, len(src)))

    chunks, problems = read_chunks("%s_*.tsv" % prefix.lower())
    print("chunks total: %d records" % len(chunks))
    for p in problems[:20]:
        print("  PROBLEM:", p)

    if len(chunks) != len(src):
        print("!! COUNT MISMATCH: source=%d chunks=%d" % (len(src), len(chunks)))

    # alignment check
    mismatches = []
    for i in range(min(len(src), len(chunks))):
        sw = norm_word(src[i][0])
        cw = norm_word(chunks[i][1])
        if sw != cw:
            mismatches.append((i + 1, src[i][0], chunks[i][1], chunks[i][0]))
    print("mismatches: %d" % len(mismatches))
    for m in mismatches[:25]:
        print("   line %d src=%r chunk=%r (%s)" % m)

    # write merged
    out = os.path.join(DATA, "tagged_%s.tsv" % prefix)
    tier_counts = {1: 0, 2: 0, 3: 0, "?": 0}
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        for i, (w, phon, mean) in enumerate(src):
            if i < len(chunks):
                _, cw, t, r, rs, note = chunks[i]
                if norm_word(cw) != norm_word(w):
                    # fall back to source word; keep annotation only if clearly same
                    t, r, rs, note = "3", "", "", ""
            else:
                t, r, rs, note = "3", "", "", ""
            if t not in ("1", "2", "3"):
                tier_counts["?"] += 1
                t = "2"
            else:
                tier_counts[int(t)] += 1
            fh.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (w, phon, mean, t, r, rs, note))
    print("wrote %s" % out)
    print("tiers:", tier_counts)
    print("core (tier1+2) = %d" % (tier_counts[1] + tier_counts[2]))


if __name__ == "__main__":
    main()
