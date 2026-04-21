---
name: llm-wiki
description: "Karpathy's LLM Wiki — build and maintain a persistent, interlinked markdown knowledge base. Ingest sources, query compiled knowledge, and lint for consistency."
version: 2.1.0
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

## Architecture: Three Layers

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── overview.md         # Living synthesis across all sources (updated on ingest)
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

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent.
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

① **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
② **Read `index.md`** — learn what pages exist and their summaries.
③ **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# Orientation reads at session start
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
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
- Every action must be appended to `log.md`

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

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

## Core Operations

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source:**
   - URL → use `web_extract` to get markdown, save to `raw/articles/`
   - PDF → use `web_extract` (handles PDFs), save to `raw/papers/`
   - Pasted text → save to appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/karpathy-llm-wiki-2026.md`

② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

③ **Check what already exists** — search index.md and use `search_files` to find
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.

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

⑥ **Update overview.md** — revise the living synthesis if the new source
   changes the overall picture (new themes, shifted conclusions, etc.).

⑦ **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in index header
   - Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
   - List every file created or updated in the log entry

⑧ **Post-ingest validation** — critical consistency check:
   - Verify all new `[[wikilinks]]` point to existing pages (run broken link check)
   - Verify all new pages appear in `index.md`
   - Print a change summary: files created, files updated, links added

⑨ **Report what changed** — list every file created or updated to the user.

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

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also `search_files` across all `.md` files
   for key terms — the index alone may miss relevant content.
③ **Read the relevant pages** using `read_file`.
④ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑥ **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
⑦ **Update log.md** with the query and whether it was filed.

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
3. **Log coverage** — source 页面是否有对应的 ingest log 条目

**执行方式：**

```bash
# Agent 可用 execute_code 调用 references/health-check.py 中的函数
WIKI="${WIKI_PATH:-$HOME/wiki}"
python3 "$SKILL_DIR/references/health-check.py" --json
# 或：python3 "$SKILL_DIR/references/health-check.py" --save  # 输出到 wiki/health-report.md
```

也可直接用 `execute_code` 内联调用 `run_health()` 函数获取结构化报告。

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

⑨ **Log rotation** → `check_log_rotation(wiki_path)` — log.md 超过 500 条时
   需轮转：重命名为 `log-YYYY.md`，创建新的空 `log.md`。

**Severity grouping**（报告必须按此顺序分组）:
1. 🔴 Broken links — 功能性错误，必须立即修复
2. 🟠 Orphan pages — 知识孤立，影响可发现性
3. 🟡 Stale content / Contradictions — 信息可能过时，需审核
4. 🟢 Style issues (frontmatter, tag, page size) — 规范问题

**Graph-aware checks**（需要 `graph/graph.json` 存在时才运行）:

⑫ **Phantom hubs** — 被 2+ 页面的 `[[wikilink]]` 引用但页面本身不存在的名称。
   这是强烈的新页面创建信号，按引用数降序排列。

⑬ **Hub stubs** — God nodes（degree > μ+2σ）但正文不足 500 字符。
   高连接度但内容单薄 — 需要充实。

⑭ **Fragile bridges** — 社区间仅 1 条边连接。删除任一端就断联。

⑮ **Sparse pages** — 出链少于 2 条的 wiki 页面（链接密度不足）。

⑯ **Data gaps** — Wiki 无法回答的领域问题，建议补充的源文件。

⑩ **Report findings** with specific file paths and suggested actions, grouped
    by severity above.

⑪ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found`

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
read_file path="$WIKI/log.md" offset=<last 20 lines>
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
- The `raw/assets/` folder holds images referenced via `![[image.png]]`

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
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
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.
- **Run health before lint** — linting an empty or stub file wastes tokens and produces
  misleading results. Always run the health pre-flight check first.
- **Post-ingest validation is not optional** — every ingest must end with a consistency
  check (broken links, index completeness). Skipping it silently introduces decay.
- **Graph inference is expensive** — Pass 2 (semantic) uses LLM calls per page.
  Use `--no-infer` for frequent quick checks; full inference only when the wiki
  has changed significantly (10+ ingests since last build).
- **Phantom hubs are action items, not errors** — when 3+ pages reference `[[Topic]]`
  but no page exists, that's the wiki telling you what to create next.
- **Overview.md is a living document** — update it on every ingest, not just when
  explicitly asked. A stale overview defeats the purpose of having one.
