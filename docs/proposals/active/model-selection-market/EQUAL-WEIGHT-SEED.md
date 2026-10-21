# EQUAL-WEIGHT-SEED (MSM-001 design)

## Policy

On admit of an eligible **free** model into a role (`triage` | `review` | `invoke` | job-class):

```text
weight[role][model_id] = 1.0
confidence = 0.0 if n == 0 else prior rules from model-success-matrix.yaml
```

Public leaderboards (`llm-leaderboard-matrix.yaml`) remain **features**, never initial weights.

## Eligibility (hard)

From existing SSOT — do not fork:

- Free rule: `:free` suffix **or** zero prompt+completion pricing (ox-alpha path)
- Declared capability + policy_enabled
- Quota / soft budgets (`model-rotation.yaml`)
- SHA / branch write confirmation when required

## Seed sources (read-only join)

| Source | Use |
|--------|-----|
| `live_catalog_feed` / catalog-feed/latest.json | current free roster |
| `docs/schemas/model-rotation.yaml` | role matrix + soft_rpd |
| `docs/schemas/model-success-matrix.yaml` | existing ELO priors (confidence ≤ 0.2 if prior-only) |
| Felo / Omni peers | include when live catalog marks free |

## Equal → learned

1. Bootstrap all eligible at 1.0
2. Append outcomes to performance ledger (MSM-002)
3. 3L0 / ELO++ update weights
4. Active routing change only after **two observe cycles** + Issue #192-class ledger decision + dual-gate PR

## Non-goals

- HuggingFace research models: optional, not auto-seeded into production roles
- POE.ai: not in live matrix — do not invent eligibility
- Paid routes: never on exhaustion path
