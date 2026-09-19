#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Fill missing 音标 from the verbatim raw sources in data/_raw/.

Sources
  dancidejianfa4_raw.txt / gaokao_hepin_raw.txt / gaozhongluan_raw.txt
      qwerty-learner JSON, field "name" + "usphone"
  zhongkao_raw.txt      `word [phonetic] pos. 释义`
  cuttlin_TZ.tsv        `word <TAB> phonetic <TAB> meaning`   (Kingsoft IPA)

Rewrites data/final_words.tsv in place; reports how many were filled.
"""
import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "_raw")


def norm(w):
    return w.replace("\ufeff", "").strip().lower().replace("\u2019", "'")


def clean_phon(p):
    p = p.strip()
    if not p:
        return ""
    p = p.replace("\u2018", "\u02c8").replace("\u2019", "\u02cc")
    p = p.replace("\u039b", "\u028c").replace(":", "\u02d0")
    p = p.replace("[", "").replace("]", "").strip()
    if p.startswith("/") and p.endswith("/"):
        p = p[1:-1]
    return p


def load():
    phon = {}

    # 1) qwerty-learner JSON dumps
    pair = re.compile(r'"name"\s*:\s*"([^"]{1,40})"[\s\S]{0,300}?"usphone"\s*:\s*"([^"]{0,60})"')
    for name in ("dancidejianfa4_raw.txt", "gaokao_hepin_raw.txt", "gaozhongluan_raw.txt"):
        p = os.path.join(RAW, name)
        if not os.path.exists(p):
            continue
        txt = io.open(p, "r", encoding="utf-8", errors="replace").read()
        n = 0
        for m in pair.finditer(txt):
            w = norm(m.group(1))
            ph = clean_phon(m.group(2))
            if w and ph and w not in phon:
                phon[w] = ph
                n += 1
        print("  %-26s +%d" % (name, n))

    # 2) 中考 word list:  word [phonetic] ...
    p = os.path.join(RAW, "zhongkao_raw.txt")
    if os.path.exists(p):
        txt = io.open(p, "r", encoding="utf-8", errors="replace").read()
        rx = re.compile(r"^([A-Za-z][A-Za-z'\- ]*?)\s*\[([^\]]+)\]", re.M)
        n = 0
        for m in rx.finditer(txt):
            w = norm(m.group(1))
            ph = clean_phon(m.group(2))
            if w and ph and w not in phon:
                phon[w] = ph
                n += 1
        print("  %-26s +%d" % ("zhongkao_raw.txt", n))

    # 3) cuttlin per-letter tables  (word <TAB> phonetic <TAB> meaning)
    for p in sorted(glob.glob(os.path.join(RAW, "cuttlin_*.tsv"))):
        n = 0
        for line in io.open(p, "r", encoding="utf-8", errors="replace"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                w = norm(parts[0])
                ph = clean_phon(parts[1])
                if w and ph and w not in phon:
                    phon[w] = ph
                    n += 1
        print("  %-26s +%d" % (os.path.basename(p), n))

    return phon


def main():
    phon = load()
    print("phonetic entries available: %d" % len(phon))

    path = os.path.join(DATA, "final_words.tsv")
    rows = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 7:
                rows.append(p)

    filled = 0
    still = []
    for r in rows:
        if not r[1].strip():
            ph = phon.get(norm(r[0]), "")
            if ph:
                r[1] = ph
                filled += 1
            else:
                still.append(r[0])

    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write("\t".join(x.replace("\t", " ") for x in r) + "\n")

    print("phonetics filled: %d" % filled)
    print("still missing   : %d" % len(still))
    if still:
        print("  ", ", ".join(still[:60]))


if __name__ == "__main__":
    main()
