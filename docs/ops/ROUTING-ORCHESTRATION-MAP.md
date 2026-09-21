# Routing & Orchestration Map (SSOT)

**Updated:** 2026-09-18
**Authority:** Lane 5 (Peer Routing, Context, & Workflows) + llm_api_hub + mcp-hub
**Related:** `docs/schemas/model-rotation.yaml`, `docs/DEPLOYMENT-LANES.md`, `docs/ops/LANE_CONSOLIDATION_SSOT.md`, bifrost-gateway-integration proposal

## Three planes (do not collapse)

```text
┌─────────────────────────────────────────────────────────────┐
│  REVIEW / OPS PLANE (ephemeral GHA)                         │
│  peer-review-orchestrator · agent-continuous-ops · Jules    │
│  model-router → http-llm-invoke (gemini|omni|openrouter|felo)│
└───────────────────────────┬─────────────────────────────────┘
                            │ role prompts / telemetry
┌───────────────────────────▼─────────────────────────────────┐
│  CHAT PLANE                                                 │
│  llm_api_hub (:8787 OpenAI-compat)                          │
│    ├─ wrapper/* → multi-ai-cli (deepseek, colab, …)         │
│    ├─ openrouter/* · openai/* · anthropic/*                 │
│    └─ [evaluation] Bifrost base_url drop-in                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  MCP PLANE                                                  │
│  mcp-hub (Vercel) · github-remote · termux-mcp · android    │
│  [evaluation] Bifrost native MCP gateway                    │
│  github-docker (self-host optional)                         │
└─────────────────────────────────────────────────────────────┘
```

## Who routes what

| Decision | Component | Output |
|----------|-----------|--------|
| triage / review / invoke model pick | `.github/actions/model-router` + `scripts/model_router.py` | provider + model or skip |
| HTTP completion + PR comment | `.github/actions/http-llm-invoke` | omni \| openrouter \| felo |
| Soft Gemini budgets | `gemini-quota-gate` + model-rotation.yaml | skip vs proceed |
| NexusCLI / ADE model calls | `llm_api_hub` or multi-ai-cli | OpenAI-shaped response |
| Tool calling for agents | MCP hosts in `mcp-hub/catalog.json` | tools list |
| Dual-gate promote | `repo_gate.py` + `termux_smoke.py` | pass/fail |

## Hosted vs ephemeral

| Workload | Prefer | Status |
|----------|--------|--------|
| MCP tool serving | Hosted (Vercel mcp-hub, github-remote) | LIVE |
| Review / sweep / Jules | GHA ephemeral | LIVE |
| Free-tier model rotation | GHA + keys in Actions secrets | LIVE |
| High-RPS multi-provider gateway | Self-host or dedicated host (Bifrost eval) | EVALUATION |
| Colab / heavy notebook | External Colab backend | LIVE wrapper |
| Dual-gate | CI + local Termux-compatible | LIVE |

**Do not** move all orchestrations to one always-on host. Secrets concentration and free-tier design argue against it. Optional gateway-backed chat plane is the measured upgrade path.

## Bifrost evaluation contract

1. Forks: `timerloggedout-spec/bifrost_fork`, `bifrost-benchmarking_fork`
2. Catalog status: `evaluation` (not live_verified)
3. Measure with mocker + `benchmark.go` against llm_api_hub / OpenRouter / OX Alpha paths
4. Promote only with dual-gate + recorded `results.json` evidence
5. Never wholesale-merge Bifrost Go workspace into master

## Free-tier hard rules (unchanged)

- Exhaustion path → OpenRouter **free only** (`:free` or zero pricing)
- Never hard-fail CI on quota; graceful skip + comment
- Counters per-branch best-effort (not global RPD)
- Gemini remains primary for best roles until evidence says otherwise

BIUDL. Agent-Identity: Grok (Administrator)
