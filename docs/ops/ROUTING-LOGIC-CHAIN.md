# Routing logic chain (optimized)

**Updated:** 2026-09-19

Full multi-lane matrix (waves, Paper2Agent, Bifrost, Mayan):
**`docs/ops/INTEGRATION-GRAPH-MATRIX.md`**

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

Agent-Identity: Grok (Administrator)
