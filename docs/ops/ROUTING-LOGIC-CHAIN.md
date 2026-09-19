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
model_router_bootstrap               catalog-feed/latest.json
  prepends live peers                  (MoneyBall / Scout evidence)
  → model_router.py
      Gemini soft-budget primary
      peers from LIVE eligible + static residual
        │
        ▼
http-llm-invoke / help-wanted-llm-assist
        │
        ▼
invocation telemetry (no secrets)
        │
        ▼
MoneyBall / 3L0   ← scores AFTER repeated success (admission)
```

## Composite action note

`.github/actions/model-router` cannot read `secrets.*` directly. Callers pass:

- `openrouter-api-key: ${{ secrets.OPENROUTER_API_KEY }}`
- `felo-api-key: ${{ secrets.FELO_AI_API }}`
- `omni-api-key: ${{ secrets.OMNI_API_KEY }}`

## Mayan / agile 13-phase

**Not found** under that title in termux-monorepo issues/docs (2026-09-19 search).
Closest sequences: admission ladder in `SCOUT-MISSIONS`; orchestration steps in `AGENT-TEAM-ORCHESTRATION`.
If the Mayan 13-phase issue lives elsewhere, link it.

Agent-Identity: Grok (Administrator)
