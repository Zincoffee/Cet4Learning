#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""Second-pass top-up selection over a candidate chunk.

Reads  data/topup/topup_NN.tsv   (word, tier, root, meaning)
Writes data/topupkeep/topup_keep_NN.tsv (word, root, keep, gloss)

Rules
  * exactly KEEP_N words are marked 1, input order is preserved;
  * a root is written only for kept words -- the root already present in the
    candidate file is carried over, otherwise a canonical root is filled in
    from NEW_ROOT when the word genuinely contains one;
  * a gloss is written only for kept words whose candidate gloss was empty;
  * everything else stays blank (dropped words are blank in every column).
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

KEEP = {
    # selected for the final list: high-frequency CET-4 exam/writing words,
    # abstract or confusable meanings, or words carried by a clear root
    "terminal", "theoretical", "thereby", "thrill", "token", "toll", "toss",
    "tournament", "tow", "trademark", "trail", "transit", "transplant",
    "treatment", "treaty", "tremble", "trial", "trigger", "trim", "triumph",
    "trivial", "troop", "tropical", "tumble", "tutor", "undergraduate",
    "underline", "union", "upright", "urgent", "utmost", "utter", "validate",
    "vapour", "variant", "vast", "velocity", "venture", "verbal", "verse",
    "vessel", "vibrate", "vice", "vigorous", "violence", "virus", "vocal",
    "volcano", "volunteer", "warehouse", "weapon", "wither",
}

# roots newly filled in for kept words that contain a canonical root
NEW_ROOT = {
    "undergraduate": "grad",   # under + grad(走，步) + uate
}

# glosses supplied for kept words whose candidate gloss was empty
NEW_GLOSS = {
    "thrill": "n. 兴奋，激动；vt. 使激动",
    "token": "n. 象征，标志；代币，礼券",
    "toll": "n. 通行费；伤亡人数；v. 鸣钟",
    "toss": "vt. 扔，抛；摇摆",
    "tournament": "n. 锦标赛，联赛",
    "tow": "vt. 拖，拉；n. 拖，牵引",
    "trademark": "n. 商标；标志",
    "transit": "n. 运输，运送；通行",
    "transplant": "vt. 移植；n. 移植的器官",
    "trigger": "vt. 引发，触发；n. 扳机",
    "trim": "vt. 修剪；削减；a. 整齐的",
    "trivial": "a. 琐碎的，不重要的",
    "troop": "n. 军队；一群，大量",
    "tumble": "vi. 跌倒，滚落；暴跌",
    "tutor": "n. 导师，家庭教师；v. 辅导",
    "validate": "vt. 证实；使生效",
    "vapour": "n. 蒸汽，水汽",
    "variant": "n. 变体，变种；a. 不同的",
    "verbal": "a. 言语的，口头的；动词的",
    "verse": "n. 诗，诗节；韵文",
    "vibrate": "vt.&vi. 振动，颤动",
    "virus": "n. 病毒",
    "vocal": "a. 嗓音的，发声的；直言的",
    "volcano": "n. 火山",
    "weapon": "n. 武器，兵器",
    "wither": "vi. 枯萎，凋谢；衰弱",
}


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
    name = sys.argv[1] if len(sys.argv) > 1 else "02"
    src_path = os.path.join(DATA, "topup", "topup_%s.tsv" % name)
    dst_dir = os.path.join(DATA, "topupkeep")
    dst_path = os.path.join(dst_dir, "topup_keep_%s.tsv" % name)

    rows = read_rows(src_path, 4)
    out = []
    kept = 0
    roots_filled = 0
    glosses_filled = 0
    unknown = []
    for r in rows:
        word, _tier, root, gloss = r[0], r[1], r[2], r[3]
        key = word.strip().lower()
        sel = key in KEEP
        if sel:
            kept += 1
            new_root = root
            if not new_root and key in NEW_ROOT:
                new_root = NEW_ROOT[key]
                roots_filled += 1
            new_gloss = ""
            if not gloss:
                new_gloss = NEW_GLOSS.get(key, "")
                if not new_gloss:
                    unknown.append(word)
                else:
                    glosses_filled += 1
            out.append([word, new_root, "1", new_gloss])
        else:
            out.append([word, "", "0", ""])

    os.makedirs(dst_dir, exist_ok=True)
    with io.open(dst_path, "w", encoding="utf-8", newline="\n") as fh:
        for r in out:
            fh.write("\t".join(r) + "\n")

    print("rows=%d kept=%d roots filled=%d glosses filled=%d"
          % (len(out), kept, roots_filled, glosses_filled))
    if unknown:
        print("  kept words with empty gloss but no new gloss: %s" % unknown)
    missing = KEEP - set(w[0].strip().lower() for w in out)
    if missing:
        print("  WARNING: selected words not found in the chunk: %s" % sorted(missing))
    print("wrote %s" % dst_path)


if __name__ == "__main__":
    main()
