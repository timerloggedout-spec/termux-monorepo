# ITEMS — model-selection-market

**Commit for review = FA-ADE.** Promote/merge only after dual-gate green + task outcome verified.

| ID | Item | Status | Depends | Notes |
|----|------|--------|---------|-------|
| MSM-000 | Proposal packet (docs + schemas + ops card) | **done** | — | Landed #959 squash `5174af0f` |
| MSM-001 | Equal-weight bootstrap | **done** | MSM-000 | `bootstrap.py` |
| MSM-002 | Append-only performance ledger | **done** | MSM-001 | `ledger.py` — observe weights until promote |
| MSM-003 | series \| parallel \| concurrent selector | **done** | MSM-002 | `selector.py` |
| MSM-004 | DSPy-DoE consideration stub | **done** | MSM-000 | `dspy_doe.py` — not default router |
| MSM-005 | Cards + bets + graph stub | **done** | MSM-002, MSM-003 | `market.py` |
| MSM-006 | Live catalog join (observe) | **done** | MSM-001 | `catalog_join.py` — OR snapshot + dict; free-only; static seed dual-gate path |
| MSM-007 | model_router peer hook | **done** | MSM-002, MSM-003, MSM-006 | `router_peer.py` — observe samples only; weight=1.0 until two cycles |

## Runtime package

```text
scripts/model_selection_market/
  __init__.py
  bootstrap.py      # MSM-001
  ledger.py         # MSM-002
  selector.py       # MSM-003
  dspy_doe.py       # MSM-004
  market.py         # MSM-005
  catalog_join.py   # MSM-006
  router_peer.py    # MSM-007
  cli.py
  test_msm.py
```

```bash
python3 -m scripts.model_selection_market.cli all-demo
python3 -m scripts.model_selection_market.cli join
python3 -m scripts.model_selection_market.cli peers --role triage
python3 -m unittest scripts.model_selection_market.test_msm -v
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

## Non-goals

- Auto-merge without dual-gate (YOLO)
- Paid routes / silent weight mutation
- Secrets in cards
- Wholesale MoneyBall mega-merge
- Promote weights on single sample
