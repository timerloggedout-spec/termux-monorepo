# SELECTION-MODES (MSM-003 design)

Selector is a **decision_engines peer** (System-1 / schema), not an LLM provider.

## Modes

| Mode | Production default | Behavior | When |
|------|--------------------|----------|------|
| **series** | **yes** | soft budgets → primary → free peer fallback | normal CI / agent path |
| **parallel** | no | sample k eligible free models on same prompt; score after | canary, valley hunt, A/B |
| **concurrent** | no | triage ∥ review ∥ invoke as independent cards; join on Canny/done | multi-role jobs |

## Ordering vs gates

```text
hard eligibility → mode dispatch → model invoke(s) → success-matrix sample → 3L0 update (observe)
                                                                      ↓
                                                         dual-gate / Canny facts hard-block
```

3L0 / MoneyBall **never** sole gate. Latency remains low-value MoneyBall.

## Dense feedback (required)

Every selection return:

- `mode`
- `candidates[]` with model_id + weight + soft_budget_remaining
- `chosen` or `chosen_set` (parallel)
- `routing.reason` / `criteria_matched[]`
- `head_sha` when PR-scoped

## Parallel constraints

- k bounded (policy default ≤ 3 free peers)
- free-only
- aggregate cost counted against soft RPD tables
- results feed performance ledger as separate samples, not one fused fake win

## Concurrent constraints

- Independent cards per role
- Join only on facts (Canny) or explicit job contract
- No silent cross-role weight copy (use trading-card trade if sharing opt scripts)
