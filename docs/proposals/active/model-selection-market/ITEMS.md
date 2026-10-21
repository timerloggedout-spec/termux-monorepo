# ITEMS — model-selection-market

**Commit for review = FA-ADE.** Promote/merge only after dual-gate green + task outcome verified.

| ID | Item | Status | Depends | Notes |
|----|------|--------|---------|-------|
| MSM-000 | Proposal packet (docs + schemas + ops card) | **done** | — | Landed #959 squash `5174af0f` |
| MSM-001 | Equal-weight bootstrap | **done** | MSM-000 | `scripts/model_selection_market/bootstrap.py` |
| MSM-002 | Append-only performance ledger | **done** | MSM-001 | `ledger.py` — observe weights until promote |
| MSM-003 | series \| parallel \| concurrent selector | **done** | MSM-002 | `selector.py` |
| MSM-004 | DSPy-DoE consideration stub | **done** | MSM-000 | `dspy_doe.py` — not default router |
| MSM-005 | Cards + bets + graph stub | **done** | MSM-002, MSM-003 | `market.py` |
| MSM-006 | Provenance-pinned provider research ingestion + deterministic refresh PR lane | **done** | MSM-000, MSM-002 | Q; implementation #1294, generated data #1295 merged; deployed run 39373733705 passed; no runtime activation |
| MSM-007 | Evidence-gated Bayesian/Delphi advisory ranking + dependency-aware Cadence plan | **done** | MSM-006 | Q; #1294 merged; deployed six-task plan verified; 63 focused/workflow tests + 9 legacy tests pass; production weights unchanged |
| MSM-008 | Complete supplied resource matrix + deterministic aggregate implementation search | **done** | MSM-006 | Q; preserve all supplied links as canonical references, reviewed resource registry, offline searchable provider/resource index and existing workflow artifacts; no account activation or expanded publication authority |
| MSM-009 | Scoped read-only GitHub metadata authentication for production collection | **done** | MSM-008 | Q; deployed run 39376417124 failed closed on anonymous GitHub API 403; token only on two fixed commit-metadata URLs, never raw source or provider endpoints; no retry or permission expansion |

| MSM-010 | Official provider catalog + explicit native hub adapters for harvested models | **done** | MSM-006, MSM-009 | Q; Groq, Mistral and Gemini official endpoints; exact-model opt-in admission, no inferred free entitlement or routing-weight mutation; real production-contract regressions |
| MSM-011 | Evidence-backed matrix review attribution and reconciliation tests | **done** | MSM-008 | Q; distinguish submitted reviews, conversation, inline comments, claimed local roles, and authenticated actors; preserve provenance |

| MSM-013 | Diagnose existing Actions provider-secret mappings and execute only a verified no-cost bounded smoke | **done** | MSM-010 | #1321 merged; run 39432211461 verified existing OpenRouter free-tier and exact zero-price model, one synthetic request returned HTTP 429; inference remains unverified, no retry/paid fallback/admission change; 301 pytest + 9 unit contracts |

| MSM-019 | Official-source passive quota manager contracts for 20 canonical provider families | **executing** | MSM-018 (free-provider prioritization) | Metadata + offline parsers only; no polling/account validation/admission change. |

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
