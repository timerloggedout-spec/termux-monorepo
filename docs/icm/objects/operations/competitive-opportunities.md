---
type: object
cluster: operations
universe: live
status: initiated
entity: docs/ops/COMPETITIVE-OPPORTUNITIES.md
verified_at: 2026-11-02
---

# Competitive Opportunities and Economics

This card routes decisions about competitive opportunities and the distinct economic ledgers that support repository Moneyball. The portfolio is an index; domain ledgers remain authoritative for their own records.

## Read when

- Comparing an opportunity against the best feasible alternative use of people, agents, provider quota, or compute.
- Reviewing challenge awards or the Challenge Opportunity Ledger.
- Separating repository time investment value from resource opportunity cost.
- Reviewing paid-equivalent API value, verified free-quota coverage, or observed provider cost.
- Connecting provider consumption evidence to Moneyball decision views.

## Canonical sources

| Surface | Authority |
|---|---|
| docs/ops/COMPETITIVE-OPPORTUNITIES.md | Cross-domain opportunity portfolio and decision vocabulary |
| docs/ops/CHALLENGE-OPPORTUNITY-LEDGER.md | Append-only, gross-only first-place challenge award ledger |
| docs/ops/FREE-TIER-USE-VALUE-BOARD.md | Repository time investment and paid-equivalent API methodology |
| docs/ops/QUOTA-ATTRIBUTION.md | Provider/model/instance attribution and native-unit rules |
| docs/ops/PROVIDER-CONSUMPTION-RECONCILIATION.md | Snapshot-to-event reconciliation and residual findings |
| docs/ops/HEX-MONEYBALL-INTEGRATION.md | Experiment/provider-call evidence and Moneyball data contract |

## First-order impact

**Hits:** opportunity portfolio documentation, challenge/resource/provider economic interpretation, quota reconciliation, and read-only Moneyball reporting.

**Does not hit:** provider polling, credentials, billing APIs, quota admission, runtime model selection, challenge submissions, automated award valuation, or autonomous merge/deploy decisions.

## Accounting rules

Investment value describes resources consumed. Opportunity cost describes the best feasible alternative use forgone. Paid-equivalent API value describes a counterfactual paid price for observed usage. Verified free-quota coverage and observed billing require their own evidence. These values must never be added into one undifferentiated total.

## Human gate

Confirm the source record, unit, time window, evidence state, alternative feasibility, and formula before accepting a portfolio value or Moneyball comparison.
