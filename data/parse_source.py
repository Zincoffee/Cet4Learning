#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_source.py -- build CET-4 (大学英语四级大纲词汇表) tab-separated sources.

Why this script exists
----------------------
Direct network access from the shell is blocked in this environment, so every
upstream file was retrieved with the harness `web_fetch` tool and dropped into
`data/` (the already-published A-S extract) or `data/_raw/` (everything else).
This script turns those raw downloads into two tidy, deduplicated TSVs.

Outputs (UTF-8, no BOM, LF line endings):
  data/cet4_TZ_source.tsv     word <TAB> phonetic <TAB> meaning   (letters T-Z)
  data/cet4_full_source.tsv   word <TAB> phonetic <TAB> meaning   (letters A-Z)

Inputs
------
  data/cet4_AS.tsv                  A-S words with phonetic + Chinese gloss
                                    (mahavivo/english-wordlists CET4_edited.txt)
  data/_raw/cuttlin_TZ.tsv          T-Z words with phonetic + Chinese gloss
                                    (cuttlin/Vocabulary-of-CET-4 JSON/{T..Z}.json)
  data/_raw/zhongkao_raw.txt        mahavivo 中考英语词汇表.txt  "word [phonetic] meaning"
                                    (fills in BASIC T-Z headwords)
  data/_raw/cet4_wordlist_bare.txt  JavaProgrammerLB/cet-word-list word-list.txt
                                    (bare CET-4 A-Z list; defines T-Z membership)
  data/_raw/cet46_wordlist_bare.txt mahavivo CET_4+6_edited.txt
                                    (bare CET-4/6 list; cross-check only)

Run:  py -3 data/parse_source.py
"""

import json
import os
import re
import sys
from collections import OrderedDict

DATA = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(DATA, "_raw")

OUT_TZ = os.path.join(DATA, "cet4_TZ_source.tsv")
OUT_FULL = os.path.join(DATA, "cet4_full_source.tsv")
OUT_GAPS = os.path.join(DATA, "cet4_missing_gloss.tsv")

TZ_LETTERS = set("tuvwxyz")

# --------------------------------------------------------------------------
# normalisation helpers
# --------------------------------------------------------------------------

# Kingsoft-Phonetic-font leftovers in the Chinese sources + the ASCII length
# mark, mapped to real IPA so every source looks the same.
PHON_FIX = (
    ("\u2018", "\u02c8"),   # left single quote  -> primary stress
    ("\u2019", "\u02cc"),   # right single quote -> secondary stress
    ("\u039b", "\u028c"),   # capital Lambda     -> open-mid back unrounded
    (":", "\u02d0"),        # ASCII colon        -> IPA length mark
)

SKIP_PREFIX = ("Fetched ", "External web content")


def norm_phon(p):
    """Strip dictionary markup from a phonetic field, return plain IPA."""
    if not p:
        return ""
    p = p.strip().strip("[]/").strip()
    for a, b in PHON_FIX:
        p = p.replace(a, b)
    p = p.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", p).strip("[]/ ")


def norm_meaning(m):
    """Collapse the padding whitespace used by the source files."""
    if not m:
        return ""
    m = m.replace("\u3000", " ").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", m).strip()


def norm_word(w):
    return w.strip().strip("\ufeff")


def skip_line(line):
    s = line.strip()
    return (not s) or s.startswith(SKIP_PREFIX) or bool(re.match(r"^[A-Z]$", s))


# --------------------------------------------------------------------------
# loaders
# --------------------------------------------------------------------------

def load_tsv(path):
    """Read `word <TAB> phonetic <TAB> meaning` rows."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if skip_line(line):
                continue
            cols = line.rstrip("\n").rstrip("\r").split("\t")
            if len(cols) < 2:
                continue
            word = norm_word(cols[0])
            if not re.match(r"^[A-Za-z]", word):
                continue
            rows.append((word,
                         norm_phon(cols[1]),
                         norm_meaning(cols[2]) if len(cols) > 2 else ""))
    return rows


BRACKET_RE = re.compile(r"^\[([^\]]*)\]")
SLASH_RE = re.compile(r"^/([^/]*)/")
WORD_RE = re.compile(r"^([A-Za-z][A-Za-z'\u2019\-]*)")


def load_inline(path):
    """Read `word [phonetic] meaning` / `word /phonetic/ meaning` lines."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if skip_line(line):
                continue
            line = line.strip().strip("\ufeff")
            m = WORD_RE.match(line)
            if not m:
                continue
            word = norm_word(m.group(1))
            rest = line[m.end():].strip()
            rest = re.sub(r"^\([^)]*\)\s*", "", rest)   # drop a leading "(an)"
            phon = ""
            mb = BRACKET_RE.match(rest)
            if mb:
                phon = norm_phon(mb.group(1))
                rest = rest[mb.end():]
            else:
                ms = SLASH_RE.match(rest)
                if ms:
                    phon = norm_phon(ms.group(1))
                    rest = rest[ms.end():]
            rows.append((word, phon, norm_meaning(rest.lstrip(".,;: ").strip())))
    return rows


# qwerty-learner style dictionary entry:
#   {"name": "...", "trans": ["...", "..."], "usphone": "...", "ukphone": "..."}
QLEARN_OBJ_RE = re.compile(
    r'\{\s*"name"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"trans"\s*:\s*\[(.*?)\]\s*'
    r'(?:,\s*"usphone"\s*:\s*"((?:[^"\\]|\\.)*)")?', re.S)
QLEARN_STR_RE = re.compile(r'"((?:[^"\\]|\\.)*)"', re.S)
# "找不到解释" = upstream placeholder; "(Earn)人名；(泰)炎" = name gloss, not a word sense
QLEARN_JUNK_RE = re.compile(r"\u627e\u4e0d\u5230\u89e3\u91ca|\u4eba\u540d")
MEAN_MAX = 160


def load_qwerty_json(path):
    """Tolerant reader for qwerty-learner dictionaries.

    The upstream file is far larger than one web_fetch can return, so the copy
    on disk stops in the middle of an object -- hence a regex scan instead of
    json.loads().  The dictionary is ordered by importance rather than
    alphabetically, so the part that did arrive still spans every letter.
    """
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    rows = []
    for m in QLEARN_OBJ_RE.finditer(text):
        try:
            word = json.loads('"' + m.group(1) + '"')
        except ValueError:
            continue
        phon = ""
        if m.group(3):
            try:
                phon = json.loads('"' + m.group(3) + '"').split(",")[0]
            except ValueError:
                phon = ""
        parts = []
        for sm in QLEARN_STR_RE.finditer(m.group(2)):
            try:
                s = json.loads('"' + sm.group(1) + '"').strip()
            except ValueError:
                continue
            if s and not QLEARN_JUNK_RE.search(s) and s not in parts:
                parts.append(s)
        gloss = "\uff1b".join(parts)
        if len(gloss) > MEAN_MAX:
            gloss = gloss[:MEAN_MAX].rstrip("\uff1b") + "\u2026"
        rows.append((word, norm_phon(phon.replace("'", "\u02c8")),
                     norm_meaning(gloss)))
    return rows


def tokenize_bare(path):
    """Split a bare word list into headword tokens.

    The upstream lists wrap several headwords onto one physical line
    ("theoretical therapy") and mark homographs with a suffix
    ("bound'", "bound2", "bound\u00b3", "contentl").  Splitting on
    whitespace and slashes, then stripping those markers, recovers the
    intended headwords.
    """
    raw = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if skip_line(line):
                continue
            for tok in re.split(r"[\s/]+", line.strip().strip("\ufeff")):
                if tok:
                    raw.append(tok)
    rawset = set(raw)

    words = []          # (display_word, key)
    for tok in raw:
        t = re.sub(r"\([^)]*\)", "", tok)                  # stor(e)y -> story
        t = t.strip().strip("[]")
        t = re.sub(r"[\d'\u2019!?*.\u00b9\u00b2\u00b3\u0142]+$", "", t)
        t = t.strip("'\"!?*-")
        if not t or not re.match(r"^[A-Za-z][A-Za-z'\u2019\-]*$", t):
            continue
        # "contentl"/"tearl"/"stilll" are homograph markers of "content2" etc.
        if t.endswith("l") and len(t) > 2:
            stem = t[:-1]
            if any(stem + suf in rawset for suf in ("2", "'", "3", "\u00b3", "1")):
                continue
        words.append((t, t.lower()))
    return words


# --------------------------------------------------------------------------
# merge machinery
# --------------------------------------------------------------------------

def add(store, word, phon, mean):
    """Accumulate phonetic/meaning for a headword (case-insensitive key)."""
    ent = store.setdefault(word.lower(), {"word": word, "phon": "", "mean": []})
    if phon and not ent["phon"]:
        ent["phon"] = phon
    if mean and mean not in ent["mean"]:
        ent["mean"].append(mean)
    return ent


def rows_out(store):
    return [(store[k]["word"], store[k]["phon"], "\uff1b".join(store[k]["mean"]))
            for k in sorted(store)]


# --------------------------------------------------------------------------

def main():
    as_rows = load_tsv(os.path.join(DATA, "cet4_AS.tsv"))
    tz_cuttlin = load_tsv(os.path.join(RAW, "cuttlin_TZ.tsv"))
    zhongkao = load_inline(os.path.join(RAW, "zhongkao_raw.txt"))
    dcdjf = load_qwerty_json(os.path.join(RAW, "dancidejianfa4_raw.txt"))
    gzluan = load_qwerty_json(os.path.join(RAW, "gaozhongluan_raw.txt"))
    gkpin = load_qwerty_json(os.path.join(RAW, "gaokao_hepin_raw.txt"))
    bare = tokenize_bare(os.path.join(RAW, "cet4_wordlist_bare.txt"))
    bare46 = tokenize_bare(os.path.join(RAW, "cet46_wordlist_bare.txt"))

    # T-Z membership comes from the bare CET-4 syllabus list (4615-word list).
    # The CET-4/6 list is only used as a coverage cross-check, because it also
    # carries the ~2200 additional CET-6 headwords.
    # The A-S extraction from CET4_edited.txt was cut off by the fetch size
    # limit at the headword "sew", so the tail of the alphabet is everything
    # from "sh..." onwards plus T-Z.  That whole tail is rebuilt here.
    def in_missing_tail(key):
        return key[:1] in TZ_LETTERS or (key[:1] == "s" and key > "sew")

    cet4_keys = {k for _, k in bare}
    cet46_keys = {k for _, k in bare46}
    seen = set()
    bare_tail = []
    for w, k in bare:
        if in_missing_tail(k) and k not in seen:
            seen.add(k)
            bare_tail.append((w, k))
    bare_tz = [(w, k) for w, k in bare_tail if k[:1] in TZ_LETTERS]

    zhongkao_map = {}
    for w, p, m in zhongkao:
        if p or m:
            zhongkao_map.setdefault(w.lower(), (w, p, m))
    dcdjf_map = {}
    for w, p, m in dcdjf:
        if p or m:
            dcdjf_map.setdefault(w.lower(), (w, p, m))
    gzluan_map = {}
    for w, p, m in gzluan:
        if p or m:
            gzluan_map.setdefault(w.lower(), (w, p, m))
    gkpin_map = {}
    for w, p, m in gkpin:
        if p or m:
            gkpin_map.setdefault(w.lower(), (w, p, m))

    # ---- letters T-Z ------------------------------------------------------
    tz = OrderedDict()
    # 1) cuttlin/Vocabulary-of-CET-4 -- a real CET-4 word book, one file/letter
    for w, p, m in tz_cuttlin:
        add(tz, w, p, m)
    cuttlin_keys = {w.lower() for w, _, _ in tz_cuttlin}
    # 2) every T-Z headword of the bare CET-4 syllabus list (coverage floor)
    for w, k in bare_tail:
        add(tz, w, "", "")
    # 3) TOP-UP from the Chinese basic-vocabulary lists (中考英语词汇表 first,
    #    then the 单词的减法四级 wordbook), only for words already in T-Z.
    filled = 0
    for source in (zhongkao_map, gzluan_map, gkpin_map, dcdjf_map):
        for key in list(tz):
            ent = tz[key]
            if ent["phon"] and ent["mean"]:
                continue
            got = source.get(key)
            if got is None:
                continue
            w, p, m = got
            if add(tz, ent["word"], "" if ent["phon"] else p,
                   "" if ent["mean"] else m) and (p or m):
                filled += 1

    tail_rows = rows_out(tz)
    tz_rows = [r for r in tail_rows if r[0][:1].lower() in TZ_LETTERS]
    with open(OUT_TZ, "w", encoding="utf-8", newline="\n") as fh:
        for w, p, m in tz_rows:
            fh.write("%s\t%s\t%s\n" % (w, p, m))

    # ---- letters A-Z ------------------------------------------------------
    full = OrderedDict()
    for w, p, m in as_rows:
        add(full, w, p, m)
    for w, p, m in tail_rows:
        add(full, w, p, m)
    full_rows = rows_out(full)
    with open(OUT_FULL, "w", encoding="utf-8", newline="\n") as fh:
        for w, p, m in full_rows:
            fh.write("%s\t%s\t%s\n" % (w, p, m))

    # ---- machine-readable inventory of every row whose meaning is empty ----
    with open(OUT_GAPS, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("word\tletter\tblock\thas_phonetic\n")
        for w, p, m in full_rows:
            if m:
                continue
            block = "T-Z" if w[:1].lower() in TZ_LETTERS else "S-tail"
            fh.write("%s\t%s\t%s\t%s\n"
                     % (w, w[:1].lower(), block, "yes" if p else "no"))

    # ---- report -----------------------------------------------------------
    def stats(rows, label):
        per, with_mean = {}, 0
        for w, p, m in rows:
            per[w[:1].lower()] = per.get(w[:1].lower(), 0) + 1
            with_mean += bool(m)
        print("%s: %d headwords, %d with a Chinese gloss" % (label, len(rows), with_mean))
        print("   per-letter: " + "  ".join("%s=%d" % (c, per.get(c, 0)) for c in sorted(per)))
        return per

    print("A-S source rows                  : %d" % len(as_rows))
    print("cuttlin T-Z rows                 : %d" % len(tz_cuttlin))
    print("中考 rows parsed                 : %d" % len(zhongkao))
    print("单词的减法四级 rows parsed       : %d" % len(dcdjf))
    print("高中乱序 rows parsed             : %d" % len(gzluan))
    print("高考真题核心高频 rows parsed     : %d" % len(gkpin))
    print("bare CET-4 headwords             : %d" % len(bare))
    print("bare CET-4/6 headwords           : %d" % len(bare46))
    print("T-Z headwords in bare CET-4 list : %d" % len(bare_tz))
    print("S(headwords after 'sew') repaired: %d" % (len(bare_tail) - len(bare_tz)))
    print("T-Z headwords filled from 中考   : %d" % filled)
    print("T-Z headwords only in cuttlin    : %d"
          % len(cuttlin_keys - cet4_keys))
    print("-" * 66)
    stats(tz_rows, "cet4_TZ_source.tsv")
    stats(full_rows, "cet4_full_source.tsv")
    print("-" * 66)
    no_mean = [w for w, p, m in tz_rows if not m]
    print("T-Z headwords still without a gloss: %d" % len(no_mean))
    if no_mean:
        print("   " + ", ".join(no_mean))
    no_phon = [w for w, p, m in tz_rows if not p]
    print("T-Z headwords without a phonetic: %d" % len(no_phon))
    return 0


if __name__ == "__main__":
    sys.exit(main())
