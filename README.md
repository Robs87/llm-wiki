# LLM Wiki — Hermes Agent Skill

> Build and maintain a persistent, compounding knowledge base as interlinked markdown files.

Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), extended with health checks, knowledge graph visualization, and structured governance.

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki compiles knowledge once and keeps it current. Cross-references are already there. Contradictions have already been flagged.

**Version:** 2.2.0 | **License:** MIT

## Update Summary (v2.2.0)

- `log.md` is now governed as a **reverse-chronological control file**: newest entries first, orientation reads the top of the file, and new entries insert at the top instead of appending to the end.
- `references/build-graph.py` now writes graph/report log entries in **top-insert mode**, matching the live wiki convention.
- `references/lint-scripts.py` now includes **reverse-log-aware rotation helpers**: keep the newest 400 entries in `log.md`, and archive overflow into `log-YYYY.md` by year once the file exceeds 500 entries.
- README / SKILL docs were updated so operational guidance, templates, and lint expectations no longer assume append-only logs.

## What's Inside

### SKILL.md

The core behavioral specification for the agent. Covers:

- **Directory structure** — three-layer architecture (`raw/` → `wiki/` → `SCHEMA.md`)
- **Ingest workflow** — 9-step process with post-ingest validation and domain-specific templates (diary, meeting notes)
- **Query workflow** — synthesize answers from compiled knowledge with citations
- **Health check** — zero-LLM pre-flight structural integrity check
- **Knowledge graph** — two-pass build (deterministic wikilinks + semantic inference) with vis.js visualization
- **Lint** — 16 automated checks including graph-aware analysis (phantom hubs, hub stubs, fragile bridges)
- **Governance** — tag taxonomy, contradiction policy, archive/rotation lifecycle

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
