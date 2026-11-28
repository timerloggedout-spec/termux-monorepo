---
name: "finance-journal-entries"
department: "finance-controller"
description: "Use when constructing a GAAP/IFRS journal entry from facts. Covers debit/credit selection, account coding, sub-ledger impact, and supporting memo. Do not use for reconciliation (use finance-reconciliation) or close orchestration (use finance-close-checklist)."
version: 1
triggers:
- "journal entry"
- "JE"
- "posting"
- "accrual"
- "prepaid"
- "reclass"
- "reversing entry"
- "debit"
- "credit"
- "account coding"
- "sub-ledger"
---

# Finance Journal Entries

## Purpose

Construct a GAAP- or IFRS-compliant journal entry from a transaction or event. The deliverable is a posting-ready entry — full account coding, balanced amounts, reversal logic, and a supporting memo that an auditor can re-perform without follow-up questions.

## Scope Constraints

- Produces the journal entry, supporting memo, and pre-post review notes; does not actually post to the GL.
- Covers single-event JE construction; does not orchestrate the close cycle (use finance-close-checklist) or reconcile balances (use finance-reconciliation).
- Does not opine on whether the transaction *should* occur — the input is a transaction or event whose accounting treatment is being captured.

## Inputs

- Transaction description (parties, amounts, currency, effective date)
- Underlying contract or supporting document reference
- Entity, location, department, and any required dimensions
- Applicable accounting standard (GAAP or IFRS) and the firm's accounting policy
- Prior treatment of similar transactions (if any) for consistency
- Period (open / closed / pending) and intended posting date

## Input Sanitization

All inputs are read-only artifacts. No user-supplied values are interpolated into commands or file paths. Account numbers are validated against the chart of accounts and entity codes against the entity master before use.

## Procedure

### Progress Checklist
<!-- Track completion across compaction boundaries -->
- [ ] Step 1: Identify the Transaction and Applicable Standard
- [ ] Step 2: Determine Debit and Credit Accounts with Full Coding
- [ ] Step 3: Compute Amounts (Including FX Translation)
- [ ] Step 4: Determine Recurring / Reversing / One-Time and Reversal Date
- [ ] Step 5: Draft Supporting Memo with Citations
- [ ] Step 6: Pre-Post Review

### Step 1: Identify the Transaction and Applicable Standard

State the transaction in one paragraph: parties, economic substance, effective date, amount, currency. Identify the controlling standard with a specific subsection cite (e.g., ASC 606-10-25-1, ASC 842-20-25-1, IFRS 15.31, IFRS 16.22). If multiple standards interact (e.g., revenue + financing component), cite each.

### Step 2: Determine Debit and Credit Accounts with Full Coding

For every line, provide full coding:
- Entity
- Location
- Department / cost center
- Account number and name
- Sub-ledger reference (customer, vendor, asset, project) where applicable
- Any custom dimensions per the firm's COA

Use the natural-balance side (debit for assets/expenses, credit for liabilities/equity/revenue) unless deliberately reversing. Note whether each line hits a sub-ledger control account.

### Step 3: Compute Amounts (Including FX Translation)

Compute amounts gross or net per the standard's measurement rule. For foreign-currency transactions, apply ASC 830 (or IAS 21):
- Transaction date spot rate for non-monetary items at initial measurement
- Period-end rate for monetary items at remeasurement
- Cumulative translation adjustment (CTA) routed to OCI for translation of foreign operations

Confirm debits = credits before proceeding. Show the arithmetic.

### Step 4: Determine Recurring / Reversing / One-Time and Reversal Date

Classify the entry:
- **One-time** — single posting; no reversal
- **Reversing** — accrual or estimate reversed in the next period (specify reversal date)
- **Recurring** — same template posts each period (specify cadence)
- **Adjusting** — corrects a prior posting (cite the original JE reference)

### Step 5: Draft Supporting Memo with Citations

Memo template:
- **Background** — one paragraph on the transaction
- **Accounting analysis** — apply the cited standard to the facts
- **Conclusion** — the recognition / measurement decision
- **Journal entry** — reproduce the JE inline
- **Evidence** — pointers to contract, invoice, schedule, or third-party confirmation

### Step 6: Pre-Post Review

Verify:
- Debits = credits (to the cent)
- Period is open and matches the intended posting date
- Reversal date (if any) lands in an open period
- Sub-ledger impact is intended (control account moves with sub-ledger)
- Trial-balance roll-forward direction is correct (no sign-flip surprises)

> **Compaction resilience**: If context was lost during a long session, re-read the Inputs section to reconstruct the transaction, check the Progress Checklist for completed steps, then resume from the earliest incomplete step.

## Handoff

- If the entry resolves a reconciling item, hand back to **finance-reconciliation** so the recon document references the new JE.
- If the entry is part of a close-cycle accrual run, hand back to **finance-close-checklist** for inclusion in the close package.
- If the underlying recognition decision is contested or sets new policy, escalate to the Controller's main deliberation thread for a recognition-policy review.

## Output Format

```markdown
# Journal Entry: [Short Title] — [Period]

## Header
- **Entity:** [entity]
- **Period:** [period — and posting date]
- **Standard:** [ASC / IFRS cite — section and paragraph]
- **Type:** [one-time / reversing (reversal date) / recurring (cadence) / adjusting (original JE ref)]
- **Currency:** [currency; FX rate and source if non-functional]

## Lines
| # | Entity | Location | Dept | Account | Sub-Ledger | Debit | Credit | Description |
|---|--------|----------|------|---------|------------|-------|--------|-------------|
| 1 | ... | ... | ... | ... | ... | [amt] | | ... |
| 2 | ... | ... | ... | ... | ... | | [amt] | ... |
| **Totals** | | | | | | **[sum]** | **[sum]** | |

## Reversal
- **Reverse:** [yes / no]
- **Reversal date:** [date or N/A]

## Supporting Memo
**Background:** [one paragraph]
**Accounting analysis:** [apply cited standard to facts]
**Conclusion:** [recognition / measurement decision]
**Evidence:** [contract / invoice / schedule / confirmation pointers]

## Pre-Post Review
- [ ] Debits = credits
- [ ] Period open; posting date confirmed
- [ ] Reversal date (if any) in open period
- [ ] Sub-ledger impact intended
- [ ] Roll-forward direction verified

**Preparer:** [name] [date]
**Reviewer:** [name] [date]
```

## Quality Checks

- [ ] Standard cited at section + paragraph level (not just "ASC 606")
- [ ] Every line has full coding (entity / location / dept / account / sub-ledger)
- [ ] Debits = credits to the cent; arithmetic shown
- [ ] FX translation logic cited (ASC 830 / IAS 21) when applicable
- [ ] Reversal flag explicit; reversal date in an open period
- [ ] Memo has Background / Analysis / Conclusion / Evidence — not free-form
- [ ] Sub-ledger control accounts move in lockstep with their sub-ledgers
- [ ] Preparer ≠ reviewer per SoD policy

## Evolution Notes
<!-- Observations appended after each use -->
