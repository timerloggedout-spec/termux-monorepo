# Help-wanted LLM selection (current)

## What is NOT used

| Thing | Why |
|-------|-----|
| **Legacy `model-router` residual/fallback chain** | Pre-FELO static Gemini→OR list; soft-budget “fallback” era |
| **MoneyBall / 3L0 as runtime picker** | MoneyBall **scores** providers/agents **after repeated task success** — it does **not** pick the next HTTP model for a single help-wanted comment |
| **HuggingFace as required gate** | Not part of live catalog path |

Help-wanted is **Oversight execute**, not MoneyBall admission (`SCOUT-MISSIONS.md`).

## What IS used

```text
provider_model_catalog.py
  → openrouter + felo + omni /v1/models
  → eligible = :free | zero price | free_trial
  → rank (coder/qwen/deepseek/ox-alpha preference)
  → chat/completions with matching secret
```

| Secret | Provider |
|--------|----------|
| `OPENROUTER_API_KEY` | openrouter |
| `FELO_AI_API` | felo |
| `OMNI_API_KEY` / `OMNIROUTE_API_KEY` | omni |
| OPERATOR PAT | post comment on foreign PR |

Catalog is **evidence**, not promotion. Promotion still follows:

`DISCOVERED → … → REPEATED_SUCCESS → MONEYBALL_SCORED → ACTIVE`

Agent-Identity: Grok (Administrator)
