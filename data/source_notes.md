# CET-4 vocabulary sources — notes

Task: obtain as complete a **大学英语四级（CET-4）大纲词汇表** as possible, with
中文释义 (and 音标 where available), covering the whole alphabet — especially T–Z.

## Environment facts that shaped the result

* The shell has **no network** (`Invoke-WebRequest`, `curl`, `pip`, `git clone` all fail).
  Every upstream file was retrieved with the harness **`web_fetch`** tool.
* `web_fetch` **truncates a single response at ≈100k–155k characters/bytes** and spills the
  (truncated) formatted result to a temp file. Anything larger than that is only partly usable,
  and because most word lists are alphabetically ordered, truncation destroys exactly the
  **tail of the alphabet** that this task needed.
* `py -3` is the interpreter (`python` is not on PATH).
* Reading the spilled files with **Windows PowerShell `Get-Content` shows mojibake**;
  the files themselves are valid UTF-8 — verified with Python. Always read them as UTF-8.

## Sources actually used

| # | URL | size | letters | role |
|---|-----|------|---------|------|
| 1 | `https://raw.githubusercontent.com/mahavivo/english-wordlists/master/CET4_edited.txt` | 198,810 B (only ~150 KB retrievable) | A–S, **cut off mid-S at `sew`** | authoritative CET-4 syllabus glosses, A–S |
| 2 | `https://raw.githubusercontent.com/cuttlin/Vocabulary-of-CET-4/HEAD/JSON/{T,U,V,W,X,Y,Z}.json` | 15,579 / 5,098 / 5,929 / 6,861 / 134 / 757 / 136 B | T–Z | CET-4 word book, one file per letter — **the T–Z backbone** |
| 3 | `https://cdn.jsdelivr.net/gh/mahavivo/english-wordlists@master/中考英语词汇表.txt` | 86,762 B | A–Z | 音标 + 中文释义 for **basic** words (fills T–Z, and the S gap) |
| 4 | `https://raw.githubusercontent.com/JavaProgrammerLB/cet-word-list/master/word-list.txt` | 65,736 B | A–Z | bare headword list used to decide **which T–Z/S words belong to CET-4** |
| 5 | `https://raw.githubusercontent.com/mahavivo/english-wordlists/master/CET_4%2B6_edited.txt` | 65,877 B | A–Z | bare CET-4/6 list, cross-check only |
| 6 | `https://cdn.jsdelivr.net/gh/RealKai42/qwerty-learner@master/public/dicts/DanCiDeJianFa_4.json` | 455,294 B → 126,334 B retrievable | sample of all letters (importance-ordered) | gloss top-up |
| 7 | `https://cdn.jsdelivr.net/gh/RealKai42/qwerty-learner@master/public/dicts/GaoZhongluan_2_T.json` | 777,383 B → 122,503 B retrievable | shuffled sample, all letters | gloss top-up |
| 8 | `https://cdn.jsdelivr.net/gh/RealKai42/qwerty-learner@master/public/dicts/GaoKaoZhenTiHeXinGaoPin.json` | 188,628 B → 125,611 B retrievable | frequency-ordered sample, all letters | gloss top-up |
| 9 | `https://api.github.com/repos/mahavivo/english-wordlists/git/trees/HEAD?recursive=1`, `.../cuttlin/Vocabulary-of-CET-4/git/trees/HEAD?recursive=1`, `.../KyleBing/english-vocabulary/contents/` (and others) | — | — | file-size reconnaissance |

All retrieved payloads are kept verbatim under `data/_raw/` so the build is reproducible
without network access.

### Sources fetched but rejected

| URL | reason |
|-----|--------|
| `https://raw.githubusercontent.com/RealKai42/qwerty-learner/master/public/dicts/CET4_T.json` (499,501 B) and `.../KyleBing/english-vocabulary/json/3-CET4-顺序.json` (5,303,137 B, same content) | whole-词书 JSON, alphabetical, far over the fetch limit |
| `.../qwerty-learner/public/dicts/Duolingo_Vocabulary_B2.json` (275,489 B) | alphabetical → truncation returned A–H only |
| `.../mahavivo/english-wordlists/台灣高中英文參考詞彙表.txt` (118,329 B) | file is Big5-encoded; decoding as UTF-8 destroyed every Chinese gloss |
| `.../mahavivo/english-wordlists/Highschool_edited.txt` (25,353 B) | bare words, no 音标/释义 |
| `https://github.com/cuttlin/Vocabulary-of-CET-4` `TXT/总表/四级词汇总表.txt` (194,662 B) | alphabetical and over the limit → tail lost |

## Outputs

| file | bytes | rows | rows with 中文释义 |
|------|-------|------|-------------------|
| `data/cet4_TZ_source.tsv` | 25,160 | **863** | **501** |
| `data/cet4_full_source.tsv` | 188,824 | **5,070** | **4,240** |

Format: `word <TAB> phonetic <TAB> meaning`, UTF-8, no BOM, LF, one line per headword
(multiple senses of a homograph are joined with `；`). Empty field = unknown, the tab
is always kept.

### `cet4_TZ_source.tsv` — per letter

| letter | headwords | with 释义 | with 音标 |
|--------|-----------|-----------|-----------|
| T | 392 | 227 | 225 |
| U | 95 | 59 | 59 |
| V | 130 | 60 | 60 |
| W | 207 | 134 | 133 |
| X | 2 | 1 | 1 |
| Y | 26 | 17 | 17 |
| Z | 11 | 3 | 3 |
| **T–Z** | **863** | **501** | **498** |

### `cet4_full_source.tsv` — per letter (total / with 释义)

A 294/294 · B 224/224 · C 429/429 · D 243/243 · E 210/210 · F 218/218 · G 130/130 ·
H 150/150 · I 171/171 · J 35/35 · K 27/27 · L 163/163 · M 216/216 · N 96/96 · O 122/122 ·
P 361/361 · Q 21/21 · R 280/280 · **S 817/349** · T 392/227 · U 95/59 · V 130/60 ·
W 207/134 · X 2/1 · Y 26/17 · Z 11/3

Letters A–R are 100 % glossed because they come from the authoritative CET-4 list.

## Findings, gaps and uncertainty (read this before using the data)

1. **The existing A–S extract was not complete A–S.** `data/cet4_AS_raw.txt` /
   `cet4_AS.tsv` stop in the middle of **S, at the headword `sew`** — everything from
   `sh…` to `sy…` (and on to Z) had been lost to the fetch-size limit.
   This build **repairs that hole**: 690 additional S headwords (S > `sew`) were added,
   349 of them with a 中文释义, using the same membership + gloss sources as T–Z.

2. **There is no single fetchable CET-4 list with 音标 + 中文释义.** The only such file
   (`CET4_edited.txt`, 198,810 B) is ~30 % larger than one `web_fetch` can return, and the
   per-letter CET-4 JSON from `cuttlin/Vocabulary-of-CET-4` is **abridged** (~3,100 headwords:
   it omits basic words such as `table`, `take`, `tea`). T–Z was therefore assembled from
   the per-letter CET-4 files **plus three Chinese gloss wordbooks** used only to fill
   headwords that were already known to be in a CET-4 list.

3. **The T–Z gloss coverage is partial: 501 / 863 (58 %).** The remaining **362 headwords
   carry an empty phonetic and meaning** — they are real CET-4-word-list headwords whose
   gloss could not be obtained. They are mostly higher-level items, e.g.
   `tangible, tariff, tentative, terminate, terrain, testament, texture, therapy, thermal,
   thesis, threshold, thrill, timid, token, topical, topple, tornado, tournament, toxic,
   trademark, trailer, trait, tranquil, transaction, transcend, transcript, transient,
   transit, transition, transplant, trauma, treasury, tribal, tribute, tricky, trigger,
   trivial, trustee, tuition, turbulent, unanimous, underestimate, undermine, underwear,
   unemployment, unfold, unilateral, unprecedented, unveil, upgrade, uphold, uranium,
   urine, utilization, vacancy, vaccinate, vaccine, validity, valve, vanity, vegetarian,
   vegetation, veil, vein, vendor, verdict, verification, versatile, veto, viable,
   vibration, vicinity, vicious, victorious, vigor, violation, virgin, virtual, virtuous,
   virus, visibility, vocational, vogue, void, volatile, voucher, vow, vulgar,
   vulnerability, vulnerable, wardrobe, warfare, warrant, warranty, wary, watchful,
   weariness, weary, whale, whereas, whereby, whirl, wholesale, wholesome, wield,
   wilderness, wittingly…`, plus a few surprisingly basic ones (`title, topic, toss,
   trash, truly, turtle, tutor, ugly, victory, violence, vocabulary, vote, wall, warn,
   wash, wealth, weapon, website, wedding, wide…`).

4. **Letter-level coverage is complete; per-word membership is a CET-4/6 superset.**
   Membership for the repaired region comes from `JavaProgrammerLB/cet-word-list`
   (≈8,009 headwords including spelling variants and derivatives) plus
   `mahavivo CET_4+6` (8,029). Those files are **CET-4/6**, not the strict 4,615-headword
   四级大纲, so the S-tail and T–Z blocks contain **some CET-6-only words** (~10–20 % is a
   reasonable estimate; it could not be measured exactly because no CET-6-only list was
   fetchable). A–R is exact.

5. **音标 style is mixed.** Values coming from the Chinese sources use the Kingsoft-font
   IPA of the originals; `‘`→`ˈ`, `’`→`ˌ`, `Λ`→`ʌ` and `:`→`ː` were normalised, and
   `cuttlin`'s leading BOM was stripped (which also fixed its `tɔilet` typo → `toilet`).
   Glosses filled from `DanCiDeJianFa_4` / `GaoZhongluan_2` / `GaoKaoZhenTiHeXinGaoPin`
   are richer (several senses, truncated at 160 characters) than the terse A–S glosses.

6. **Nothing was invented.** Every row comes from one of the files listed above; every
   empty field means "not found", never a guess.

## Reproducing

```powershell
cd "D:\ds practice\Cet4Learning"
py -3 data\parse_source.py
```

The script reads `data/cet4_AS.tsv` plus the verbatim downloads in `data/_raw/`, and
rewrites `cet4_TZ_source.tsv` and `cet4_full_source.tsv`. It prints the per-letter counts.

No temporary files were left behind; the only extras are the documented source payloads
in `data/_raw/`.
