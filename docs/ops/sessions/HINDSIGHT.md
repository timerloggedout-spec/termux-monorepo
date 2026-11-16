# Hindsight — deployment plan and integration contract

Source fork: `timerloggedout-spec/hindsight` (fork of `vectorize-io/hindsight`).
Default branch: `main`. Size: ~758 MB.

## What Hindsight is

Agent memory system with biomimetic memory types (world facts, experiences,
observations, mental models) over PostgreSQL + pgvector. HNSW index, tsvector
full-text, 4-parallel-strategy recall (semantic, BM25, graph, temporal) + RRF
+ cross-encoder rerank. SOTA on LongMemEval.

## The three operations

```

retain(bank_id, content)           — write to memory
recall(bank_id, query, limit=N)    — retrieve candidates
reflect(bank_id, query)            — synthesize an answer from memory

```

## Deployment shapes

| Shape | Min RAM | Notes |
|---|---|---|
| Full API | 1.5 GB / 2 GB rec | Loads BGE embedder (~130 MB) + MiniLM (~90 MB) + ONNX |
| Slim API | 512 MB / 1 GB rec | External embeddings + reranker required |
| Control Plane UI | 128 MB / 256 MB rec | Optional |
| PostgreSQL | 512 MB / 1 GB+ | pgvector required |
| Cloud | 0 | api.hindsight.vectorize.io, usage-based |

**BLU B160V budget: ~400 MB free / ~620 MB swap.** Local full image is not
survivable. Local slim is marginal. Cloud is zero-cost for our usage pattern.

## Integration contract (from dsh.ts)

Cordis plugin, but the shape ports to any agent loop:

```

agent/session-start  ->  seedIfCold        (background git/codebase seed)
agent/pre-step       ->  onPrompt          (recall + inject sourced message)
agent/turn-stopping  ->  onSessionIdle     (write-back completed exchange)
ctx.tools            ->  hindsight_* suite (retain / recall / reflect)

```

**Per-repo, not per-process.** Bank resolved from `session.header.cwd`.
Cached at RuntimeCore level. Same convergence as our `session_store`
(task-hash keyed, one store, per-task identity).

## Python client

```

pip install hindsight-client -U

from hindsight_client import Hindsight
client = Hindsight(base_url="https://api.hindsight.vectorize.io",
api_key="...")
client.retain(bank_id="my-bank", content="...")
client.recall(bank_id="my-bank", query="...", limit=5)
client.reflect(bank_id="my-bank", query="...")

```

High-level class: `hindsight_clients/python/hindsight_client/hindsight_client.py`
(142 KB). Async variants `aretain` / `arecall` / `areflect`.

## Our integration plan

### Phase 1 — PR #881 (merged)

`deepcli/_v1_hindsight.py` (384 lines) — self-contained:
- `HindsightClient` (async httpx, bearer auth, configurable URL/bank/timeout)
- `retain` / `recall` / `reflect` handlers
- `build_hindsight_tools()` returning spec entries with JSON schemas
- Env: `HINDSIGHT_BASE_URL`, `HINDSIGHT_API_KEY`, `HINDSIGHT_BANK_ID`,
  `HINDSIGHT_TIMEOUT_S`

### Phase 2 — wire into deepagent.py

Three insert sites, ~30 lines total:
1. Import `build_hindsight_tools` at module top
2. Append tool specs to `TOOLS` list, conditional on `HINDSIGHT_BASE_URL` set
3. `DISPATCH["hindsight_retain"] = ...` etc.
4. Loop hooks: `recall(task)` before first LLM call, `retain(exchange)` on finish

### Phase 3 — lifecycle hooks (explicit)

```python
async def on_session_start(task):    ...
async def on_pre_step(msgs):         ...
async def on_turn_stopping(msgs):    ...
```

Called at loop boundaries. Phase 2 inlines them; Phase 3 makes them first-class.

Phase 4 — proof run

Task: "Recall the last 3 things you learned about this repo. Do ONE thing
that improves on them. Retain the outcome."

Runtime decision

Hindsight runs remote. BLU runs only hindsight-client (thin HTTP) or
nothing at all — deepagent.py calls the client directly via httpx.

Candidate hosts (no local signup needed, agent-driven when Tasker/Accessibility
are wired):

· Hindsight Cloud (usage-based, free tier available)
· Fly.io (free tier, persistent)
· Your Vercel / Render accounts (already signed up)

Set at runtime via HINDSIGHT_BASE_URL env. Absent = tools return
{"error": "hindsight not configured"}; loop continues unchanged.

File paths (fork, branch main)

· README.md
· hindsight-integrations/coding-agents/README.md
· hindsight-integrations/coding-agents/src/dsh.ts — Cordis plugin
· hindsight-integrations/coding-agents/src/core/runtime.ts — RuntimeCore
· hindsight-integrations/coding-agents/src/core/transcript-dsh.ts
· hindsight-clients/python/hindsight_client/hindsight_client.py
· hindsight-api-slim/README.md
· hindsight-all-slim/README.md
· hindsight-docs/docs/developer/installation.md
· hindsight-docs/docs/sdks/python.mdx
· hindsight-cli/ — Rust CLI

Ports (self-hosted)

· API: 8888
· Control Plane UI: 9999
· MCP endpoint: http://localhost:8888/mcp/{bank_id}/

Bank naming

Default: coding-agent::{gitProject} — one bank per repo, shared across
agents. We adopt: deepagent::{repo-slug} to keep our memory separate from
other tooling.

Reference

· Repo: https://github.com/timerloggedout-spec/hindsight
· Upstream: https://github.com/vectorize-io/hindsight
· Docs: https://hindsight.vectorize.io
· Paper: https://arxiv.org/abs/2512.12818
