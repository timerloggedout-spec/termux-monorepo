---
name: "finance-variance-analysis"
department: "finance-fpa"
description: "Use when explaining actual-vs-plan or actual-vs-prior variance with commentary. Covers volume/price/mix decomposition, run-rate impact, and management commentary. Do not use for forecast revision (use finance-forecast-update — Phase 3+) or close orchestration (use finance-close-checklist)."
version: 1
triggers:
- "variance"
- "actuals"
- "plan"
- "budget"
- "AOP"
- "MD&A"
- "commentary"
- "run rate"
- "bridge"
- "volume price mix"
---

# Finance Variance Analysis

## Purpose

Explain a variance — actual vs. plan, actual vs. prior period, or actual vs. forecast — with decomposition (volume / price / mix / FX / timing), driver attribution, run-rate impact, and management-voice commentary. The deliverable supports management review, board reporting, MD&A drafting, and forecast-revision decisions.

## Scope Constraints

- Produces the variance bridge, decomposition, and commentary; does not revise the forecast (handoff to finance-forecast-update once available) and does not produce SEC disclosure language (handoff to finance-disclosure-language for MD&A drafting).
- Operates on closed actuals — does not opine on whether close-cycle accruals are correctly stated (handoff to finance-reconciliation if a balance is suspect).
- Does not score the forecast process itself; this is a backward-looking analysis.

## Inputs

- Actual results for the period (revenue, gross profit, opex, EBITDA, or the line items in scope)
- Plan / budget figures for the same period (with version identifier — AOP, latest forecast, prior year)
- Prior-period actuals for the same line items (period-over-period basis)
- Source identifiers and timestamps for each data set (system, report, run timestamp)
- Volume, price, and mix detail at the SKU / customer / segment grain where available
- FX rates (period actuals, plan rates) for multi-currency entities
- Materiality threshold for driver call-outs (per firm policy — typically the lower of $X or Y%)

## Input Sanitization

All inputs are read-only artifacts. No user-supplied values are interpolated into commands or file paths. Account, segment, customer, and SKU identifiers are validated against master data before use.

## Procedure

### Progress Checklist
<!-- Track completion across compaction boundaries -->
- [ ] Step 1: Establish Actual, Plan, and Prior with Source Identifiers
- [ ] Step 2: Compute Total Variance and Decompose
- [ ] Step 3: Identify Drivers Above Materiality Threshold
- [ ] Step 4: Run-Rate Impact (One-Time vs. Persistent)
- [ ] Step 5: Draft Management-Voice Commentary
- [ ] Step 6: Tie Back to Forecast-Revision Recommendation

### Step 1: Establish Actual, Plan, and Prior with Source Identifiers

Pull all three data sets:
- Actual results (post-close trial balance or BI tool)
- Plan / budget version (specify AOP, LRP, latest forecast)
- Prior-period actuals (same period last year, or sequential prior period)

For each, record source system, report name, and run timestamp. Confirm consistent units, currency, and segmentation. If currencies differ, note the FX treatment to be applied in Step 2.

### Step 2: Compute Total Variance and Decompose

Total variance = Actual − Comparison (Plan or Prior).

Decompose into buckets that explain the gap:
- **Volume** — units delta × prior-period or plan price
- **Price** — price delta × actual or plan units
- **Mix** — shift between higher/lower-margin SKUs, segments, or customers
- **FX** — translation impact (actual rate vs. plan / prior rate, on the foreign-currency portion)
- **Timing** — pull-forward or push-out vs. the comparison period

Show the arithmetic for each bucket. Buckets must sum to total variance.

### Step 3: Identify Drivers Above Materiality Threshold

For each bucket, identify the specific driver(s) — customer, product, region, channel — that exceed the materiality threshold (`> $X` or `> Y%`). Below-threshold movements are aggregated into "other."

Each driver gets: name, magnitude, sign, and a one-sentence root-cause hypothesis.

### Step 4: Run-Rate Impact (One-Time vs. Persistent)

Classify each material driver:
- **One-time** — non-recurring (litigation settlement, customer one-time order, FX spike)
- **Persistent** — structural (lost customer, new pricing, market-share shift)
- **Timing** — reverses in a future period (specify which period)

Persistent drivers feed Step 6's forecast-revision recommendation.

### Step 5: Draft Management-Voice Commentary

Commentary leads with the operating driver, not the number. Bad: "Revenue was down $4M (8%)." Good: "Revenue declined 8% as the rollout of the new pricing schedule pushed renewals one quarter, with $3M of timing reversal expected in Q3."

One paragraph per major driver. Quote-ready for management review and (with Controller / RegRep partnership) for MD&A.

### Step 6: Tie Back to Forecast-Revision Recommendation

If persistent drivers exceed the firm's forecast-revision threshold, recommend:
- Update full-year forecast (with directional magnitude)
- Trigger re-plan / mid-year re-baseline
- Hold (one-time or timing only)

Hand off the recommendation to the FP&A specialist's main thread (or the future finance-forecast-update skill) for execution.

> **Compaction resilience**: If context was lost during a long session, re-read the Inputs section to reconstruct the period and comparison basis, check the Progress Checklist for completed steps, then resume from the earliest incomplete step.

## Handoff

- If a balance underlying the variance looks misstated, hand off to **finance-reconciliation** before completing commentary.
- If the variance changes the forward outlook materially, hand off the run-rate flag to the FP&A forecast-revision thread (future **finance-forecast-update**).
- If the commentary will appear in MD&A or earnings materials, hand off to RegRep / **finance-disclosure-language** for compliance review (Reg S-K Item 303).

## Output Format

```markdown
# Variance Analysis: [Line Item or Segment] — [Period] vs. [Comparison]

## Header
- **Period:** [period]
- **Comparison basis:** [Plan version / Prior period]
- **Source — Actuals:** [system, report, timestamp]
- **Source — Comparison:** [system, report, timestamp]
- **Materiality threshold:** [amount / percent, per policy]

## Variance Bridge
| Item | Amount |
|------|--------|
| Comparison ([basis]) | [amount] |
| + / − Volume | [amount] |
| + / − Price | [amount] |
| + / − Mix | [amount] |
| + / − FX | [amount] |
| + / − Timing | [amount] |
| + / − Other (sub-threshold) | [amount] |
| **= Actual** | **[amount]** |
| **Total variance** | **[amount] ([percent])** |

## Decomposition Detail
| Bucket | Driver | Amount | Sign | Run-Rate | Root-Cause Hypothesis |
|--------|--------|--------|------|----------|----------------------|
| Volume | [customer / SKU] | ... | +/− | one-time / persistent / timing | ... |
| Price | ... | ... | ... | ... | ... |
| Mix | ... | ... | ... | ... | ... |
| FX | ... | ... | ... | ... | ... |
| Timing | ... | ... | ... | ... | ... |

## Commentary
[One paragraph per material driver, in management voice. Lead with the operating driver, then the number.]

## Run-Rate Flag
- **Persistent drivers:** [list with magnitude]
- **One-time drivers:** [list with magnitude]
- **Timing reversals:** [period and magnitude]

## Forecast-Impact Recommendation
- [ ] No forecast change (variance is one-time or timing only)
- [ ] Update full-year forecast: directional magnitude [+/−$X]
- [ ] Trigger re-plan / mid-year re-baseline

**Preparer:** [name] [date]
**Reviewer:** [name] [date]
```

## Quality Checks

- [ ] Source identifiers and timestamps captured for actuals, plan, and prior
- [ ] Decomposition buckets sum exactly to total variance (arithmetic shown)
- [ ] Volume / price / mix arithmetic is explicit (not just labeled)
- [ ] Materiality threshold cited (with policy reference); below-threshold rolled to "other"
- [ ] Every material driver has a run-rate classification (one-time / persistent / timing)
- [ ] Commentary leads with the operating driver, not the number
- [ ] Forecast-impact recommendation is checked exactly once
- [ ] Preparer ≠ reviewer per SoD policy

## Evolution Notes
<!-- Observations appended after each use -->
