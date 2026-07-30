---
title: "📊 DATA STORES"
tags: [data, indices, databases, json, sqlite]
date: 2026-07-18
---

Authoritative map of every JSON/DB file in the ecosystem.

## Session Store
- **Path:** `~/.deepcli/session_store/<sid>.json` (or `primary/`, `secondary/`)
- **Format:** JSON list of message dicts with `role`, `content`, `thinking_content`
- **Writers:** `core.py._cache_save()`, `import_session.py`
- **Readers:** `context_graph_builder.py`, TUI, `dispatch_pipeline.py`
- **Sample query:**
\`\`\`python
import json
msgs = json.load(open('~/.deepcli/session_store/<sid>.json'))
for m in msgs:
    print(m['role'], m['content'][:80])
\`\`\`

## Export Directories
- **Path:** `~/synthegration_exports/<uuid>/`
- **Format:** `manifest.json` (list of code blocks), `session.json` (full history)
- **Writers:** `dispatch_pipeline.update_all()`, `batch_export_all.py`
- **Readers:** `session_digest.py`, `pointer_index.py`, `lexicon_harvest.py`

## Codex Index
- **Path:** `cli-synthegration/codex/codex_index.json`
- **Format:** `{ "pointers": [ { "sid", "ch", "path", "ts" } ] }`
- **Writers:** `CodexIndex.index_conversation()`, `batch_export_all.py`
- **Readers:** `context_graph_builder.py`, `synthegration_index.py`
- **Stats:** 31,397 total pointers, 14,787 unique hashes

## Comprehensive Provenance
- **Path:** `cli-synthegration/workspace/provenance/comprehensive_provenance.json`
- **Format:** `{ file_path: [ { strategy, session, timestamp_utc, snippet, ... } ] }`
- **Writers:** `comprehensive_fast.py`, `batch_update_provenance.py`
- **Readers:** `provenance_api.py`, `forensic_toolchain.py`, `archaeologist.py`
- **Stats:** 726 files, 3 strategies (hash/similarity/time)

## True Versions
- **Path:** `cli-synthegration/workspace/provenance/true_versions.json`
- **Format:** `{ file_path: { hash, session, timestamp_utc } }`
- **Writers:** `sync_provenance_to_true_versions.py`, `true_versions.py`
- **Readers:** `restore_version.py`, `archaeologist.py`, `correlation_scout.py`
- **Stats:** 732 files

## Pointer Index
- **Path:** `archwiz/pointer_index.json`
- **Format:** `{ code_hash: { session_id, references } }`
- **Writers:** `pointer_index.py build`
- **Readers:** `find_orphan_commands.py`, `context_graph_builder.py`
- **Stats:** 14,787 hashes

## LLM Mapper Indices
- **Path:** `workspace/llm_map/`
- **Files:** `llm_index_compact.jsonl` (8,239 files), `func_index.jsonl` (1,437 defs),
  `file_graph.json` (135 files, 158 edges), `ast_snippets.json` (682 files)
- **Writers:** `build_final_all_profile.py`, `func_indexer.py`
- **Readers:** `router_agent.py`, `impact_oracle.py`, `context_graph_builder.py`

## Run History
- **Path:** `termux-multi-agent/run_history.jsonl`
- **Format:** JSONL lines with `target_file`, `verdict`, `timestamp`
- **Writers:** orchestrator, dispatch pipeline
- **Readers:** `impact_oracle.py`, `foresight_collect.py`, `restore_version.py`

## Lexicon DB
- **Path:** `archwiz/lexicon.db`
- **Format:** SQLite with `terms`, `occurrences` tables
- **Writers:** `lexicon_harvest.py scan`, `harvest_session()`
- **Readers:** `dispatch_pipeline.py`
- **Stats:** 19,065 terms

## Agent Repository DB
- **Path:** `termux-multi-agent/local_repo.db`
- **Format:** SQLite with `sessions`, `messages`, `messages_fts`, `run_history`, `nodes`, `edges`
- **Writers:** `orchestrator.py`, `provision_agent.py`
- **Readers:** `context_collector.py`, `dashboard.py`
