# LLM Wiki — Hermes Agent Skill

> Build and maintain a persistent, compounding knowledge base as interlinked markdown files.

Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), extended with health checks, knowledge graph visualization, and structured governance.

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki compiles knowledge once and keeps it current. Cross-references are already there. Contradictions have already been flagged.

**Version:** 2.1.0 | **License:** MIT

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
| `lint-scripts.py` | Automated lint functions (orphans, broken links, frontmatter, tags, page size) |

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
