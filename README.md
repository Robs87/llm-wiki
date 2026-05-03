# LLM Wiki — Hermes Agent Skill

> Build and maintain a persistent, compounding knowledge base as interlinked markdown files.

Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), extended with health checks, knowledge graph visualization, and structured governance.

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki compiles knowledge once and keeps it current. Cross-references are already there. Contradictions have already been flagged.

**Version:** 2.2.0 | **License:** MIT

## Update Summary (Human Control Layer)

- Added a **Human Control Layer** for large LLM-compiled wikis: `overview.md`, `maps.md`, `questions.md`, `principles.md`, `decisions.md`, plus `queries/inbox.md` for candidate questions.
- Added a mandatory **return-flow gate** after ingest/query/organizing: update the relevant human-owned entry page only when the big picture, topic map, long-term questions, principles, or concrete decisions change; otherwise record `Human layer: no update` in `log.md`.
- Clarified that `overview.md` is a living synthesis, **not a forced dump**: update it only when the overall picture changes, to keep the human layer readable and actually ownable.
- Added query-value governance: AI captures candidate questions when they meet value criteria; the human calibrates/promotes them instead of letting the LLM decide final knowledge automatically.
- Preserved existing operational improvements: reverse-chronological `log.md`, source-vs-raw separation, health/lint helpers, graph tooling, and post-ingest validation.

## What's Inside

### SKILL.md

The core behavioral specification for the agent. Covers:

- **Directory structure** — three-layer architecture plus Human Control Layer
- **Ingest workflow** — raw faithful capture, wiki compilation, return-flow gate, post-ingest validation, and domain-specific templates (diary, meeting notes)
- **Query workflow** — synthesize answers from compiled knowledge with citations, capture valuable questions into `queries/inbox.md`, and update human-owned pages when judgment changes
- **Health check** — zero-LLM pre-flight structural integrity check
- **Knowledge graph** — two-pass build (deterministic wikilinks + semantic inference) with vis.js visualization
- **Lint** — automated checks including graph-aware analysis (phantom hubs, hub stubs, fragile bridges)
- **Governance** — Human Control Layer, tag taxonomy, contradiction policy, archive/rotation lifecycle

### references/

Standalone Python tools:

| Script | Purpose |
|---|---|
| `health-check.py` | Structural health checks (empty files, index sync, log coverage) — zero LLM calls |
| `build-graph.py` | Knowledge graph builder with NetworkX + Louvain community detection + vis.js HTML output |
| `lint-scripts.py` | Automated lint functions (orphans, broken links, frontmatter, tags, page size, reverse-log rotation check/execute) |

All scripts read `WIKI_PATH` from environment (defaults to `~/Desktop/wiki`).

## Install as Hermes Skill

```bash
# If using hermes-skills-backup:
cd ~/.hermes/skills/research
git clone https://github.com/Robs87/llm-wiki.git llm-wiki
```

## Quick Start

1. Set `WIKI_PATH` in your `~/.hermes/.env`
2. Tell the agent to initialize a wiki for your domain
3. Start ingesting sources — the agent handles the rest

```
"Create a wiki for AI/ML research"
"Ingest raw/papers/attention-is-all-you-need.md"
"What does the wiki say about transformer architecture?"
"Check wiki health"
"Build the knowledge graph"
```

## Comparison with [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent)

This skill incorporates the best ideas from that project (health checks, knowledge graph, post-ingest validation, phantom hub detection) while preserving stronger governance (SCHEMA.md with tag taxonomy, contradiction handling policy, archive/rotation lifecycle, session orientation protocol).

## Credits

- [Andrej Karpathy](https://github.com/karpathy) — original wiki pattern
- [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) — health check, graph, and validation inspiration
