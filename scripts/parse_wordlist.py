#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Parse mahavivo/english-wordlists style CET word lists into TSV.

Entry format handled:
    word [phonetic] pos.中文释义
    word pos.中文释义
    a.m (缩)上午，午前
    p.m (缩)上午，午前
Section headers are single uppercase letters (A, B, ... Z) or the title lines.

Output TSV columns: word <TAB> phonetic <TAB> meaning
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# word token: letters, apostrophes, dots (a.m, B.C.), hyphens
WORD_RE = re.compile(r"^([A-Za-z][A-Za-z'\u2019]*(?:[.\-][A-Za-z]+)*)")
PHON_RE = re.compile(r"^\[([^\]]*)\]\s*")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
NOTICE_RE = re.compile(r"^(Fetched |External web content|\(Content truncated|\(Omitted )")

# a "meaning" must contain a CJK char or a part-of-speech tag
POS_RE = re.compile(
    r"^(art|prep|pron|conj|ad|adv|a|adj|n|v|vi|vt|aux|num|int|u|c)\.(?![a-z])"
)


def parse_line(line):
    """Return (word, phonetic, meaning) or None."""
    s = line.strip()
    if not s:
        return None
    if NOTICE_RE.match(s):
        return None
    if len(s) == 1 and s.isalpha() and s.isupper():
        return None  # section header
    if s.startswith("大学英语四级") or s.startswith("(共"):
        return None
    if s.startswith("Fetched") or "External web content" in s:
        return None

    m = WORD_RE.match(s)
    if not m:
        return None
    word = m.group(1)
    rest = s[m.end():].lstrip()

    phon = ""
    pm = PHON_RE.match(rest)
    if pm:
        phon = pm.group(1).strip()
        rest = rest[pm.end():].lstrip()

    meaning = rest.strip()
    if not meaning:
        return None
    # keep only entries that look like a real dictionary gloss
    if not CJK_RE.search(meaning) and not POS_RE.match(meaning):
        return None
    return word, phon, meaning


def parse_file(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    entries = []
    for line in raw.splitlines():
        got = parse_line(line)
        if got:
            entries.append(got)
    return entries


def dedupe(entries):
    seen = {}
    order = []
    for w, p, m in entries:
        key = w.lower()
        if key in seen:
            # keep the longer gloss / one that has a phonetic
            old = seen[key]
            if (len(p) > len(old[1])) or (len(m) > len(old[2]) and not old[1]):
                seen[key] = (w, p, m)
            continue
        seen[key] = (w, p, m)
        order.append(key)
    return [seen[k] for k in order]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "cet4_AS_raw.txt")
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data", "cet4_AS.tsv")
    entries = dedupe(parse_file(src))
    with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for w, p, m in entries:
            fh.write("%s\t%s\t%s\n" % (w, p, m.replace("\t", " ")))
    print("parsed %d entries -> %s" % (len(entries), dst))
    letters = {}
    for w, _, _ in entries:
        letters[w[0].upper()] = letters.get(w[0].upper(), 0) + 1
    print("per-letter:", " ".join("%s=%d" % (k, letters[k]) for k in sorted(letters)))


if __name__ == "__main__":
    main()
