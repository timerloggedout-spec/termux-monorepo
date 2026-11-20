---
title: "🗺️ SYSTEM MAP"
tags: [map, projects, workspaces, data-stores]
date: 2026-07-18
---

Every project, workspace, and data store, with one‑line purpose.

## Projects
- **`deepcli`** — DeepSeek API CLI (auth, history, send, export)
- **`deepcli-tui`** — Textual TUI dashboard for session browsing
- **`deepseek-cli`** — Puppeteer browser automation (deepseek.js, upload, expert mode)
- **`cli-synthegration`** — Conversation synthesis: indexing, provenance, branching, codex
- **`termux-multi-agent`** — Parallel agent refactoring with orchestration & telemetry
- **`synthegration-cli`** — Rust CLI wrapper (cargo build)
- **`harmonizer-prod_cli`** — ETL pipeline (shell+YAML)
- **`harmony_hub`** — Registry, utility belt, accounts
- **`archwiz`** — Core toolchain: archaeologist, oracle, context builder, dispatch

## Workspaces
- **`workspace/cedar_forge`** — CEDARscript compression & executor
- **`workspace/llm_map`** — LLM mapper, function index, AST, forensics
- **`workspace/maxc`** — MaxC language compiler (Rust)
- **`workspace/scripts`** — Enforcement & hierarchy
- **`workspace/compression_sandbox`** — CedrLang experiments

## Data Stores
- **`~/.deepcli/session_store/`** — 408 full‑message JSONs with thinking_content
- **`~/synthegration_exports/`** — 344 export dirs with manifests & session.json
- **`cli-synthegration/codex/codex_index.json`** — 31K pointers, 14K unique hashes
- **`cli-synthegration/workspace/provenance/comprehensive_provenance.json`** — file→session mapping (726 files)
- **`workspace/llm_map/llm_index_compact.jsonl`** — 8K files, 409 AST‑enriched
- **`workspace/llm_map/func_index.jsonl`** — 1.4K function/class definitions
- **`workspace/llm_map/file_graph.json`** — 135 files, 158 dependency edges
- **`archwiz/pointer_index.json`** — 14K code block hashes
- **`archwiz/lexicon.db`** — 19K extracted terms
- **`termux-multi-agent/local_repo.db`** — sessions, messages, FTS

See [[DATA_STORES]] for full details.
