---
title: "🪄 ArchW1z Ecosystem – Home Dashboard"
tags: [dashboard, index, map]
date: 2026-07-18
---

## Quick Navigation
- [[ARCHITECTURE_OVERVIEW]] — every project, workspace, and data store
- [[DATA_STORES]] — authoritative map of all indices and databases
- [[PIPELINE]] — how data flows from API to prompt
- [[TOOLS_INDEX]] — every alias, script, and command
- [[CONTEXT_SCOPING]] — building role‑optimised LLM prompts
- [[PROMOTION]] — FORGE_OVERSIGHT & Time Loop Accelerator
- [[QUICKSTART]] — one‑page guide for new sessions

## Quick Commands
| Alias | What it does |
|-------|-------------|
| `deepcli send` | Send prompt to DeepSeek API |
| `tui` | Interactive session browser |
| `archaeo [file]` | File provenance & lifecycle |
| `oracle [file]` | Shockwave impact analysis |
| `promote` | Promotion protocol enforcement |
| `map-build` | Rebuild LLM index + AST |
| `map-func` | Extract function definitions |
| `fore` | ForeSight metrics |
| `funcfind [q]` | Search function index |
| `dep [file]` | Dependency tree |
| `workflow` | Quick reference card |

## Projects
| Project | Purpose |
|---------|---------|
| `deepcli` | DeepSeek API CLI |
| `deepcli-tui` | Textual TUI for sessions |
| `deepseek-cli` | Puppeteer browser automation |
| `cli-synthegration` | Conversation synthesis, indexing, provenance |
| `termux-multi-agent` | Parallel agent refactoring |
| `synthegration-cli` | Rust CLI wrapper |
| `harmonizer-prod_cli` | ETL pipeline |
| `harmony_hub` | Registry, utility belt |
| `archwiz` | Core toolkit & docs |

## Data Stores at a Glance
| Store | Location | Size |
|-------|----------|------|
| Session store | `~/.deepcli/session_store/` | 408 JSONs, 87 MB |
| Export dirs | `~/synthegration_exports/` | 344 dirs |
| Codex index | `cli-synthegration/codex/codex_index.json` | 31K pointers |
| Provenance | `workspace/provenance/comprehensive_provenance.json` | 726 files |
| True versions | `workspace/provenance/true_versions.json` | 732 files |
| Pointer index | `archwiz/pointer_index.json` | 14K hashes |
| LLM index | `workspace/llm_map/llm_index_compact.jsonl` | 8K files |
| Function index | `workspace/llm_map/func_index.jsonl` | 1.4K defs |

## Pipeline
1. **Ingest** — `core.get_history()` → session store
2. **Dispatch** — `dispatch_pipeline.update_all()` → export + lexicon + codex
3. **Index** — `map-build`, `map-func`, `fore`
4. **Scope** — `context_graph_builder.py` → LLM‑ready context pack
5. **Promote** — Fork → ForeSight → Generate → Validate → Promote → Index

See [[PIPELINE]] for details.
