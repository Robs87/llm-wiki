---
name: llm-wiki
description: "Karpathy's LLM Wiki — build and maintain a persistent, interlinked markdown knowledge base. Ingest sources, query compiled knowledge, and lint for consistency."
version: 2.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [obsidian, arxiv, agentic-research-ideas]
---

# Karpathy's LLM Wiki

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent
summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context

## Wiki Location

**Location:** Set via `WIKI_PATH` environment variable (e.g. in `~/.hermes/.env`).

If unset, defaults to `~/wiki`.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

The wiki is just a directory of markdown files — open it in Obsidian, VS Code, or
any editor. No database, no special tooling required.

## Architecture: Three Layers + Human Control Layer

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log（倒序：最新在前，超 500 条轮转）
├── overview.md         # Living synthesis / current human-facing big picture
├── maps.md             # Human control: topic/concept map and core hubs
├── questions.md        # Human control: long-term recurring questions
├── principles.md       # Human control: reusable judgment principles
├── decisions.md        # Human control: decisions made with wiki support
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── sources/            # Layer 2a: One summary page per source document
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
├── queries/            # Layer 2: Filed query results worth keeping
└── graph/              # Auto-generated graph data (build-graph.py output)
    ├── graph.json      # Node/edge data (SHA256-cached)
    └── graph.html      # Interactive vis.js visualization
```

**Human Control Layer — Human-owned synthesis:** For large wikis, do not expect the
human to know every LLM-compiled page. Keep five stable entry pages the human can
actually master: `overview.md` (current big picture), `maps.md` (topic/concept map),
`questions.md` (long-term questions), `principles.md` (reusable judgment rules), and
`decisions.md` (choices made using the wiki). Also maintain `queries/inbox.md` as a
candidate-question inbox. Every ingest/query/organizing pass should run a return-flow
gate: update `overview` if the overall picture changed; `maps` if topic structure
changed; `questions` if a recurring/open question surfaced; `principles` if a reusable
judgment emerged; `decisions` if the wiki supported an action/choice; otherwise write
`Human layer: no update` or the reason in `log.md`. This is what keeps LLM-compiled
knowledge from becoming merely "the LLM's knowledge."

**Layer 1 — Raw Sources:** Faithful, immutable copies of original material. This layer is
equivalent to web clipping — preserve the original text and images exactly as-is.
**Do NOT summarize, analyze, or restructure content at this layer.** All summarization
and analysis belongs in Layer 2 (sources/, entities/, etc.). The agent reads but never
modifies files in raw/.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent. This is where summarization, analysis, and
cross-referencing happen (sources/, entities/, concepts/, comparisons/, queries/).
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

① **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
② **Read `index.md`** — learn what pages exist and their summaries.
③ **Scan recent `log.md`** — read the first 20-30 entries to understand recent activity（因为 log 采用倒序，最新在前）。

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# Orientation reads at session start
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=1 limit=120
```

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick `search_files` for the topic
at hand before creating anything new.

## Initializing a New Wiki

When the user asks to create or start a wiki:

1. Determine the wiki path (from `$WIKI_PATH` env var, or ask the user; default `~/wiki`)
2. Create the directory structure above
3. Ask the user what domain the wiki covers — be specific
4. Write `SCHEMA.md` customized to the domain (see template below)
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

### SCHEMA.md Template

Adapt to the user's domain. The schema constrains agent behavior and ensures consistency:

```markdown
# Wiki Schema

## Domain
[What this wiki covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be recorded in `log.md` with newest entries inserted at the top

## Frontmatter
  ```yaml
  ---
  title: Page Title
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | query | summary
  tags: [from taxonomy below]
  sources: [raw/articles/source-name.md]
  ---
  ```

## Tag Taxonomy
[Define 10-20 top-level tags for the domain. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed,
add it here first, then use it. This prevents tag sprawl.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report
```

### index.md Template

The index is sectioned by type. Each entry is one line: wikilink + summary.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total pages: N

## Entities
<!-- Alphabetical within section -->

## Concepts

## Comparisons

## Queries
```

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections
by first letter or sub-domain. When the index exceeds 200 entries total, create
a `_meta/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Newest entries first (reverse chronological).
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, keep the newest 400 in `log.md` and move older entries into `log-YYYY.md` archives.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

## Core Operations

### Human Control Layer initialization

When an existing wiki is already large or the user worries the wiki is becoming "LLM-owned",
initialize the Human Control Layer before doing more bulk ingest: create/update `maps.md`,
`questions.md`, `principles.md`, `decisions.md`, and `queries/inbox.md`; add them near the top
of `index.md`; add a `SCHEMA.md` rule requiring the return-flow gate after each ingest/query;
and log the change. Use `templates/human-control-layer.md` as the starter. Keep this layer
small and human-masterable — do not turn it into another compiled encyclopedia.

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source (faithful archive — no summarization):**
   - **This step is equivalent to web clipping.** Save the original text and images exactly
     as they appear. Do NOT add summaries, key takeaways, or analysis at this layer.
   - URL → use `web_extract` to get markdown; for anti-scraping sites (e.g. `mp.weixin.qq.com`),
     use `browser_navigate` to extract content and image URLs via JS.
   - PDF → use `web_extract` (handles PDFs), save to `raw/papers/`
   - Pasted text → save to appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/YYYY-MM-DD-title.md`
   - **Image handling — exactly one rule depending on vault setup:**
     - **CAL vault** (Obsidian with Custom Attachment Location): Download images to
       `raw/assets/${noteFileName}/` (noteFileName = raw md filename without `.md`).
       Rewrite references to `![](../assets/${noteFileName}/image.jpg)`.
     - **Non-CAL vault**: Download images to `raw/articles/<filename>_assets/` and
       rewrite to relative paths. **Never** create `_assets/` inside a CAL vault.
   - For WeChat articles, images use `data-src` lazy-loading — extract real URLs via
     browser JS (`document.querySelectorAll('img[data-src]')`) before downloading.
   - Preserve information-bearing visuals (charts, diagrams, screenshots, figures);
     skip low-value decorative assets (favicons, tracking pixels, tiny UI icons).
   - If an image cannot be fetched (anti-bot, auth wall, broken lazy-loading), explicitly
     report it; do not imply the raw capture is complete.

② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

③ **Check what already exists** — search index.md and use `search_files` to find
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.
   - If a closely related page exists but the new source covers a *different angle or
     sub-topic*, create a new page with a distinguishing title and cross-link from
     the existing page.
   - If a page simply needs updating (new facts, same topic), update the existing page.

④ **Plan wiki page changes** — based on ③'s findings, list which pages to create,
   update, or skip. For large ingests (10+ page changes), confirm scope with user first.

⑤ **Write or update wiki pages:**
   - **Create source summary page:** Write `sources/<slug>.md` using the Source Page
     Format below (or a domain-specific template if applicable).
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source)
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow the Update Policy.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in SCHEMA.md

⑥ **Run Human Control Layer return-flow gate** — decide whether this ingest changes any human-owned entry page:
   - Overall understanding changed → update `overview.md`
   - New topic cluster or changed topic structure → update `maps.md`
   - Recurring/open question surfaced → update `questions.md` or `queries/inbox.md`
   - Reusable judgment rule emerged → update `principles.md`
   - Source supports an actual action/choice → update `decisions.md`
   - If none apply, record `Human layer: no update` or a short reason in `log.md`

⑦ **Update overview.md** — revise the living synthesis if the new source
   changes the overall picture (new themes, shifted conclusions, etc.).

⑧ **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in index header
   - Insert at the top of `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
   - List every file created or updated in the log entry

⑨ **Post-ingest validation** — critical consistency check:
   - Verify all new `[[wikilinks]]` point to existing pages (run broken link check)
   - Verify all new pages appear in `index.md`
   - Print a change summary: files created, files updated, links added

⑩ **Report what changed** — list every file created or updated to the user.

A single source can trigger updates across 5-15 wiki pages. This is normal
and desired — it's the compounding effect.

### Source Page Format

Use this template for `sources/<slug>.md`:

```markdown
---
title: "Source Title"
type: source
tags: []
date: YYYY-MM-DD
source_file: raw/...
---

## Summary
2–4 sentence summary.

## Key Claims
- Claim 1
- Claim 2

## Key Quotes
> "Quote here" — context

## Connections
- [[EntityName]] — how they relate
- [[ConceptName]] — how it connects

## Contradictions
- Contradicts [[OtherPage]] on: ...
```

### Domain-Specific Templates

If the source falls into a specific domain, use a specialized template instead
of the default generic one above:

#### Diary / Journal Template
```markdown
---
title: "YYYY-MM-DD Diary"
type: source
tags: [diary]
date: YYYY-MM-DD
---

## Event Summary
...

## Key Decisions
...

## Energy & Mood
...

## Connections
- [[EntityName]] — how they relate
...

## Shifts & Contradictions
...
```

#### Meeting Notes Template
```markdown
---
title: "Meeting Title"
type: source
tags: [meeting]
date: YYYY-MM-DD
---

## Goal
...

## Key Discussions
...

## Decisions Made
...

## Action Items
- [ ] ...
```

### 1b. Long Page Split (技术长页拆分)

When a wiki page exceeds ~200 lines, split it into a **navigation mother page + content volumes**.
This is a repeatable batch operation — typically 3 pages per round, yielding ~10-12 new volumes.

**触发条件：** `check_page_size(wiki_path)` 返回超 200 行的页面，按行数降序取 top 3。

**流程：**

① **扫描目标** — 读 `check_page_size` 输出，选最重的 3 个。不要硬拆刚过阈值的页（收益太低），优先拆 250+ 行的。

② **分析章节结构** — 解析所有 `##` 二级标题，统计每个 section 的行数。

③ **规划分卷** — 按 topic 亲缘性把相邻 sections 组成 2-4 个 volume。每个 volume 应有独立主题：
   - Agent 配置类：会话启动+职责 / 工具+输出 / 工作流+协作 / 安全+异常
   - 技术文档类：背景+部署 / 原理+踩坑 / 验证+适用 / 局限+展望
   - 理念类：关注+价值观 / 方法+项目 / 技术栈+成长

④ **写分卷文件** — 每个分卷独立存为 `sources/{原文件名} - {分卷主题}.md`：
   - 继承母页 frontmatter（title 改为分卷全名，去掉 sources 字段）
   - 首行加 `[[{原文件名}|← 返回导航页]]` 反链
   - 正文为对应 sections 原文（不改动内容）

⑤ **改写母页为导航页** — 原文件替换为：
   - 保留原 frontmatter（bump updated 日期）
   - 一行说明：`> 本页已拆分为分卷页，以下为导航索引。`
   - 列出所有分卷的 wikilink（`- [[{分卷名}]]`）
   - 如有实质 preamble 内容，保留到 `## 概述` 段

⑥ **同步 index.md** — 在母页条目下方插入所有分卷条目（`- [[sources/{名}|{名}]]`），更新 Total pages 计数和日期。

⑦ **同步 log.md** — 插入到顶部：`## [YYYY-MM-DD] split | 技术长页拆分第N轮`，列出母页行数变化和分卷名。

⑧ **复检** — 运行 `find_broken_links` + `find_orphans` + `check_index_completeness`，全部归零才算完成。顺手修复历史遗留的 index 文件名不匹配。

**Pitfalls：**
- **Python heredoc 中避免 f-string 嵌套** — 在 `terminal` heredoc 里用 f-string 且字符串含大括号时极易 SyntaxError。改用字符串拼接。
- **index.md 条目文件名必须与磁盘文件精确匹配** — 中文文件名中的空格、全角/半角差异是 index completeness 误报的头号原因。先 `ls` 确认真实文件名，再写 index。
- **分卷数量以 3-4 个为宜** — 太少等于没拆，太多导航成本反升。
- **不要改写正文内容** — 拆分是结构操作，不是编辑操作。原封不动搬运 section 文本。

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also `search_files` across all `.md` files
   for key terms — the index alone may miss relevant content.
③ **Read the relevant pages** using `read_file`.
④ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑥ **File valuable answers back** — do not rely on the user to copy/paste valuable
   fragments. If a question meets at least 2 value criteria (recurs, changes judgment,
   connects multiple themes, will be reused, exposes a gap, or produces a principle),
   append it to `queries/inbox.md` with the value rationale and suggested destination.
   If it meets 3+ criteria or would be painful to re-derive, propose or create a formal
   `queries/` or `comparisons/` page as appropriate. The inbox is a candidate pool, not
   final knowledge: AI captures candidates; the human calibrates/promotes them.
⑦ **Run Human Control Layer return-flow gate** — update `overview.md`, `maps.md`,
   `questions.md`, `principles.md`, or `decisions.md` when the answer changes the big
   picture, topic map, long-term questions, reusable principles, or concrete choices.
⑧ **Update log.md** with the query, whether it was filed/promoted, and the human-layer
   outcome (`Human layer: updated ...` or `Human layer: no update`).

### 4. Health (Pre-Flight Check)

> **Health vs Lint 分界：** Health 是结构完整性检查（零 LLM 调用），
> 每次 session 开始前运行。Lint 是内容质量检查（需要 LLM 语义分析），
> 每 10-15 次 ingest 后运行。先跑 health，再跑 lint — 对空文件跑 lint 浪费 token。

When the user asks for a health check, or at the start of a new wiki session:

| 维度 | `health` | `lint` |
|---|---|---|
| **范围** | 结构完整性 | 内容质量 |
| **LLM 调用** | 零 | 是（语义分析） |
| **成本** | 免费 | Token |
| **频率** | 每次 session | 每 10-15 次 ingest |
| **检查项** | 空文件、index 同步、log 覆盖率 | 孤儿页、断链、矛盾、数据缺口 |
| **工具** | `references/health-check.py` | Agent 内联逻辑 |
| **执行顺序** | 先（pre-flight） | 后（health 通过后） |

**检查项：**
1. **Empty / stub files** — 正文不足 100 字符的页面（可能是 rate-limit 损坏）
2. **Index sync** — `index.md` 条目 vs 文件系统实际文件
③ **Log coverage** — source 页面是否有对应的 log 条目。注意：历史补录不一定是逐页 `## ... ingest | 标题`；也可能是批量 backfill（例如一个 `update` 条目下面列出 `- sources/foo.md` 清单）。health-check / 自定义检查在做 log coverage 时，必须同时识别：① 逐条 `ingest|create|update` 标题；② 批量 backfill 中列出的 `sources/*.md` 路径。否则会把已补录的历史来源页继续误报为缺失覆盖。

**执行方式：**

```bash
# Agent 可用 execute_code 调用 references/health-check.py 中的函数
WIKI="${WIKI_PATH:-$HOME/wiki}"
python3 "$SKILL_DIR/references/health-check.py" --json
# 或：python3 "$SKILL_DIR/references/health-check.py" --save  # 输出到 wiki/health-report.md
```

也可直接用 `execute_code` 内联调用 `run_health()` 函数获取结构化报告。

> 备注：health 检查应只覆盖 wiki layer（`sources/`、`entities/`、`concepts/`、`comparisons/`、`queries/`、`overview.md`），不要把 `raw/`、`.obsidian/`、`graph/` 等目录混入；`index.md` 解析同时要支持标准 markdown 链接和 Obsidian `[[wikilinks]]`，否则会产生大量假阳性。解析 `[[target|alias]]` 时不能假设 alias 内不含 `]`：像 `([美] 作者)` 这类常见中文别名会让简单正则提前截断，导致 index_sync 误报。实现上优先用 `re.finditer(r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|.*?)?\]\]')` 这类“抓 target、别名非贪婪吃到 `]]`”的写法，而不是 `(?:\|[^\]]+)?`。

### 5. Graph

When the user asks to build the knowledge graph, or wants to visualize wiki structure:

**两阶段构建：**

1. **Pass 1（确定性）** — 解析所有 wiki 页面中的 `[[wikilinks]]` → `EXTRACTED` 边
2. **Pass 2（语义推理）** — Agent 推断 wikilinks 未捕获的隐含关系 → `INFERRED` 边（附置信度）；低置信度 → `AMBIGUOUS`

**输出：**
- `graph/graph.json` — `{nodes, edges, built: date}`，SHA256 缓存避免重算
- `graph/graph.html` — 自包含 vis.js 交互可视化（无服务器，浏览器直接打开）

**图谱健康报告（`graph/graph-report.md`）：**

| 指标 | 含义 |
|---|---|
| Health summary | edges/node 比率、孤儿率、社区数、链接密度 |
| Orphan nodes | 零连接的页面 |
| God nodes | 超连接枢纽（degree > μ+2σ） |
| Fragile bridges | 社区间仅 1 条边连接 |
| Phantom hubs | 被 2+ 页面引用但页面本身不存在 → 强创建信号 |

**执行方式：**

```bash
# 需要 networkx（pip install networkx）用于社区发现
WIKI="${WIKI_PATH:-$HOME/wiki}"
python3 "$SKILL_DIR/references/build-graph.py" --no-infer   # 仅确定性边（快）
python3 "$SKILL_DIR/references/build-graph.py"               # 完整构建（含语义推理）
python3 "$SKILL_DIR/references/build-graph.py" --open        # 构建后浏览器打开
python3 "$SKILL_DIR/references/build-graph.py" --report --save  # 生成健康报告
```

如果 Python/依赖不可用，agent 可手动构建：
1. 用 `search_files` 找到所有 `[[wikilinks]]`
2. 构建 nodes（每页一个）和 edges（每条链接一条）
3. 写 `graph/graph.json`
4. 写 `graph/graph.html` 使用 vis.js 模板

### 3. Lint

When the user asks to lint, health-check, or audit the wiki:

> **Lint 脚本参考：** `references/lint-scripts.py` 提供了 ①②③④⑦⑧⑨ 项的
> 可执行 Python 函数。Agent 可直接用 `execute_code` 内联调用，或将其作为
> 实现模板。⑤（stale content）和⑥（contradictions）需要 LLM + 人工判断，
> 脚本不直接覆盖。下面的每项检查标注了对应的函数名。

**Automated checks**（可用脚本直接运行）:

> **脚本适配提醒（已踩坑）**：如果 wiki 把 `sources/` 当作 wiki layer 的正式页面目录，`references/lint-scripts.py` 必须把 `sources` 纳入 `WIKI_DIRS`，且 `VALID_TYPES` 必须包含 `source`；否则 broken links / orphan / index completeness 会报大量假阳性。若页面允许直接链接根层控制页 `SCHEMA.md`、`index.md`、`log.md`、`overview.md`，lint 也必须把这些名字加入 existing set；做 orphan 检测时，还要把这些根层页面本身纳入“出链来源”，否则 index/overview 已收录的页面仍会被误报为孤儿。对于 `[[raw/articles/foo.md]]` 这类 raw 链接，要按 `base_dir/link` 的真实路径判断，不要错误拼成 `raw/raw/...`。另外，tag audit 只能读取**首个正式 YAML frontmatter**，不能把正文里二次嵌入的元数据块当成页面标签；taxonomy 提取也要只读 `SCHEMA.md` 的 `## Tag Taxonomy` 段，并正确解析带反引号的条目（如 ``- `framework` — ...``），否则会把 used tags / unlisted tags 误报得非常夸张。

① **Orphan pages** → `find_orphans(wiki_path)` — 零入链的 wiki 页面。

② **Broken wikilinks** → `find_broken_links(wiki_path)` — 指向不存在页面的
   `[[links]]`。注意：指向 `raw/` 下文件的链接不算断链。

③ **Index completeness** → `check_index_completeness(wiki_path)` — 对比
   文件系统 vs `index.md`，返回遗漏和多余条目。

④ **Frontmatter validation** → `validate_frontmatter(wiki_path)` — 检查
   必填字段（title, created, updated, type, tags, sources）和 type 合法性。

⑤ **Stale content** — Pages whose `updated` date is >90 days older than the
   most recent source. 需 agent 读取 `raw/` 源文件日期后对比，脚本不直接覆盖。

⑥ **Contradictions** — Pages that share tags/entities but state different facts.
   **⚠ 不可完全自动化：** agent 做预筛选（按 tag/entity 分组同主题页面），
   但最终矛盾判定需要 LLM 阅读 + 用户确认。输出格式：
   ```
   潜在矛盾: [[page-a]] vs [[page-b]]
     - page-a: "声明 X"
     - page-b: "声明 Y（与 X 矛盾）"
     - 建议: 用户审核
   ```

⑦ **Page size** → `check_page_size(wiki_path)` — 超过 200 行的页面，按行数
   降序排列。

⑧ **Tag audit** → `audit_tags(wiki_path)` — 对比所有页面使用的标签 vs
   `SCHEMA.md` taxonomy，列出不在 taxonomy 中的标签及其使用位置。

⑨ **Log rotation** → `check_log_rotation(wiki_path)` / `rotate_log(wiki_path)` — log.md 超过 500 条时
   保留最新 400 条在 `log.md`，把更旧记录按年份归档到 `log-YYYY.md`；不要因为轮转把当前最近日志清空。

**Severity grouping**（报告必须按此顺序分组）:
1. 🔴 Broken links — 功能性错误，必须立即修复
2. 🟠 Orphan pages — 知识孤立，影响可发现性
3. 🟡 Stale content / Contradictions — 信息可能过时，需审核
4. 🟢 Style issues (frontmatter, tag, page size) — 规范问题

**Graph-aware checks**（需要 `graph/graph.json` 存在时才运行）:

⑩ **Phantom hubs** — 被 2+ 页面的 `[[wikilink]]` 引用但页面本身不存在的名称。
   这是强烈的新页面创建信号，按引用数降序排列。

⑪ **Hub stubs** — God nodes（degree > μ+2σ）但正文不足 500 字符。
   高连接度但内容单薄 — 需要充实。

⑫ **Fragile bridges** — 社区间仅 1 条边连接。删除任一端就断联。

⑬ **Sparse pages** — 出链少于 2 条的 wiki 页面（链接密度不足）。

⑭ **Data gaps** — Wiki 无法回答的领域问题，建议补充的源文件。

⑮ **Report findings** with specific file paths and suggested actions, grouped
    by severity above.

⑯ **Fix issues** — resolve in severity order (🔴 → 🟠 → 🟡 → 🟢).

⑰ **Re-verify after repair** — re-run `find_broken_links` + `find_orphans` +
    `check_index_completeness` to confirm no new issues were introduced.
    If new issues appear, repeat from ⑮ until clean.

⑱ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found, M fixed`

## Working with the Wiki

### Searching

```bash
# Find pages by content (Hermes search_files: pattern=regex, path=dir, file_glob=*.md)
search_files pattern="transformer" path="$WIKI" file_glob="*.md"

# Find pages by filename
search_files pattern=".*\\.md$" target="files" path="$WIKI"

# Find pages by tag (search inside frontmatter tags field)
search_files pattern="alignment" path="$WIKI" file_glob="*.md"

# Recent activity
read_file path="$WIKI/log.md" offset=1 limit=80
```

> **Hermes 工具说明：** `search_files` 参数是具名参数（`pattern`, `path`, `file_glob`, `target`），
> 不是位置参数。`target="files"` 按文件名搜索，默认 `target="content"` 按内容搜索。

### Bulk Ingest

When ingesting multiple sources at once, batch the updates:
1. Read all sources first
2. Identify all entities and concepts across all sources
3. Check existing pages for all of them (one search pass, not N)
4. Create/update pages in one pass (avoids redundant updates)
5. Update index.md once at the end
6. Write a single log entry covering the batch

### Archiving

When content is fully superseded or the domain scope changes:
1. Create `_archive/` directory if it doesn't exist
2. Move the page to `_archive/` with its original path (e.g., `_archive/entities/old-page.md`)
3. Remove from `index.md`
4. Update any pages that linked to it — replace wikilink with plain text + "(archived)"
5. Log the archive action

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box:
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- Image paths follow the rules in ingest ① (CAL vs non-CAL vault) — no separate
  rules here; that section is the single source of truth.

For best results:
- Enable "Wikilinks" in Obsidian settings (usually on by default)
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

If using the Obsidian skill alongside this one, set `OBSIDIAN_VAULT_PATH` to the
same directory as the wiki path.

### Obsidian Headless (servers and headless machines)

On machines without a display, use `obsidian-headless` instead of the desktop app.
It syncs vaults via Obsidian Sync without a GUI — perfect for agents running on
servers that write to the wiki while Obsidian desktop reads it on another device.

**Setup:**
```bash
# Requires Node.js 22+
npm install -g obsidian-headless

# Login (requires Obsidian account with Sync subscription)
ob login --email <email> --password '<password>'

# Create a remote vault for the wiki
ob sync-create-remote --name "LLM Wiki"

# Connect the wiki directory to the vault
cd ~/wiki
ob sync-setup --vault "<vault-id>"

# Initial sync
ob sync

# Continuous sync (foreground — use systemd for background)
ob sync --continuous
```

**Continuous background sync via systemd:**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# Enable linger so sync survives logout:
sudo loginctl enable-linger $USER
```

This lets the agent write to `~/wiki` on a server while you browse the same
vault in Obsidian on your laptop/phone — changes appear within seconds.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates, missed cross-references, and wrong assumptions about what already exists.
- **Install/creation tasks also need duplicate checks** — before creating a new page/record/skill-like object, first search whether an equivalent object already exists locally or in recent history. Classify the task as create vs update vs repair before writing anything.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone. For vault-like setups where a clipped page is a real knowledge-base object,
  a successful web clip is not "done" until the control layer is also synchronized when the schema says so.
- **Restore is different from rewrite** — if the user asks to restore a page, first look for a real source of truth
  (git history, backups, raw source, existing duplicate, recent log context). If you cannot recover the original text,
  do **not** overwrite the target page with a guessed reconstruction and call it restored. Say explicitly that only a
  reconstruction draft is possible, and get the user's approval before writing anything.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, keep the newest 400 in `log.md` and archive older entries into `log-YYYY.md` by year.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.
- **Run health before lint** — linting an empty or stub file wastes tokens and produces
  misleading results. Always run the health pre-flight check first.
- **Post-ingest validation is not optional** — every ingest must end with a consistency
  check (broken links, index completeness). Skipping it silently introduces decay.
- **WeChat articles require browser-based extraction** — a direct HTTP fetch may return HTML that lacks usable `#js_content` / author / publish-time markers even though the rendered page has them. For `mp.weixin.qq.com` pages: (1) use `browser_navigate` to load the page, (2) extract images via `document.querySelectorAll('img[data-src]')` because WeChat uses lazy-loading (`data-src` holds the real URL, `src` is empty), (3) download images per the vault's image rule (see ingest ① — CAL or non-CAL), (4) rewrite the raw markdown with local image references. Do NOT save a text-only raw file — raw must include images.
- **Do not hardcode CAL attachment paths** — when a wiki lives inside an Obsidian vault, inspect the vault's actual CAL/plugin config before saving images. The attachment root may be `raw/assets/${noteFileName}` instead of a global `05_Attachments/...` path.
- **Image path single source of truth** — ingest ① defines the only image handling rules. Obsidian Integration and Pitfalls sections reference it, not duplicate it.
- **Source-page images use Markdown image syntax** — for source/source-like wiki pages, embed local images with relative Markdown paths such as `![](../raw/assets/...)`, not Obsidian `![[...]]`, to avoid render/lint inconsistencies across tooling.
- **Raw diary ingest is usually partial update, not bulk create** — before ingesting `raw/diary/` or another date-note folder, first map raw filenames/dates against existing `sources/` pages. Many diary files may already be ingested under renamed source titles. Do a coverage check first, then ingest only the missing raw files; otherwise you create duplicates and inflate `index.md` / `log.md` for no gain.
- **Lint may treat image wikilinks to `raw/assets/` as broken links** — if a source page embeds images stored under `raw/assets/...`, prefer standard markdown image links with a correct relative path like `![](../raw/assets/foo/bar.png)` rather than `![[raw/assets/foo/bar.png]]` unless your lint/build pipeline explicitly whitelists image wikilinks.
- **Graph inference is expensive** — Pass 2 (semantic) uses LLM calls per page.
  Use `--no-infer` for frequent quick checks; full inference only when the wiki
  has changed significantly (10+ ingests since last build).
- **Phantom hubs are action items, not errors** — when 3+ pages reference `[[Topic]]`
  but no page exists, that's the wiki telling you what to create next.
- **Overview.md is a living document, not a forced dump** — run the Human Control Layer
  return-flow gate on every ingest/query. Update `overview.md` only when the overall picture
  changes; otherwise record `Human layer: no update` or the short reason in `log.md`. A stale
  overview defeats the purpose, but noisy forced updates make the human layer unreadable.
