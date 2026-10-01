# ITEMS — model-selection-market

Thin extract order. **Commit for review = FA-ADE.** Promote/merge only after dual-gate green + task outcome verified.

| ID | Item | Status | Depends | Notes |
|----|------|--------|---------|-------|
| MSM-000 | Proposal packet (MANIFEST + ITEMS + DESIGN + schemas + ops card + design docs) | **done (in review)** | — | PR #959 |
| MSM-001 | Equal-weight role table bootstrap from live free catalog → success-matrix seed | todo | MSM-000 | weight=1.0 per role on admit |
| MSM-002 | Append-only performance ledger (invocation telemetry → bounded aggregates) | todo | MSM-001 | Reuse success-matrix dimensions |
| MSM-003 | Explicit series \| parallel \| concurrent selector (decision_engines peer) | todo | MSM-002 | Production default = series |
| MSM-004 | DSPy-DoE-MVT consideration lane under Approxination affinity | todo | MSM-000, APPROX-006 | Not default router |
| MSM-005 | Bets{Itself\|Others\|Job} ledger + trading-card runtime + total graph stub | todo | MSM-002, MSM-003 | Observational until promote rule |

## Packet files (MSM-000)

- README.md, MANIFEST.md, ITEMS.md, DESIGN.md
- EQUAL-WEIGHT-SEED.md, SELECTION-MODES.md, PERFORMANCE-LEDGER.md
- DSPY-DOE-LANE.md, GRAPH.md
- schemas/trading-card.schema.json, schemas/bet-ledger.schema.json
- docs/ops/MODEL-SELECTION-MARKET.md
- registry.yaml row

## Non-goals

- Wholesale MoneyBall mega-merge
- Paid OpenRouter routes
- Auto weight mutation without observe cycles
- Secrets in cards
- Merge without dual-gate (that is YOLO)

## Validation

```text
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```
