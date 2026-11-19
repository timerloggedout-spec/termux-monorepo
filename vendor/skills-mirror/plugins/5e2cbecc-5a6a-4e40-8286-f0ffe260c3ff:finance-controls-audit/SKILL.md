---
name: "finance-controls-audit"
department: "finance-auditor"
description: "Use when testing a SOX 404 control or designing a controls walkthrough. Covers control description, design effectiveness, operating effectiveness, deficiency evaluation, and remediation. Do not use for evidence-package preparation (use finance-evidence-package — Phase 3+)."
version: 1
triggers:
- "SOX"
- "control"
- "ICFR"
- "walkthrough"
- "control test"
- "design effectiveness"
- "operating effectiveness"
- "deficiency"
- "material weakness"
- "ITGC"
- "COSO"
---

# Finance Controls Audit

## Purpose

Test a SOX 404 control over financial reporting (ICFR) or design a controls walkthrough. The deliverable is a workpaper that documents control description, design effectiveness, operating effectiveness sample testing, exception evaluation, deficiency classification, and remediation plan — to PCAOB AS 2201 standards.

## Scope Constraints

- Produces the control test workpaper and remediation plan; does not assemble the broader evidence package (handoff to future finance-evidence-package).
- Covers ICFR and ITGC controls (PCAOB AS 2201, COSO 2013); does not cover SOC 1 / SOC 2 service-organization audits as primary scope, though SOC reports may be used as evidence under AU-C 402 / AS 2601.
- Does not opine on the underlying account balance — that is the domain of substantive testing or finance-reconciliation.

## Inputs

- Control identifier and description (from the firm's Risk-Control Matrix)
- Risk addressed and the assertion(s) covered (existence, completeness, valuation, etc.)
- COSO component classification (control environment, risk assessment, control activities, information & communication, monitoring)
- Control frequency (per-transaction, daily, weekly, monthly, quarterly, annual)
- Population size and population identifier (system, report, run timestamp)
- Prior-year test results and any deficiencies / remediation status
- Sampling policy (per firm methodology — typically aligned to AICPA AAG-SAM)
- Materiality / significance threshold for the engagement (per firm policy)

## Input Sanitization

All inputs are read-only artifacts. No user-supplied values are interpolated into commands or file paths. Population reports are pulled from authoritative systems and validated against the source (system date, record count, hash) before sampling.

## Procedure

### Progress Checklist
<!-- Track completion across compaction boundaries -->
- [ ] Step 1: Identify the Control (Objective, Risk, COSO Component)
- [ ] Step 2: Assess Design Effectiveness
- [ ] Step 3: Plan Operating-Effectiveness Testing
- [ ] Step 4: Perform Test (Re-Performance / Inquiry / Observation / Inspection)
- [ ] Step 5: Evaluate Exceptions and Classify Deficiency Severity
- [ ] Step 6: Document Remediation Plan

### Step 1: Identify the Control (Objective, Risk, COSO Component)

Document:
- **Control objective** — what the control prevents or detects
- **Risk addressed** — the financial-reporting risk and the affected assertion
- **COSO component** — control environment / risk assessment / control activities / information & communication / monitoring (COSO 2013 framework)
- **Control type** — preventive vs. detective; manual vs. automated vs. IT-dependent; ITGC vs. application
- **Frequency** — drives sample size in Step 3

### Step 2: Assess Design Effectiveness

Walk through the control. Ask: *as designed, does this control actually address the risk?*

- Confirm the control's input, processing, output, and review steps are documented
- Verify the control includes a competent reviewer (segregation of duties)
- Verify the control produces evidence that survives auditor review
- Identify any gap where the design fails to address the risk — design deficiency must be flagged before operating-effectiveness testing wastes effort

### Step 3: Plan Operating-Effectiveness Testing

Determine sample size based on control frequency and the firm's sampling policy (typical guidance):

| Frequency | Population | Sample Size |
|-----------|------------|-------------|
| Annual | 1 | 1 |
| Quarterly | 4 | 2 |
| Monthly | 12 | 2-5 |
| Weekly | 52 | 5-15 |
| Daily | 250 | 15-25 |
| Per-transaction | High | 25-60 (statistical) |

Document sampling method (random, haphazard, systematic, attribute), testing attributes, and pass / fail criteria.

### Step 4: Perform Test (Re-Performance / Inquiry / Observation / Inspection)

Apply procedures consistent with PCAOB AS 1105 / ISA 500 evidence standards:
- **Inquiry alone is insufficient** for design or operating effectiveness
- **Observation** — watch the control execute (limited persuasiveness)
- **Inspection** — examine the documentary evidence (preferred)
- **Re-performance** — independently re-execute the control (most persuasive)

For each sample, document the date executed, attribute(s) tested, result (pass / exception), and evidence reference.

### Step 5: Evaluate Exceptions and Classify Deficiency Severity

For any exception, classify per PCAOB AS 2201 § 62-70:
- **Control deficiency** — control fails to prevent or detect on a timely basis
- **Significant deficiency** — less severe than material weakness but important enough to merit attention by those charged with governance
- **Material weakness** — reasonable possibility of a material misstatement of the financial statements not being prevented or detected on a timely basis

Quantitative evaluation (likelihood × magnitude) and qualitative factors both apply. Compensating controls may mitigate severity but do not eliminate the deficiency.

### Step 6: Document Remediation Plan

For each deficiency:
- **Owner** — accountable executive (and remediator)
- **Remediation action** — specific change to control design, frequency, or evidence
- **ETA** — target implementation date
- **Retest schedule** — when the remediated control will be re-tested
- **Interim mitigation** — compensating procedures while remediation is in flight

> **Compaction resilience**: If context was lost during a long session, re-read the Inputs section to reconstruct the control and population, check the Progress Checklist for completed steps, then resume from the earliest incomplete step.

## Handoff

- If exceptions reveal a misstated balance, hand off to **finance-reconciliation** to substantiate the affected account.
- If exceptions imply a recognition or measurement error, hand off to the Controller's main thread (and **finance-journal-entries** for any correcting entry).
- If the deficiency rises to significant deficiency or material weakness, escalate to the Audit Committee per the engagement charter and route to the future **finance-evidence-package** skill for the audit-deliverable.
- If the deficiency triggers a Section 302 / 906 disclosure or ICFR opinion change, hand off to RegRep / **finance-disclosure-language**.

## Output Format

```markdown
# Control Test Workpaper: [Control ID] — [Period]

## Header
- **Control ID:** [from RCM]
- **Control description:** [...]
- **Control objective:** [...]
- **Risk addressed:** [risk + financial-statement assertion]
- **COSO component:** [...]
- **Control type:** [preventive / detective; manual / automated / IT-dependent; ITGC / application]
- **Frequency:** [...]
- **Period:** [...]

## Design Effectiveness Assessment
- [ ] Input / processing / output / review steps documented
- [ ] Competent reviewer with appropriate SoD
- [ ] Evidence produced and retained
- [ ] No design gap identified
- **Conclusion:** [Effective / Deficient — with rationale]

## Operating-Effectiveness Sample
- **Population:** [size, source, timestamp]
- **Sampling method:** [random / haphazard / systematic / attribute]
- **Sample size:** [n] (per firm policy / AICPA AAG-SAM)
- **Testing attributes:** [list]
- **Procedures applied:** [inspection / re-performance / observation / inquiry — per AS 1105]

| # | Sample Item | Date Executed | Attribute(s) Tested | Result | Evidence Reference |
|---|-------------|---------------|---------------------|--------|--------------------|
| 1 | ... | ... | ... | Pass / Exception | [link] |
| ... | ... | ... | ... | ... | ... |

## Exception Log
| # | Sample # | Description | Root Cause | Compensating Controls |
|---|----------|-------------|------------|----------------------|
| 1 | ... | ... | ... | ... |

## Deficiency Classification (AS 2201)
- **Likelihood:** [reasonable possibility / remote]
- **Magnitude:** [material / not material]
- **Compensating controls considered:** [...]
- **Classification:** [Control deficiency / Significant deficiency / Material weakness]

## Remediation Plan
| Deficiency | Owner | Action | ETA | Retest Date | Interim Mitigation |
|-----------|-------|--------|-----|-------------|-------------------|
| ... | ... | ... | ... | ... | ... |

**Tester:** [name] [date]
**Reviewer:** [name] [date]
**Engagement partner / equivalent:** [name] [date]
```

## Quality Checks

- [ ] Control mapped to a specific COSO component and a specific financial-statement assertion
- [ ] Design effectiveness assessed before operating-effectiveness testing began
- [ ] Sample size justified against firm policy / AICPA AAG-SAM and control frequency
- [ ] Procedures applied beyond inquiry (inspection or re-performance), per AS 1105
- [ ] Every exception has root cause, compensating-controls assessment, and a sample reference
- [ ] Deficiency classification cites likelihood × magnitude analysis per AS 2201
- [ ] Remediation plan has owner, ETA, retest date, and interim mitigation
- [ ] Tester ≠ reviewer ≠ engagement partner per SoD policy

## Evolution Notes
<!-- Observations appended after each use -->
