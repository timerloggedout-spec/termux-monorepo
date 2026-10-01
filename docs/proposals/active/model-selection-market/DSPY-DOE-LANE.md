# DSPY-DOE-LANE (MSM-004 design)

## Role

**Consideration lane** for multivariate DoE / MVT prompt-optimizer experiments.
Affinity: Approxination A/B/C/D + MoneyBall evidence.

**Not** model-router primary. **Not** required for default agent path.

## Why DSPy here

- Structured signatures + metrics fit trading-card + performance-ledger samples
- Optimizer arms map cleanly onto Approxination fixed A/B/C/D treatments
- Keeps free-first: solvers/judges use OPENROUTER free / existing secrets only

## Constraints

| Rule | Detail |
|------|--------|
| Free-only | No paid routes in CI or default arms |
| Dual-gate | Any optimizer artifact PR must pass repo-gate + termux-smoke |
| Observe | Results append to performance ledger; do not auto-mutate production weights |
| Secrets | APPROX_TOKEN / OPENROUTER / etc. stay Actions secrets (#184 names-only) |
| Gate | APPROX-006 formal A/B/C/D smoke remains the cohort entry; DSPy arms feed it |

## Output contract

```text
DSPy run → signatures + metrics → trading card (opt_script) → ledger sample → optional bet settle
```

No silent write into `model-rotation.yaml` soft budgets.

## Implementation note

Runtime extract is a **later** PR (MSM-004). This file is design-only for review.
