---
name: "finance-close-checklist"
department: "finance-controller"
description: "Use when orchestrating monthly or quarterly close. Covers the close calendar, sub-ledger cutoffs, accruals, reclass entries, and post-close review. Do not use for individual reconciliations (use finance-reconciliation) or journal-entry construction (use finance-journal-entries)."
version: 1
triggers:
- "close"
- "month-end"
- "quarter-end"
- "close calendar"
- "cutoff"
- "accrual run"
- "recurring entries"
- "post-close"
- "sub-ledger close"
---

# Finance Close Checklist

## Purpose

Orchestrate a monthly or quarterly close from sub-ledger cutoff through period lock. The deliverable is a day-by-day calendar with owners, dependencies, and sign-off gates — the close as a control, not as a scramble.

## Scope Constraints

- Produces the close calendar, accrual schedule, sign-off matrix, and post-close adjustment log; does not post entries (handoff to finance-journal-entries) or perform individual reconciliations (handoff to finance-reconciliation).
- Covers monthly and quarterly close; year-end / annual report close adds disclosure work routed through the RegRep specialist.
- Does not produce variance commentary itself — that handoff goes to finance-variance-analysis.

## Inputs

- Period being closed (month / quarter / year-end), with target close +N
- Sub-ledger inventory (AR, AP, payroll, inventory, fixed assets, intercompany, others)
- Recurring-entry catalog (standing accruals, depreciation, amortization, allocations)
- Consolidation structure (entities, intercompany pairs, currency mix)
- Materiality threshold for post-close adjustments (per firm policy)
- Prior-period close calendar for baseline cadence
- Sign-off matrix (preparer / reviewer / approver per SoD policy)

## Input Sanitization

All inputs are read-only artifacts. No user-supplied values are interpolated into commands or file paths. Entity codes, account numbers, and sub-ledger identifiers are validated against the COA and entity master before use.

## Procedure

### Progress Checklist
<!-- Track completion across compaction boundaries -->
- [ ] Step 1: Confirm Sub-Ledger Cutoffs
- [ ] Step 2: Run Scheduled Accruals and Recurring Entries
- [ ] Step 3: Reconcile Balance-Sheet Accounts (handoff to finance-reconciliation)
- [ ] Step 4: Run Consolidation and Intercompany Eliminations
- [ ] Step 5: Generate Trial Balance and Variance Commentary (handoff to finance-variance-analysis)
- [ ] Step 6: Post-Close Adjustments
- [ ] Step 7: Sign-Off and Lock Period

### Step 1: Confirm Sub-Ledger Cutoffs

For each sub-ledger, confirm cutoff timing and the last entry that will be included:
- **AR** — invoice cutoff, cash-receipts cutoff, credit-memo cutoff
- **AP** — invoice receipt cutoff, expense-report cutoff, manual-vendor cutoff
- **Payroll** — pay-period boundary, accrued-payroll calculation
- **Inventory** — physical / cycle count, in-transit treatment, standard-cost roll
- **Fixed assets** — additions, disposals, depreciation run, impairment review
- **Intercompany** — settlement cutoff, FX rate fix

Document each cutoff with an owner and a cutoff timestamp.

### Step 2: Run Scheduled Accruals and Recurring Entries

Execute the recurring-entry catalog in dependency order:
- Standing accruals (utilities, professional fees, bonus, vacation)
- Depreciation and amortization
- Allocations (overhead, shared services)
- Lease accounting (ASC 842 / IFRS 16) entries
- Reversing entries from prior period (verify they actually reversed)

Cross-check actuals against accrual estimates; flag delta > materiality threshold for true-up.

### Step 3: Reconcile Balance-Sheet Accounts

Hand off each balance-sheet account to **finance-reconciliation**. Track completion in the sign-off matrix. Reconciliation completion is a gate to Step 4.

### Step 4: Run Consolidation and Intercompany Eliminations

- Translate foreign entities (ASC 830 / IAS 21): income statement at average rate, balance sheet at period-end rate, equity at historical, CTA to OCI.
- Eliminate intercompany payables / receivables, intercompany sales / cost, intercompany profit in inventory.
- Confirm intercompany pairs net to zero by entity pair and by account.

### Step 5: Generate Trial Balance and Variance Commentary

Produce the consolidated trial balance and bridge to prior period and to plan. Hand off to **finance-variance-analysis** for commentary on actual-vs-plan and actual-vs-prior. Variance completion is a gate to Step 6.

### Step 6: Post-Close Adjustments

For items identified after the trial-balance freeze:
- Below materiality threshold → log in passed-adjustment schedule
- Above threshold → re-open period, post adjustment via finance-journal-entries, re-run consolidation
- Document each adjustment with owner, root cause, and prevention plan

### Step 7: Sign-Off and Lock Period

Capture sign-offs per the SoD matrix (preparer / reviewer / approver). Lock the period in the GL. Distribute close package: trial balance, variance commentary, sign-off matrix, post-close adjustment log.

> **Compaction resilience**: If context was lost during a long session, re-read the Inputs section to reconstruct the period and sub-ledger inventory, check the Progress Checklist for completed steps, then resume from the earliest incomplete step.

## Handoff

- For each balance-sheet account, hand off to **finance-reconciliation**.
- For each accrual or adjustment entry, hand off to **finance-journal-entries**.
- For variance commentary on the consolidated trial balance, hand off to **finance-variance-analysis**.
- If the close reveals a control failure, emit a cross-specialist handoff to the Auditor specialist (and **finance-controls-audit**).

## Output Format

```markdown
# Close Package: [Period]

## Close Calendar
| Day | Date | Activity | Owner | Predecessor | Status |
|-----|------|----------|-------|-------------|--------|
| -1 | ... | Sub-ledger cutoff communications | ... | — | ... |
| 0  | ... | Period-end | ... | — | ... |
| +1 | ... | AR / AP cutoff confirmations | ... | Day 0 | ... |
| +2 | ... | Accrual run | ... | Day +1 | ... |
| +3 | ... | Recon kickoff | ... | Day +2 | ... |
| ... | ... | ... | ... | ... | ... |
| +N | ... | Period lock | ... | Sign-offs | ... |

## Sub-Ledger Cutoff Confirmations
| Sub-Ledger | Cutoff Timestamp | Owner | Confirmed |
|------------|------------------|-------|-----------|
| AR | ... | ... | [ ] |
| AP | ... | ... | [ ] |
| Payroll | ... | ... | [ ] |
| Inventory | ... | ... | [ ] |
| Fixed Assets | ... | ... | [ ] |
| Intercompany | ... | ... | [ ] |

## Accrual Schedule
| # | Description | Account | Amount | Reverses | Owner |
|---|-------------|---------|--------|----------|-------|
| 1 | ... | ... | ... | ... | ... |

## Sign-Off Matrix
| Step | Preparer | Reviewer | Approver |
|------|----------|----------|----------|
| Sub-ledger cutoffs | ... | ... | ... |
| Accrual run | ... | ... | ... |
| Reconciliations | ... | ... | ... |
| Consolidation | ... | ... | ... |
| Trial balance / variance | ... | ... | ... |
| Period lock | ... | ... | ... |

## Post-Close Adjustment Log
| # | Description | Amount | Above / Below Threshold | Disposition | Root Cause |
|---|-------------|--------|------------------------|-------------|------------|
| 1 | ... | ... | ... | ... | ... |

## Close Conclusion
- [ ] All sub-ledgers closed and reconciled
- [ ] All recurring + accrual entries posted
- [ ] Consolidation and intercompany eliminations clean
- [ ] Trial balance signed off; variance commentary distributed
- [ ] Period locked at: [timestamp]
```

## Quality Checks

- [ ] Every calendar day has an owner and a predecessor (or "—" if independent)
- [ ] All sub-ledger cutoffs have a confirmed timestamp before accrual run starts
- [ ] Recurring-entry catalog ran in dependency order; reversal of prior-period entries verified
- [ ] Every balance-sheet account has a reconciliation in the sign-off matrix
- [ ] Intercompany nets to zero by entity pair and by account
- [ ] Materiality threshold cited (with policy reference) before post-close adjustments are classified
- [ ] Sign-off matrix enforces preparer ≠ reviewer ≠ approver where SoD policy requires three roles
- [ ] Period lock has a timestamp and an approver of record

## Evolution Notes
<!-- Observations appended after each use -->
