---
name: "finance-tax-research"
department: "finance-tax"
description: "Use when answering a federal, state, or international tax question that requires authoritative research. Covers IRC, Treasury Regs, Rev Rul/Proc, case law, and applicable treaty positions. Do not use for tax-provision computation (use finance-provision — Phase 3+)."
version: 1
triggers:
- "tax research"
- "IRC"
- "Treasury Reg"
- "Rev Rul"
- "Rev Proc"
- "PLR"
- "technical advice"
- "case law"
- "tax memo"
- "technical position"
---

# Finance Tax Research

## Purpose

Answer a federal, state, or international tax question with a defensible authority-based memo. The deliverable cites the controlling authorities in hierarchy order, applies them to the facts, reaches a tentative conclusion, and flags any uncertain-tax-position implications under FIN 48 / ASC 740-10.

## Scope Constraints

- Produces a research memo and UTP recommendation; does not compute the tax provision (handoff to finance-provision once available) and does not file a return.
- Covers federal, state, and international (treaty-based) research; does not cover transfer-pricing benchmarking studies (specialized work).
- Does not constitute legal advice; the memo is a working paper for the tax function and outside counsel review.

## Inputs

- The factual question, framed by the requester (with proposed transaction, dates, parties, amounts)
- Applicable jurisdictions (federal / state / foreign)
- Taxpayer entity classification (C-corp, S-corp, partnership, foreign branch, etc.)
- Relevant prior-year returns or positions for consistency
- Any open IRS / state examinations or letter rulings on point
- Authoritative research database access (BNA, CCH, RIA, Westlaw, Lexis)
- Materiality / risk threshold for UTP evaluation (per firm policy)

## Input Sanitization

All inputs are read-only artifacts. No user-supplied values are interpolated into commands or file paths. Citations are verified against the authoritative source (not paraphrased from secondary sources) before being included in the memo.

## Procedure

### Progress Checklist
<!-- Track completion across compaction boundaries -->
- [ ] Step 1: Frame the Issue as a Yes/No or Quantitative Question
- [ ] Step 2: Identify Controlling Authority Hierarchy
- [ ] Step 3: Pull Authorities and Quote Relevant Text
- [ ] Step 4: Apply Each Authority to the Facts
- [ ] Step 5: Identify UTP Implications under FIN 48 / ASC 740-10
- [ ] Step 6: Draft Research Memo

### Step 1: Frame the Issue as a Yes/No or Quantitative Question

Restate the requester's question in research-memo form: a precise yes/no question ("Is the proposed transaction eligible for IRC §351 nonrecognition?") or a quantitative question ("What portion of the §163(j) limitation applies to interest on intercompany debt?"). Vague questions yield vague memos; pin the issue down before pulling authority.

### Step 2: Identify Controlling Authority Hierarchy

Map the issue to the authority hierarchy:

1. **Statute** — Internal Revenue Code (federal), state code, treaty text
2. **Regulations** — Treasury Regulations (final > temporary > proposed)
3. **Revenue Rulings** — IRS published interpretive guidance
4. **Revenue Procedures** — IRS procedural guidance
5. **Case law** — Tax Court, district court, circuit court, Supreme Court (note jurisdiction)
6. **Private Letter Rulings / TAMs** — non-precedential but instructive
7. **Secondary sources** — BNA portfolios, CCH explanations, treatises (citable for context, not authority)

Note where authorities conflict. Higher-tier authority controls.

### Step 3: Pull Authorities and Quote Relevant Text

For each authority that bears on the issue:
- Full cite (e.g., IRC §351(a); Treas. Reg. §1.351-1(a)(1); Rev. Rul. 2003-51, 2003-1 C.B. 938)
- Quote the operative text verbatim (not paraphrased)
- Note the date adopted or modified, and any subsequent guidance

### Step 4: Apply Each Authority to the Facts

For each authority, apply it to the taxpayer's facts:
- What the authority requires / permits / prohibits
- How the facts satisfy or fail each prong
- Where the facts are ambiguous, identify the assumption and flag it

Reach a tentative conclusion only after all bearing authorities have been applied.

### Step 5: Identify UTP Implications under FIN 48 / ASC 740-10

If the conclusion involves an uncertain position:
- Apply the two-step FIN 48 test: (a) more-likely-than-not (>50%) recognition threshold, (b) measurement at the largest amount > 50% likely of being realized.
- If uncertain → recommend UTP reserve and quantify
- Flag whether the position requires Schedule UTP disclosure (taxpayer size threshold)

### Step 6: Draft Research Memo

Memo structure: **Issue / Conclusion / Authorities / Analysis / UTP Implication**.

Memo is the workpaper of record; archive with full cite list and quoted authority text.

> **Compaction resilience**: If context was lost during a long session, re-read the Inputs section to reconstruct the question and jurisdiction, check the Progress Checklist for completed steps, then resume from the earliest incomplete step.

## Handoff

- If the conclusion drives a current- or deferred-tax computation, hand off to the future **finance-provision** skill for ASC 740 workpaper preparation.
- If the position triggers a UTP reserve, hand off to the Auditor specialist (and **finance-controls-audit**) for ICFR implications around tax controls.
- If the position implicates SEC disclosure (e.g., material UTP reserve, change in deferred-tax valuation allowance), hand off to RegRep / **finance-disclosure-language** for footnote and MD&A language.

## Output Format

```markdown
# Tax Research Memo: [Short Title]

## Header
- **Requester:** [name / function]
- **Date:** [date]
- **Jurisdiction(s):** [federal / state / foreign]
- **Taxpayer:** [entity, classification]
- **Researcher:** [name]
- **Reviewer:** [name]

## Issue
[Precise yes/no or quantitative question]

## Conclusion
[1-2 sentences. Direct answer to the Issue. Note confidence level — "more likely than not," "should," "would," "will" — per the firm's opinion-language conventions.]

## Authorities
| # | Cite | Type | Operative Text (quoted) |
|---|------|------|-------------------------|
| 1 | [IRC §...] | Statute | "..." |
| 2 | [Treas. Reg. §...] | Regulation | "..." |
| 3 | [Rev. Rul. ...] | Rev Rul | "..." |
| 4 | [Case, jurisdiction] | Case law | "..." |
| 5 | [PLR / TAM] | PLR (non-precedential) | "..." |

## Analysis
[Paragraph(s) applying each authority to the facts. Identify any factual assumptions and their impact on the conclusion.]

## UTP Implication (FIN 48 / ASC 740-10)
- **Position uncertain?** [yes / no]
- **MLTN recognition threshold met?** [yes / no — with reasoning]
- **Measurement (if recognized):** [largest amount > 50% likely of being realized]
- **Reserve recommendation:** [amount or N/A]
- **Schedule UTP disclosure required?** [yes / no — with size-threshold note]

## Follow-Up to Provision Team
- [Specific computation, deferred-tax impact, valuation-allowance implication, or disclosure follow-up]
```

## Quality Checks

- [ ] Issue is a precise yes/no or quantitative question, not a topic
- [ ] Authority hierarchy followed (statute > reg > Rev Rul > case > PLR > secondary)
- [ ] Operative authority text is quoted verbatim and cite-verified
- [ ] Conclusion uses calibrated opinion language ("more likely than not" / "should" / "would" / "will")
- [ ] Each material authority is explicitly applied to the facts (not just listed)
- [ ] FIN 48 / ASC 740-10 two-step test addressed for any uncertain position
- [ ] Schedule UTP disclosure threshold considered
- [ ] Researcher ≠ reviewer per SoD policy

## Evolution Notes
<!-- Observations appended after each use -->
