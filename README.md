<p align="center">
  <h1 align="center">CET-4 词缀翻卡记忆站</h1>
  <p align="center">把四级核心词按词根词缀重新组织，让人看得见「为什么是这个意思」</p>
</p>

<p align="center">
  <a aria-label="Deliverable" href="./out"><img alt="" src="https://img.shields.io/badge/%E6%88%90%E5%93%81-1998%20%E8%AF%8D%20%C2%B7%20260%20%E8%AF%8D%E6%A0%B9-2f6f4e?style=for-the-badge&labelColor=000000"></a>
  <a aria-label="Python" href="./scripts"><img alt="" src="https://img.shields.io/badge/Python-%E4%BB%85%E6%A0%87%E5%87%86%E5%BA%93%20%C2%B7%20%E9%9B%B6%E4%BE%9D%E8%B5%96-3776ab?style=for-the-badge&logo=python&labelColor=000000&logoColor=white"></a>
  <a aria-label="Frontend plan" href="./foundation/TECH_SPEC.md"><img alt="" src="https://img.shields.io/badge/%E5%89%8D%E7%AB%AF-ES5%20%C2%B7%20%E9%9B%B6%E6%9E%84%E5%BB%BA%20%C2%B7%20%E7%A6%BB%E7%BA%BF%E5%8F%AF%E7%94%A8-f0a020?style=for-the-badge&labelColor=000000"></a>
  <a aria-label="Screens" href="./foundation/DESIGN.md"><img alt="" src="https://img.shields.io/badge/%E5%B1%8F%E5%B9%95-1366%C3%97768%20%E4%B8%80%E5%B1%8F%E6%94%BE%E4%B8%8B-555555?style=for-the-badge&labelColor=000000"></a>
</p>

## 概述

背四级单词最常见的两个失败原因：

1. **单词表是字母序的**——`abandon` 和 `abandonment` 隔了几十页，词与词之间没有关系，记忆只能靠一遍遍重复；
2. **「按词根背」听起来很好，动手却很难**——想按词根组织，得自己查词源、判断一个词该归到哪个词根、再手抄成表；网上现成的词根表又常常混入错误拆分（把 `interest` 拆成 `in-` + `terest`），越背越乱。

本项目把这两件事都做成了可复现的工程：

- 以《大学英语四级考试大纲词汇表》为主干，**筛出 1998 个四级核心词**（剔除中学基础词、语义透明的派生词、超纲的六级生僻词）；
- 用 **306 条标准词根表**（含 `sta / stat / stit` 这类变体写法）把其中 **1151 词**归入 **260 个常见希腊/拉丁词根**，按词根成组输出；
- 为单词生成**构词助记串**：看到的不是 `review = 复习`，而是 `re-(再) + view(看) → 再看一遍 → 复习`；
- 最终交付一张**可直接使用的 Excel 表**（词根分类 + 词根索引 + 说明三张工作表），并配有一套**零依赖、可复现**的 Python 数据处理脚本。

> **产品形态**：数据成品（xlsx）**已经可用**；网页版「词缀翻卡记忆站」的设计与技术方案**已经完成**，实现尚未开始（见「项目状态」与 [`foundation/`](./foundation)）。

---

## 它解决什么问题

| 痛点 | 具体表现 | 本项目的做法 |
|---|---|---|
| 词与词孤立 | 字母序词表里同族词被拆散，记 10 个词等于记 10 件无关的事 | 以词根为聚类键，同根词连续成组；记一个 `sist`（站）能带动 assist / consist / exist / insist / persist / resist / stable / station… 共 38 词（含 `sta / stat / stit` 变体拼写） |
| 词根表不可信 | 网上词表存在错误拆分与写法混乱（`spect` 被写成 `spec`/`specto`，同根词散落各处） | 建 `roots_canonical.tsv` 标准词根表，统一写法 + 记录变体；`audit_roots.py` 做体检，当前 **重名键 0、非标准写法 0** |
| 只有结论没有过程 | 「记住就行」型词表，看不出构词逻辑 | 生成 `breakdown` 助记串；实测 **933 / 1151（81.1%）** 的带词根词，其拼写直接包含词根或其变体，可自动生成助记 |
| 数据来源不可追溯 | 网上流传的词表说不清是哪一版大纲、缺词漏词无人知 | 9 份来源全部**逐字留档**在 `data/_raw/`，`source_notes.md` 记录每一份的用途、体积、字母区间与**被拒绝的来源及原因** |
| 老电脑跑不动 | 现代前端项目动辄几 MB，Win7 办公机/集显/2GB 内存直接白屏 | 前端基线锁定 **ES5 + 零依赖 + 零构建 + 零外链**，`file://` 双击可用，并另出「单文件便携版」 |

---

## 仓库结构

```text
Cet4Learning/
├── foundation/                   # 设计与方案文档（先读这里）
│   ├── idea.txt                  # 玩法原始需求（9 行）
│   ├── DESIGN.md                 # 产品设计：界面 / 状态机 / 翻卡交互 / 响应式档位 / 兼容性基线
│   ├── TECH_SPEC.md              # 技术方案：数据层 / Unit Builder / 构建脚本 / 兼容守卫 / 验收矩阵
│   └── CET4.md                   # 数据成品说明书（数字口径与已知限制）
├── data/                         # 数据层（四段式流水线，见下）
│   ├── _raw/                     # 上游原始词表逐字留档（9 份，约 600 KB）
│   ├── chunks/ core/ fill/ keep/ # 中间产物：分片 → 标注 → 回灌
│   ├── multi/ topup/ ...keep/    # 多词根复核与补足的分片与回灌结果
│   ├── cet4_*.tsv                # 各阶段明细：大纲解析、S 尾/T–Z 补齐、候选库、缺漏清单
│   ├── roots_canonical.tsv       # 306 条标准词根（写法 / 中文含义 / 变体）
│   ├── root_fix.tsv gloss_fix.tsv# 人工审定的小型修正表
│   ├── final_words.tsv           # 【关键】最终 1998 词：word/phonetic/meaning/tier/root/roots/note
│   ├── tagged_AS.tsv ...         # 标注中间态
│   ├── parse_source.py           # 原始词表 → TSV 的解析脚本
│   └── source_notes.md           # 数据来源与不确定性说明
├── scripts/                      # 19 个 Python 脚本（仅标准库，无第三方依赖）
├── out/
│   └── CET4核心2000词_词根分类.xlsx   # 【成品】3 个工作表，直接可用
└── README.md
```

---

## 主要功能

**成品表 `out/CET4核心2000词_词根分类.xlsx`**

| 工作表 | 内容 |
|---|---|
| 词根分类词汇表 | 1998 词，列：序号 ｜ 词根 ｜ 词根含义 ｜ 单词 ｜ 音标 ｜ 释义 ｜ 批注；同词根行纵向合并、按词数从多到少排列、首行冻结、可筛选 |
| 词根索引 | 按词数排序的词根清单，用于挑「高产词根」优先攻克 |
| 说明 | 选词标准、列说明、数据来源、已知限制与使用建议（表内自解释，不依赖 README） |

**数据与脚本能力**

- **选词**：5070 词候选库 → 1998 词核心表（剔除中学基础词 / 语义透明派生词 / 六级生僻词三类）；
- **归词根**：1151 词进入 260 个词根（`tier` 分档 1: 859 / 2: 1139，高频词优先）；
- **助记**：43 个多词根词带人工批注（`arch(首领)+tect(覆盖) → 建筑师`）；其余带词根词走规则生成（81.1% 命中）；
- **字段补全**：音标 1865 / 1998、释义 1992 / 1998，缺的一律**留空不猜**，并留有固定回填入口（`fill_phonetic.py` / `gloss_fix.tsv`）；
- **数据校验**：`audit_roots.py`（词根表体检）、`check_phonetic.py`（音标体检，默认只报告、`--fix` 才修复）、`merge_chunks.py`（合并前逐行对齐校验）；
- **应用管线**：`core → keep → multi → fill → normalize → assemble → build_xlsx` 七步回灌，每步都可单独重跑。

**网页版（方案已定，未实现）**

- 自选每日单词量 → 词缀面板 + 5 张同族词卡 → 点卡出释义 → 翻卡自测 → 完成页「添加单词」续接；
- 取词游标只前进不回退，「添加单词」天然不重不漏；场次自包含，刷新即恢复；
- 键盘快捷键（`1~5` / 空格 / `←` `→`）、四档响应式、三级动画降级（3D 翻面 → 淡入 → 直切）。

---

## 运行 / 使用说明

### 一、直接用成品（无需任何环境）

1. 打开 [`out/CET4核心2000词_词根分类.xlsx`](./out/CET4%E6%A0%B8%E5%BF%832000%E8%AF%8D_%E8%AF%8D%E6%A0%B9%E5%88%86%E7%B1%BB.xlsx)（Excel / WPS / LibreOffice 均可）；
2. 建议按「用法」用：**先按词根成组记忆**——同一词根下的词共用一个含义，记一个词根带动 5~10 个单词；
3. 想先攻高频词根，去「词根索引」按词数排序挑高产词根；
4. 无词根的那 847 词排在主表末尾单独成节，多为本族语基础词，靠语境记忆，不必强求词根。

### 二、重建数据（需要 `py -3`）

本机环境假设：**解释器只有 `py -3`**（`python` 不在 PATH 上），**无第三方包、无网络**。

```powershell
cd "D:\ds practice\Cet4Learning"
py -3 scripts\build_xlsx.py     # 从 final_words.tsv 重建成品（实测约 0.3 秒）
```

输出 `out/CET4核心2000词_词根分类.xlsx`（147,956 字节，**确定性构建**：重复执行字节一致）。

完整流水线（一般只在需要改动数据时才会走全套）：

```powershell
py -3 data\parse_source.py         # 原始词表 → cet4_TZ_source.tsv / cet4_full_source.tsv
py -3 scripts\parse_wordlist.py    # 大纲词表行 → TSV
py -3 scripts\build_new.py         # 从候选库取出新收录的词并分片
py -3 scripts\split_core.py        # 分片 → core/（供标注）
py -3 scripts\apply_keep.py        # 应用标注结果 → keep/
py -3 scripts\merge_chunks.py      # 分片回灌（逐行对齐校验）
py -3 scripts\split_multi.py       # 拆出多词根词复核
py -3 scripts\apply_multi.py       # 应用多词根复核（两个词根都须在标准表内）
py -3 scripts\split_fill.py        # 拆出无词根词
py -3 scripts\apply_fill.py        # 应用无词根补标
py -3 scripts\make_topup.py        # 生成补足候选
py -3 scripts\apply_topup_keep.py  # 应用补足筛选
py -3 scripts\normalize_roots.py   # 按 root_fix.tsv 统一重名/变体词根
py -3 scripts\fill_phonetic.py     # 从 data\_raw\ 回填缺失音标
py -3 scripts\assemble.py          # 合成 final_ALL.tsv
py -3 scripts\build_xlsx.py        # 生成 xlsx
```

体检与校验（改数据后建议都跑一遍）：

```powershell
py -3 scripts\audit_roots.py       # 词根表：重名键 / 非标准写法
py -3 scripts\check_phonetic.py    # 音标体检（默认只报告；--fix 才修复）
py -3 scripts\analyze_derivatives.py   # 统计透明派生词，用于复核选词边界
```

### 三、网页版

尚未实现。方案见 [`foundation/DESIGN.md`](./foundation/DESIGN.md)（产品与交互）与 [`foundation/TECH_SPEC.md`](./foundation/TECH_SPEC.md)（数据层与构建脚本）。
实现后的使用方式是：双击 `index.html`（或拷走单个 `build/CET4翻卡记忆_单文件版.html`）即可离线使用，无需服务器。

---

## 项目里的实用与创新内容

**1）无依赖 xlsx 写入器（`scripts/xlsx_writer.py`，214 行）**
目标机器上没有 `openpyxl` 且 `pip` 无网络。于是用标准库 `zipfile` + XML 手写了一个最小 `.xlsx` 生成器：内联字符串、固定样式表、列宽、冻结首行、自动筛选、单元格合并、行高。**成品表因此可以在任何只有 Python 标准库的机器上重新生成**，而不是把一个二进制文件当作唯一真相。

**2）标准词根表 + 体检脚本（`roots_canonical.tsv` + `audit_roots.py`）**
词根表的真正难点不是「有哪些词根」，而是**同一个词根不要写成三种样子**。本项目把「标准写法」与「常见变体/说明」分成两列（如 `sist` 对应 `sta, stat, stit`），并用脚本断言「重名键 0、词表使用的词根全部能在标准表中查到」。变体列后来还成了助记串生成的匹配依据——**同一份数据同时服务于聚类和讲解**。

**3）可解释的助记生成，且明确标注「不臆造」**
助记串按四级策略降级：L1 用人工批注 → L2 规则生成（前缀剥离 + 词根变体在拼写中的最长匹配）→ L3 批量标注 → L4 兜底显示「该词暂无助记」。并且方案里写明了已知质量风险：拼写匹配率 81% **不等于语义匹配率**（`return` 的历史词源确实与 `tort` 相关，但直觉上突兀），因此规则结果必须抽检、不通过就降级，**宁可不讲也不讲错**。

**4）「分片 → 标注 → 回灌」的可校验管线**
把几百个词拆成小分片交给人工/子代理标注，再用 `merge_chunks.py` **逐行对齐校验**后合并；配套 `*keep*` 目录保留筛选结果，`root_fix.tsv` / `gloss_fix.tsv` 记录人工修正。好处是：标注过程可以并行、可以返工，而**回灌永远是确定的**。

**5）留空不猜的数据原则**
音标缺 133 词、释义曾缺 6 词，处理方式都是**留空 + 记录缺口清单**（`cet4_missing_gloss.tsv`），从不根据拼写猜音标、根据上下文编释义。`source_notes.md` 里连「某份来源是 Big5 编码，按 UTF-8 解码会毁掉全部中文释义，故弃用」这类判断都写下来了——**数据的可信度来自它敢承认哪里不知道**。

**6）为「2015 年的老电脑」写前端**
前端基线是一条硬约束而不是愿望：ES5 语法（`var` / `function` / 字符串拼接）、Chrome 49+ / Firefox 45+ / Safari 9+ / Edge 12+、1366×768 一屏无滚动、1024×768 不溢出、零外链、`localStorage` 全量 `try/catch` 兜底。并且把这条承诺变成**机器可验证的断言**：`check_es5.py` 用正则黑名单扫 `app.js` 与 `styles.css`（禁用箭头函数、`let/const`、模板串、`display:grid`、`gap:`、`clamp()`、CSS 变量等），命中即构建失败。

**7）用实测推翻自己的估算**
方案 v1.0 估计运行期数据约 350 KB 并据此设计了「紧凑分隔串」格式。实测后：最啰嗦的字段名格式只有 172 KB、短字段名 104 KB、紧凑串 77 KB——**体积根本不是瓶颈**，为省 27 KB 而引入自定义分隔符解析不划算（实测数据里已有 99 条释义含 ASCII 分号，会导致静默错行）。于是默认改用 JSON，紧凑格式降级为可选开关。这次「证伪」是文档里显式记录的一节。

**8）轻量化不只在前端**
运行时开销与总词数几乎无关（只切片、只渲染当前页 5 张卡），因此 1487 词可以全量进 MVP，不需要「先拿 100 词跑通再扩量」的过渡阶段；渲染粒度也细化为「点卡只切类名、换页只重建卡片区、切视图才整体重建」，避免弱 CPU 上每秒重排。

---

## 项目状态

| 部分 | 状态 |
|---|---|
| 数据管线（`data/` + `scripts/`） | **已完成并可复现**：19 个脚本、四段式流水线、确定性构建 |
| 成品 Excel（`out/`） | **已完成**：1998 词 / 260 词根 / 3 个工作表 |
| 产品设计（`foundation/DESIGN.md`） | 已完成（v1.1，含兼容性与屏幕基线） |
| 技术方案（`foundation/TECH_SPEC.md`） | 已完成（v1.1，含数据契约 10 条断言与验收矩阵） |
| 网页版（`index.html` / `styles.css` / `app.js` / `data/words.js`） | **未实现**（方案阶段）；M0 数据构建 → M1 骨架 → M2 交互 → M3 兼容性打磨 |

---

## 已知限制（如实记录）

- **音标缺 133 词**：唯一完整的四级大纲词表（198 KB）超过 `web_fetch` 单次取回上限，其 S 尾段与 T–Z 部分缺音标；已从其他词表尽量回填，剩余留空，不猜。
- **选词边界**：A–R 依据四级大纲，精确；S 尾段与 T–Z 的「是否属于四级」依据四级/六级合并词表判断，**个别六级词可能混入**（估计 10~20%，因无纯六级词表可取回而无法精确测量）。
- **释义风格不统一**：大纲原文释义偏简短，补写的部分偏详细（多义项、最长 160 字符）。
- **助记串质量**：规则生成的助记在少数词上「词源正确但直觉突兀」，未抽检的结果不对外展示。
- **旧浏览器回归未实测**：Chrome 49 / Firefox 45 / Safari 9 等老旧浏览器无法在本机安装，方案中以「语法与特性守卫脚本全绿 + 禁用特性的等价模拟」作为替代证据，**不谎称已验证**。

---

## 数据来源

9 份上游文件全部逐字留档于 `data/_raw/`，明细（体积、字母区间、用途、被拒绝的原因）见 [`data/source_notes.md`](./data/source_notes.md)。主要来源：

1. 大学英语四级考试大纲词汇表 — `mahavivo/english-wordlists` · `CET4_edited.txt`（A–S 主干，权威释义）。
2. `cuttlin/Vocabulary-of-CET-4` 分字母词表（T–Z 与音标，其总表超限故改用分字母 JSON）。
3. `mahavivo/english-wordlists` · 中考英语词汇表（基础词音标/释义，用于回填）。
4. `JavaProgrammerLB/cet-word-list`（四级词表成员核对）。
5. `RealKai42/qwerty-learner` 词书（释义补充：单词的减法 4 / 高中乱序 2 / 高考真题核心高频）。

## 许可证

本仓库尚未添加 `LICENSE` 文件；上游词表各自的许可与署名要求见 `data/source_notes.md`，再分发前请一并遵守。
