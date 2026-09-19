# Routing logic chain (optimized)

**Updated:** 2026-09-19

```text
live catalogs (OpenRouter + Felo + Omni)
        │
        ▼
live_catalog_feed.py  → eligible free / zero-price / free_trial
        │
        ├──────────────────────────────┐
        ▼                              ▼
model_router.py                  catalog-feed/latest.json
  Gemini soft-budget primary       (MoneyBall / Scout evidence)
  peers from LIVE eligible
  FELO first-class when key set
        │
        ▼
http-llm-invoke / help-wanted-llm-assist
        │
        ▼
invocation telemetry (no secrets)
        │
        ▼
MoneyBall / 3L0   ← scores AFTER repeated success (admission)
                    does NOT pick the next HTTP model by itself
```

## Deprecations

| Old | New |
|-----|-----|
| Frozen Gemini→OR “fallback hierarchy” | Dynamic recovery from unavailable capacity |
| Static ROLE_PEERS only | Live eligible peers + soft limits |
| model-router without Felo | `HAS_FELO` + catalog poll |
| MoneyBall as runtime picker | MoneyBall as post-success scorer |

## Secrets (names only)

`OPENROUTER_API_KEY` · `FELO_AI_API` · `OMNI_API_KEY`/`OMNIROUTE_API_KEY` · `GEMINI_API_KEY`

## Mayan / agile 13-phase

No issue or doc titled **Mayan 13-phase** was found in `termux-monorepo` at this investigation.
Closest control-plane sequences:

- Admission: `DISCOVERED → … → MONEYBALL_SCORED → ACTIVE` (`SCOUT-MISSIONS`)
- Orchestration: classify → split → concurrent → wait → integrate (`AGENT-TEAM-ORCHESTRATION`)

If “Mayan 13-phase” lives in another issue/repo/Drive note, link it and we fold it into this chain.

Agent-Identity: Grok (Administrator)
