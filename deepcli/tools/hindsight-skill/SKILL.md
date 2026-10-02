---
name: hindsight-memory-architect
description: Expert agent skill for Hindsight by Vectorize.io across Codespace, Koyeb/Fly.io, and api.hindsight.vectorize.io — with quota rotation, redundancy, and export/import pipelines.
version: 0.2.0
---

# Hindsight Memory Architect

Long-term memory engine for autonomous agents. Hybrid TEMPR retrieval
(Temporal, Embedding, Match-keyword, Parallel-graph, Reasoned) with
contextual consolidation.

## Core operations

1. **Retain** — feed raw context, not pre-summarized strings.
2. **Recall** — RRF-fused parallel search. Query before any git-mutating action.
3. **Reflect** — async consolidation. Produces observations + mental models.

## Three-tier hierarchy (reflect priority)

- **Mental Models** — user-curated pre-computed reflections. `source_query` + `tags`. Refreshed on consolidation or manual trigger.
- **Observations** — auto-consolidated beliefs from >= 2 facts. `proof_count` counts support. Reconciled on new evidence.
- **Raw Facts** — individual `memory_units`. Ground truth, append-only via retain, edited via `hs-facts set-meta`.

## Deployment footprints

### A · Codespace (primary, dev)

- API: `http://localhost:8888` (gemini), `:8889` (openrouter)
- Postgres: pg0 embedded. Config: `/home/vscode/.pg0/instances/hindsight/instance.json`
- Env pin: `HINDSIGHT_BANK_ID=termux-monorepo::primary` must be in `.devcontainer/devcontainer.json` containerEnv
- Launchers: `hs-primary-launch.sh` (:8888), `hs-or-launch.sh` (:8889)
- `/tmp` is ephemeral on stop/start AND rebuild. Tracked git is durable.

### B · Koyeb / Fly.io (cold-start, non-codespace)

Docker image `ghcr.io/vectorize-io/hindsight:latest`. Embedded Postgres.

    docker run -it --pull always --name hindsight --restart unless-stopped \
      -p 8888:8888 -p 9999:9999 \
      -e HINDSIGHT_API_LLM_PROVIDER=gemini \
      -e HINDSIGHT_API_LLM_API_KEY=$GEMINI_KEY \
      -e HINDSIGHT_API_LLM_MODEL=gemini-3.1-flash-lite \
      -e HINDSIGHT_BANK_ID=termux-monorepo::primary \
      -v hindsight-data:/home/hindsight/.pg0 \
      ghcr.io/vectorize-io/hindsight:latest

- Koyeb: service + persistent volume at `/home/hindsight/.pg0`
- Fly.io: `fly volumes create hindsight_data`; `[mounts] source="hindsight_data" destination="/home/hindsight/.pg0"`
- Wake cost 60–90s. Remote clients retry 3x with 30s backoff.

### C · Cloud (api.hindsight.vectorize.io)

- Managed tier. Auth: `Authorization: Bearer $HINDSIGHT_API_KEY`
- No pg0, no volume. Config: `~/.hindsight/config` (mode 600)
- Used as third-tier fallback in the router when codespace + local are unavailable.

## Redundancy + fallback (RoutedHindsightClient)

`deepcli/deepcli/_v1_hindsight_router.py` — three-tier failover:

| Tier | Priority | Trigger to demote |
|------|----------|-------------------|
| Codespace (:8888 local / public URL) | 1 | 402, 429, 500, 502, 503, 504 |
| Cloud (api.hindsight.vectorize.io) | 2 | same code set |
| Local FTS5 (~/.deepcli/bank-local.db) | 3 | never demoted |

- `RESET_AFTER_S=900` — cloud re-probes after 15 min
- `HS_WRITE_MODE=fanout` — write to all reachable targets concurrently
- Env: `HS_LOCAL_URL`, `HS_REMOTE_URL`, `HS_WRITE_MODE`

## Quota rotation

`hs-stack.py` — per-model RPD tracking + headroom-based rotation:

- `limits.json` — probe cache (refreshed hourly). Every model probed with a 1-token call.
- `state.json` — per-model per-day counters keyed by Pacific date. Rebuilt from `llm_requests` via `rebuild-state.py`.
- `pick_next()` — max headroom, ORDER tiebreak. Skips `http=429`.
- `restart_hindsight()` — reads live env from `/proc/<api-pid>/environ` before kill. Preserves keys.
- Reset: 00:00 America/Los_Angeles.

**Per-model daily RPD (Gemini free tier):**

| Model | RPD |
|-------|-----|
| gemini-3.5-flash-lite | 500 |
| gemini-3.1-flash-lite | 500 |
| gemini-flash-lite-latest | 500 |
| gemini-3.7/3.6/3.5-flash, 3-flash-preview | 20 each |

**OpenRouter free:** 50 RPD before $10 lifetime, 1000 after. 20 RPM.

## Bank naming convention

    <project>::<method>::<vendor>::<family>::<model>::<settings>::<role>::<comp>

Primary bank exception: `<project>::primary`

Vendor = who bills (google, openrouter, anthropic).
Family = product line (gemini, qwen, llama).
Settings = tier (standard, flex, free, thinking, lite).

## Export / import (LLM-free)

- `hindsight-admin export-bank <bank> --out file.zip` — documents, memory_units, links, entities, mental_models, config
- `hindsight-admin import-bank <zip>` — re-embeds locally, no LLM re-run
- API: `POST /v1/default/banks/<bank>/transfer/export` returns `operation_id`; poll `/operations/<id>`
- `hs-drain-auto.sh` — DB JSONL primary, API ZIP bonus. Size-validated.
- `hs-parity2` — bidirectional cloud ⇄ codespace ⇄ local
- Git substrate: `memory-bank` branch holds `bank-latest.zip` + `LAST-DRAIN.md`

## Redirects

- `HINDSIGHT_BASE_URL` — client target. Refuses `vectorize.io` for agent writes (`agent_hindsight.py`), always localhost.
- `HINDSIGHT_LOCAL_URL` — codespace `:8888` tunnel target
- `HS_REMOTE_URL` — public codespace HTTPS
- URL cache: `~/.deepcli/cs-hindsight-url.txt`

## Framework skill paths

- Claude Code: `~/.claude/skills/{name}/SKILL.md`
- Codex / Gemini / Cursor: `~/.codex/skills/{name}/SKILL.md`
- Kiro: `~/.kiro/skills/{name}/SKILL.md`
- Factory Droid: `~/.factory/skills/{name}/SKILL.md`

## Python client

    from hindsight_client import Hindsight
    client = Hindsight(base_url="http://localhost:8888")
    client.retain(bank_id="termux-monorepo::primary", content="...", metadata={...})
    hits = client.recall(bank_id="termux-monorepo::primary", query="...", limit=10)
    answer = client.reflect(bank_id="termux-monorepo::primary", query="...")

## CLI

    hindsight-admin export-bank <bank> --out file.zip
    hindsight-admin import-bank file.zip
    memory retain <bank-id> "<context>"
    memory recall <bank-id> "<query>"
    memory reflect <bank-id> "<topic>"

## Diagnostics

1. Verify SKILL.md path matches framework directory.
2. `curl $HINDSIGHT_BASE_URL/health` → 200
3. `hs-verify` → 11-point PASS/FAIL
4. `hs-dash` → dashboard with bank/observation/quota sections
5. On 429: `hs-stack rotate` picks next headroom model
6. On 402: cloud tier exhausted — `hs-stack` demotes to codespace, then FTS5
7. Config tokens in `~/.hindsight/config` — no trailing whitespace

## Termux-monorepo integration

- Primary bank: `termux-monorepo::primary`
- MVT lanes: `termux-monorepo::mvt::<vendor>::<family>::<model>::<settings>::<role>::<comp>`
- DeepAgent reach: `agent_hindsight.retain_async()` — sync HTTP, env-gated, refuses cloud URLs
- Lifecycle tools: `deepcli/tools/hindsight-lifecycle/`
- Dashboard: `dashboard/sections/*.sh`, observers only, verified by `dashboard/verify.sh`
- Skill: `deepcli/tools/hindsight-skill/SKILL.md`

## References

- https://github.com/vectorize-io/hindsight-skills
- https://vectorize.io
- https://www.getclaudeskills.com/skills/hindsight-memory-architect-vectorize-io
