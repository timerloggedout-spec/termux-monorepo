# OpenRouter free catalog

## Sources (consolidated)

| Surface | Path | Cadence |
|---|---|---|
| Runtime poll | `scripts/model_router.py` → `fetch_openrouter_free_models*` | Per Actions routing decision (1h cache under `/tmp/model-router`) |
| Snapshot poll | `scripts/poll_openrouter_free_catalog.py` | Daily workflow + manual dispatch |
| Snapshot artifact | `docs/schemas/openrouter-free-catalog.json` | Written by poller; PR on drift |
| Policy matrices | `docs/schemas/llm-leaderboard-matrix.yaml`, `docs/schemas/model-rotation.yaml` | Operator/PR updates |
| Peer list | `.github/connectors/llm-peers.yaml` | Operator/PR updates |
| Provider registry | `.github/connectors/llm_providers.yaml` | Operator/PR updates |

## Free rule (2026-08-23)

A model is free if **either**:

1. `id` ends with `:free`, **or**
2. `pricing.prompt == 0` and `pricing.completion == 0` (covers `stealth/ox-alpha`)

`require_free_suffix: true` was retired in `llm-peers.yaml` for this reason.

## Secrets

| Secret | Provider |
|---|---|
| `OPENROUTER_API_KEY` | OpenRouter (required for peer invoke) |
| `FELO_AI_API` | Felo OpenAPI (`https://openapi.felo.ai/api/v1`); alias docs also mention `FELO_API_KEY` |

## OX Alpha

- Model id: `stealth/ox-alpha`
- Context: 1 048 576
- Pricing: free preview on OpenRouter
- Roles: triage / review / invoke preferred fallback

Workflow: `.github/workflows/openrouter-free-catalog-sync.yml`
