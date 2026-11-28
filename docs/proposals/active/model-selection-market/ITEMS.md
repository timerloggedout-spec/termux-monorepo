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

| MSM-012 | Paper-only CSV wallet projection from market snapshots | **in_review** | MSM-005 | PR #1470 at `d2778bcc`: read-only stakes/cards/offers projection only; unmerged/undeployed, no balances or settlement engine |
| MSM-013 | Diagnose existing Actions provider-secret mappings and execute only a verified no-cost bounded smoke | **done** | MSM-010 | #1321 merged; run 39432211461 verified existing OpenRouter free-tier and exact zero-price model, one synthetic request returned HTTP 429; inference remains unverified, no retry/paid fallback/admission change; 301 pytest + 9 unit contracts |

| MSM-019 | Official-source passive quota manager contracts for 20 canonical provider families | **done** | MSM-018 (free-provider prioritization) | Implementation validated in #1448; 5 passive parsers, 12 documentation-only, 3 unsupported; current-head promotion/publication receipts in that PR. No new polling/account validation/admission change; 18 live/service-mapping gaps remain explicit. |

| MSM-020 | Official Ollama balance parser and bounded injectable private account transport | **done** | MSM-019 | Official GET balance schema; modern USD pools and legacy percentages/reset timestamps remain distinct. Fixture-only validation; no account calls, inference, polling, paid fallback or runtime admission changes. |

| MSM-022 | Opt-in production Ollama balance service manager with private persistence and source/freshness checks | **done** | MSM-020 | Fixed authenticated HTTPS balance source, explicit credential-selected user/Team scope, bounded no-redirect transport, private exclusive output, reset/period validity and status-only projection. No automatic collection, account identity claim, inference, admission or schedule change. Separate code/mapping readiness from live account validation. |

| MSM-023 | Opt-in private OpenRouter current-key quota service observation | **done** | MSM-022 | Official GET /api/v1/key only; manual trusted-master/private secret pathway, default off. Request counters, monetary key limits and account tier remain separate; private exclusive output and status-only projection. No inference, retries, schedules, key hopping, paid fallback or routing/admission changes. |

| MSM-024 | Batch passive quota management on existing provider catalog responses and operational readiness | **executing** | MSM-019, MSM-023 | Owner-authorized batch: reuse canonical managers and existing responses; expose status only, unknown when no endpoint-specific contract exists. Reconcile Felo daily-credit eligibility separately from the ended OX Alpha preview without duplicating its adapter. No new requests, inference, account/key/terms action, paid fallback, routing/admission or schedule changes. |

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

## MSM-005 paper-accounting extension (proposed)

The existing MSM-005 **done** row covers its cards/bets/graph stub only. The balance/reservation/settlement engine is absent; these are proposed subscopes of that same lane, not a duplicate wagering market or new MSM-012. [Proposal](PAPER-WALLET-ACCOUNTING.md) · [cross-lane tracking](../termux-agentic-hub/RESEARCH-WALLET-TRACKING.md).

Owning extension issue: [wallet / #1521](https://github.com/timerloggedout-spec/termux-monorepo/issues/1521).

| Scope | Status | Depends | Acceptance / issue |
|---|---|---|---|
| MSM-005.A | posted / Todo | MSM-005 existing event/market model; proposal review | [MSM-005.A / #1526](https://github.com/timerloggedout-spec/termux-monorepo/issues/1526): Paper-point unit, issuance, account/event and settlement contracts. |
| MSM-005.B | posted / Todo | MSM-005.A | [MSM-005.B / #1527](https://github.com/timerloggedout-spec/termux-monorepo/issues/1527): Balance/reserve/settle/release, atomicity, idempotency and recovery. |
| MSM-005.C | posted / Todo | MSM-005.A/B; MSM-012 projection baseline | [MSM-005.C / #1528](https://github.com/timerloggedout-spec/termux-monorepo/issues/1528): Rebuildable versioned CSV views, no import-based minting. |
| MSM-005.D | posted / Todo | MSM-005.A/B/C | [MSM-005.D / #1529](https://github.com/timerloggedout-spec/termux-monorepo/issues/1529): Conservation, overspend, replay, concurrency, restart and CSV proofs. |
