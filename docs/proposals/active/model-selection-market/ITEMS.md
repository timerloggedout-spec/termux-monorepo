# ITEMS — model-selection-market

**Commit for review = FA-ADE.** Promote/merge only after dual-gate green + task outcome verified.

| ID | Item | Status | Depends | Notes |
|----|------|--------|---------|-------|
| MSM-000 | Proposal packet (docs + schemas + ops card) | **done (in review)** | — | PR #959 |
| MSM-001 | Equal-weight bootstrap | **done (in review)** | MSM-000 | `scripts/model_selection_market/bootstrap.py` |
| MSM-002 | Append-only performance ledger | **done (in review)** | MSM-001 | `ledger.py` — observe weights until promote |
| MSM-003 | series \| parallel \| concurrent selector | **done (in review)** | MSM-002 | `selector.py` |
| MSM-004 | DSPy-DoE consideration stub | **done (in review)** | MSM-000 | `dspy_doe.py` — not default router |
| MSM-005 | Cards + bets + graph stub | **done (in review)** | MSM-002, MSM-003 | `market.py` |

## Runtime package

```text
scripts/model_selection_market/
  __init__.py
  bootstrap.py      # MSM-001
  ledger.py         # MSM-002
  selector.py       # MSM-003
  dspy_doe.py       # MSM-004
  market.py         # MSM-005
  cli.py
  test_msm.py
```

```bash
python3 -m scripts.model_selection_market.cli all-demo
python3 -m unittest scripts.model_selection_market.test_msm -v
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

## Non-goals

- Auto-merge without dual-gate (YOLO)
- Paid routes / silent weight mutation
- Secrets in cards
- Wholesale MoneyBall mega-merge
