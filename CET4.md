# 四级核心 2000 词 · 词根分类表

**成品：`out/CET4核心2000词_词根分类.xlsx`**（3 个工作表：词根分类词汇表 / 词根索引 / 说明）

## 成品内容

| 项目 | 数值 |
|---|---|
| 收录单词 | **1998** 词 |
| 含词根 | 1151 词，归入 **260** 个词根 |
| 无词根 | 847 词，集中在主表末尾单独成节 |
| 多词根批注 | **43** 词（只有含 2 个及以上词根的词才有批注） |
| 音标 | 1865 / 1998 |
| 释义 | 1998 / 1998 |

主表列：序号 ｜ 词根 ｜ 词根含义 ｜ 单词 ｜ 音标 ｜ 释义 ｜ 批注。
同一词根的行在「词根 / 词根含义」两列纵向合并，并按词数从多到少排列；首行冻结、可筛选。

## 构建流程（可复现）

```
data/roots_canonical.tsv      # 306 条标准词根（含变体写法），分类基准
data/cet4_AS.tsv              # 大纲词表 A–S（web_fetch 截断位置）
data/cet4_full_source.tsv     # 5070 词候选库（A–S + 补齐的 S 尾段与 T–Z）
data/final_words.tsv          # 最终 1998 词：word, phonetic, meaning, tier, root, roots, note

scripts/parse_wordlist.py     # 解析大纲词表 -> TSV
scripts/build_new.py          # 从候选库中取出新收录的 1553 词并分片
scripts/split_core.py         # 按候选核心词分片（供子代理标注）
scripts/merge_chunks.py       # 校验并合并子代理标注结果（逐行对齐检查）
scripts/apply_keep.py         # 应用「补词根 + 筛选」结果
scripts/make_topup.py         # 生成补足候选
scripts/assemble.py           # 合并 A–S 与 S 尾/T–Z 两段，得到 final_ALL.tsv
scripts/split_multi.py        # 拆分已标词根的词，供多词根复核
scripts/apply_multi.py        # 应用多词根复核（严格规则：两个词根都必须在标准词根表内）
scripts/split_fill.py         # 拆分无词根词
scripts/apply_fill.py         # 应用无词根补标
scripts/normalize_roots.py    # 按 data/root_fix.tsv 修正重名/变体词根
scripts/fill_phonetic.py      # 从 data/_raw/ 的原始词表回填缺失音标
scripts/check_phonetic.py     # 音标体检（默认只报告，--fix 才修复）
scripts/audit_roots.py        # 词根表体检：重名键、非标准写法
scripts/build_xlsx.py         # 生成 xlsx
scripts/xlsx_writer.py        # 无依赖 xlsx 写入器（本机无 openpyxl 且 pip 无网络）
```

重建成品：`py -3 scripts/build_xlsx.py`
（`python` 不在 PATH 上，用 `py -3`。）

## 已知限制

* **音标**：133 词无音标。唯一的四级大纲完整词表文件（198 KB）超过 `web_fetch` 单次取回上限，
  其 S 尾段与 T–Z 部分缺少音标；已从另外几份词表尽量回填，剩余的不猜、留空。
* **外部校验**：`data/_raw/cuttlin_S.tsv` 是经 `web_fetch` 转写后落盘的（本机无直连网络），
  其中 2 条形近字段粘连的音标已在 `scripts/check_phonetic.py --fix` 中截取有效前缀修复。
* **选词边界**：S 尾段与 T–Z 的「是否属于四级」依据四级/六级合并词表判断，个别六级词可能混入；
  A–R 依据四级大纲，精确。

## 数据来源

1. 大学英语四级考试大纲词汇表 — `mahavivo/english-wordlists` · `CET4_edited.txt`
2. `cuttlin/Vocabulary-of-CET-4` 分字母词表（T–Z、S 段与音标）
3. `mahavivo/english-wordlists` · 中考英语词汇表（基础词音标/释义）
4. `JavaProgrammerLB/cet-word-list`（四级词表成员核对）
5. `RealKai42/qwerty-learner` 词书（释义补充）
