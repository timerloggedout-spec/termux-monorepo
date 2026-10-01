# ITEMS — model-selection-market

Thin extract order. Promote only after dual-gate green + task outcome verified.

| ID | Item | Status | Depends | Notes |
|----|------|--------|---------|-------|
| MSM-000 | Proposal packet (MANIFEST + ITEMS + DESIGN + registry row) | **doing** | — | This PR |
| MSM-001 | Equal-weight role table bootstrap from live free catalog → success-matrix seed | todo | MSM-000 | weight=1.0 per role on admit; no public-board authority |
| MSM-002 | Append-only performance ledger (invocation telemetry → bounded aggregates) | todo | MSM-001 | Reuse success-matrix dimensions + provenance; no raw bodies |
| MSM-003 | Explicit series \| parallel \| concurrent selector (decision_engines peer) | todo | MSM-002 | Production default remains series |
| MSM-004 | DSPy-DoE-MVT consideration lane under Approxination affinity | todo | MSM-000, APPROX-006 | Not default router; arms feed A/B/C/D + success matrix |
| MSM-005 | Bets{Itself\|Others\|Job} ledger + trading-card schema + total graph stub | todo | MSM-002, MSM-003 | Observational until two observe cycles + #192-class decision |

## Non-goals (this proposal)

- Wholesale MoneyBall mega-merge (#432 / #682 family remains extract-only)
- Paid OpenRouter routes
- Auto-promote weight changes without observe cycles
- Secrets in cards or graph
- YOLO / YEET / AUTOAPPROVE

## Validation per item

```text
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
# plus item-local tests when runtime code lands
```
