---
title: "⚙️ PIPELINE — Data Flow & Dispatch"
tags: [pipeline, dispatch, ingestion, promotion]
date: 2026-07-18
---

## Overview
Every conversation follows a 6‑phase loop:

1. **Fork** — isolate change in a session branch
2. **ForeSight** — assess impact (`impact_oracle.py`)
3. **Generate** — produce structured diff (`deepcli send`)
4. **Validate** — require PASS verdict (`run_history.jsonl`)
5. **Promote** — timestamped backup + tier move (`promote.py`)
6. **Index** — rebuild maps (`map-build && map-func && fore`)

## Ingestion Flow
\`\`\`
DeepSeek API
  │
  ▼
core.get_history() → _cache_save()
  │
  ├─► ~/.deepcli/session_store/{sid}.json
  │
  └─► dispatch_pipeline.update_all()
        ├─► Export dir: synthegration_exports/{sid}/session.json
        ├─► Lexicon: harvest_session(sid)
        └─► Codex: CodexIndex.index_conversation(sid, msgs)
\`\`\`

## Export & Index Pipeline (batch)
\`\`\`
synthegration_exports/
  │
  ├─► session_digest.py → SESSION_DIGEST.md
  ├─► pointer_index.py → pointer_index.json
  └─► lexicon_harvest.py → lexicon.db
\`\`\`

## Context Scoping Pipeline
\`\`\`
Session ID
  │
  ├─► provenance_api.search(sid) → files touched
  ├─► file_graph expansion → dependency neighborhood
  ├─► token Jaccard similarity → similar files
  ├─► session store → chat messages + code blocks
  │
  └─► context_graph_builder.py → JSON context pack
\`\`\`

## Dispatch Hook (non‑blocking)
`core._cache_save()` calls `dispatch_pipeline.update_all()`:
- **Export:** writes `session.json` into `synthegration_exports/`
- **Lexicon:** incremental term extraction
- **Codex:** adds pointers to `codex_index.json`

All failures are silently caught — user‑facing tools never break.

## See Also
- [[DATA_STORES]] for all index formats
- [[CONTEXT_SCOPING]] for LLM prompt assembly
- [[PROMOTION]] for the FORGE_OVERSIGHT cycle
- [[TOOLS_INDEX]] for every alias & script
