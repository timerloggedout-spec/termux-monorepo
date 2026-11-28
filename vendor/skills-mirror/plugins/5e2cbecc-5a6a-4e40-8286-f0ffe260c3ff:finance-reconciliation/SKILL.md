---
name: "finance-reconciliation"
department: "finance-controller"
description: "Use when reconciling a balance-sheet account during the close cycle. Covers sub-ledger to GL ties, intercompany eliminations, exception triage, and audit-ready documentation. Do not use for journal-entry construction (use finance-journal-entries) or close orchestration (use finance-close-checklist)."
version: 1
triggers:
- "reconciliation"
- "recon"
- "balance sheet substantiation"
- "BS sub"
- "sub-ledger"
- "GL tie"
- "intercompany"
- "close"
---

# Finance Reconciliation

## Purpose

Produce an audit-ready reconciliation of a balance-sheet account. Reconciliation ties the GL balance to its source of truth (sub-ledger, bank statement, third-party confirmation, schedule), explains every difference, and produces evidence that survives auditor review.

This skill is the foundation that every other Controller skill builds on. A close cycle that doesn't reconcile is a close cycle that hasn't closed.

## Scope Constraints

- Produces analysis and documentation; does not post journal entries.
- Covers balance-sheet account reconciliation; does not cover P&L variance analysis (use FP&A's variance-analysis skill).
- Does not opine on recognition policy — the input is an existing posted balance.

## Inputs

- Account number, name, and entity (and, if multi-entity, the consolidation perspective)
- Period-end date
- GL trial balance for the account (current period, prior period)
- Sub-ledger or source-of-truth detail (AR aging, AP aging, fixed-asset register, payroll register, bank statement, schedule, etc.)
- Prior-period reconciliation (to roll-forward)
- Any known reconciling items (in-transit, timing differences, manual entries pending)

## Input Sanitization

All inputs are read-only artifacts. No user-supplied values are interpolated into commands or file paths. Account identifiers are validated against the chart of accounts before use.

## Procedure

### Progress Checklist
<!-- Track completion across compaction boundaries -->
- [ ] Step 1: Establish the GL Balance and the Source-of-Truth Balance
- [ ] Step 2: Compute the Variance and Categorize
- [ ] Step 3: Roll Forward From Prior Period
- [ ] Step 4: Investigate and Document Reconciling Items
- [ ] Step 5: Triage Exceptions
- [ ] Step 6: Conclude and Sign Off

### Step 1: Establish the GL Balance and the Source-of-Truth Balance

Pull the GL balance for the account at period-end. Pull the corresponding source-of-truth balance:
- AR control → AR sub-ledger aging total
- AP control → AP sub-ledger aging total
- Cash → bank statement ending balance + outstanding deposits − outstanding checks
- Fixed assets → FA sub-ledger NBV
- Accrued payroll → payroll register accrual schedule
- Schedule-supported accounts → the schedule

Record both with their as-of timestamp and source identifier (report name, run date, file hash).

### Step 2: Compute the Variance and Categorize

Variance = GL balance − source-of-truth balance.

Categorize the variance:
- **Zero** — proceed to Step 3 (still verify roll-forward).
- **Material under tolerance** — proceed; document the threshold rule used.
- **Material over tolerance** — flag as exception; continue but mark for Step 5.

Materiality thresholds follow the firm's reconciliation policy (typically the lower of $X or Y% of the balance). Cite the policy.

### Step 3: Roll Forward From Prior Period

Reconcile this period's balance to the prior period's reconciled balance:

`Prior reconciled balance + activity (debits − credits) = Current GL balance`

Source the activity from the GL detail for the period. If the roll-forward doesn't tie, the reconciling items in Step 4 must explain the gap.

### Step 4: Investigate and Document Reconciling Items

For each reconciling item between GL and source-of-truth, document:
- **Description** — what it is in plain English
- **Amount** — debit or credit, with sign
- **Origin** — when and why it arose (in-transit, timing, error, manual entry)
- **Disposition** — clears next period (with expected date), requires JE (with proposed entry), or carry-forward (with rationale)
- **Owner** — who is accountable for clearing it

### Step 5: Triage Exceptions

For any item categorized as "exception" in Step 2 or any item without a clear disposition in Step 4:
- Escalate per the firm's exception policy (typically Controller for items > threshold X, CFO for items > threshold Y).
- Propose a path to resolution (investigate, post adjusting JE, accept and document, restate prior period).
- Note the audit implication if the exception persists past close +N.

### Step 6: Conclude and Sign Off

Write the reconciliation memo (see Output Format). Attach evidence references. Mark preparer / reviewer / approver per the segregation-of-duties policy.

> **Compaction resilience**: If context was lost during a long session, re-read the Inputs section to reconstruct what account is being reconciled, check the Progress Checklist for completed steps, then resume from the earliest incomplete step.

## Handoff

- If reconciling items require new journal entries, hand off to **finance-journal-entries** to construct the entries with proper coding.
- If exceptions reveal a systemic recognition issue (e.g., revenue cut-off pattern), hand off to the Controller's main deliberation thread for a recognition-policy review.
- If exceptions reveal a control deficiency, emit a cross-council handoff to the Auditor specialist (or, if external, route to the engagement team).

## Output Format

```markdown
# Account Reconciliation: [Account] — [Period]

## Header
- **Account:** [number] [name]
- **Entity:** [entity]
- **Period:** [period-end date]
- **GL Balance:** [amount] (source: [report], pulled [timestamp])
- **Source-of-Truth Balance:** [amount] (source: [report], pulled [timestamp])
- **Variance:** [amount] ([percent of balance])
- **Materiality Threshold:** [amount] (per [policy reference])

## Roll-Forward
| Item | Amount |
|------|--------|
| Prior reconciled balance | [amount] |
| + Debits during period | [amount] |
| − Credits during period | [amount] |
| = Expected current balance | [amount] |
| Actual current GL balance | [amount] |
| Roll-forward variance | [amount] |

## Reconciling Items
| # | Description | Amount | Origin | Disposition | Owner |
|---|-------------|--------|--------|-------------|-------|
| 1 | ... | ... | ... | clears [date] / JE proposed / carry-forward | ... |
| ... | ... | ... | ... | ... | ... |
| **Total** | | [sum] | | | |

## Exceptions
| # | Description | Amount | Escalation | Path to Resolution |
|---|-------------|--------|------------|--------------------|
| ... | ... | ... | ... | ... |

## Conclusion
- [ ] GL ties to source-of-truth within materiality, or all variances are explained as reconciling items
- [ ] Roll-forward ties to prior period
- [ ] All exceptions have an owner and a path to resolution
- [ ] Evidence retained at: [path / link]

**Preparer:** [name] [date]
**Reviewer:** [name] [date]
**Approver:** [name] [date]
```

## Quality Checks

- [ ] GL and source-of-truth balances both have explicit timestamps and source identifiers
- [ ] Variance is computed and compared to the firm's materiality threshold (with policy citation)
- [ ] Roll-forward arithmetic ties (prior + activity = current); any gap is fully explained by reconciling items
- [ ] Every reconciling item has an owner and a disposition (not just a description)
- [ ] Exceptions over threshold are escalated per policy
- [ ] Evidence references are paths or links auditors can follow, not "see file"
- [ ] Preparer ≠ reviewer ≠ approver where SoD policy requires three roles

## Evolution Notes
<!-- Observations appended after each use -->
