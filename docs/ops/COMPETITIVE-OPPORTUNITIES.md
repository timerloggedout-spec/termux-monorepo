# Competitive Opportunities Portfolio

**Purpose:** one decision surface for opportunities the repository can pursue, preserve, or deliberately decline. This portfolio connects competitive outcomes to resource allocation without collapsing unlike economic measures into one score.

The portfolio is a navigation and decision contract. Existing domain ledgers remain the systems of record for their own facts.

## Portfolio lanes

| Lane | What it measures | System of record | Valuation rule |
|---|---|---|---|
| Competitive opportunities | Candidate opportunities, constraints, decision windows, alternatives, and disposition | This portfolio plus linked domain records | Compare feasible alternatives; preserve source and decision evidence |
| Challenge opportunity | Gross first-place award value foregone or at risk | Challenge Opportunity Ledger | Gross first-place award only; no expected-value or win-probability fields |
| Resource opportunity cost | Value of the best feasible alternative use of human/agent capacity that was forgone | Resource-allocation records, once evidenced | Record the alternative, feasibility, time window, and valuation basis; do not substitute investment value |
| Provider opportunity cost | Value of the best feasible alternative use of provider quota, credits, or compute that was forgone | Provider consumption and entitlement evidence | Preserve native units unless an official, scoped conversion exists |
| Repository time investment value | Value assigned to measured time actually invested in repository work | Free-Tier Use Value Board | Measured minutes / 60 × documented valuation rate |
| Paid-equivalent API value | Counterfactual paid list-price equivalent of observed provider/model token usage | Validated provider-call/session evidence plus versioned price records | Exact model/version rate match; input and output priced separately |
| Observed provider cost | Actual billed amount | Provider invoice or authoritative billing export | Never infer from list-price equivalence or quota movement |

## Decision vocabulary

A portfolio entry should include:

- stable opportunity ID and owning lane;
- originating source URL, issue, challenge, provider, or repository record;
- decision window and deadline, when applicable;
- feasible alternatives considered and the selected alternative;
- resource requirements and constraints;
- evidence state (measured, reconstructed, estimated, activity-only, waived, pending, or fault);
- valuation method, unit, currency, and source timestamp;
- decision owner, disposition, and review date.

Use candidate, assessed, committed, realized, expired, or declined for portfolio disposition. These states do not replace domain-specific statuses in the linked ledgers.

## Accounting invariants

1. **Investment value is not opportunity cost.** Investment value prices resources consumed; opportunity cost prices the best feasible alternative use forgone.
2. **Challenge awards stay separate.** The Challenge Opportunity Ledger remains append-only and gross-only under its 1st-place convention. Do not inject challenge EV, win probability, or resource-allocation cost into it.
3. **Provider economics stay evidence-qualified.** Native quota units, paid-equivalent API value, verified free-tier coverage, and observed billing are separate measures.
4. **No synthetic allocation.** Shared provider buckets remain provider/account-level unless a provider exposes an exact consumer key or dispatch-time instrumentation establishes the join.
5. **Unknown is not zero.** Missing usage, rates, billing, or alternative-use evidence remains unavailable with a reason.
6. **No double counting.** A resource event may be referenced by multiple decision views, but its underlying quantity/value is counted once in its authoritative ledger.
7. **Append-only correction.** Where a source ledger is append-only, correct through a superseding record that references the original; never rewrite historical evidence in place.

## Moneyball integration

Moneyball consumes validated, provenance-bearing records from the domain ledgers. It may compare opportunity portfolios, resource allocations, provider performance, and realized outcomes, but it must preserve their units and evidence classes.

The decision layer must expose the source record IDs, source SHA/ref, observation window, model/provider version where relevant, formula/version, and confidence or uncertainty. Derived scores are decision support, not source facts and never an autonomous merge/deploy authorization.

Recommended flow:

Competitive Opportunities → domain ledgers → evidence reconciliation → Moneyball decision views → human disposition

## Current integration points

- Challenge award history: Challenge Opportunity Ledger.
- Repository time and paid-equivalent methodology: Free-Tier Use Value Board.
- Provider-call and experiment evidence: Hex × Agent Team Moneyball Integration.
- Provider consumption and entitlement semantics: Quota Attribution.
- Reconciliation contract: Provider Consumption Reconciliation.

## Acceptance criteria

- Each displayed metric names its authoritative source, unit, window, evidence class, and formula.
- Challenge gross awards, resource opportunity cost, repo time investment value, paid-equivalent API value, verified free-quota coverage, and observed provider cost remain distinct.
- No opportunity cost is calculated without a documented feasible alternative that was actually forgone.
- Missing feeds and provider-level-only measurements are shown as gaps, not zeroes or per-agent estimates.
- Corrections preserve the original record and lineage.
