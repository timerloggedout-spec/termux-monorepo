# OpenRouter free catalog

## Seed semantics

The file `docs/schemas/openrouter-free-catalog.json` is a **seed** — an initial bootstrap only.

| Event | Behavior |
|---|---|
| **Every router use** | Prefer live OpenRouter `/api/v1/models` poll; free rule applied |
| **Live success** | Refresh 1h process cache; optionally rewrite snapshot when `OPENROUTER_PERSIST_SNAPSHOT=true` |
| **Live fail** | Fall back: 1h cache → seed snapshot → legacy hardcode |
| **Daily workflow** | Always rewrite snapshot from live poll; open PR on drift |

A seed is not a frozen allow-list. It grows/shrinks with the live free set.

## Free rule

A model is free if **either**:

1. `id` ends with `:free`, **or**
2. `pricing.prompt == 0` and `pricing.completion == 0` (covers `stealth/ox-alpha`)

## Sources

| Surface | Path |
|---|---|
| Runtime | `scripts/model_router.py` |
| Snapshot poll | `scripts/poll_openrouter_free_catalog.py` |
| Snapshot artifact | `docs/schemas/openrouter-free-catalog.json` |
| Workflow | `.github/workflows/openrouter-free-catalog-sync.yml` |
| Peers | `.github/connectors/llm-peers.yaml` |
| Providers | `.github/connectors/llm_providers.yaml` |

## Secrets

| Secret | Provider |
|---|---|
| `OPENROUTER_API_KEY` | OpenRouter peer invoke |
| `FELO_AI_API` | Felo OpenAPI |

## Capacity check (2026-08-23)

Live poll: **22** free ids including `stealth/ox-alpha`.
Router selection with Gemini off / OpenRouter on → **`stealth/ox-alpha`** for role=review.
