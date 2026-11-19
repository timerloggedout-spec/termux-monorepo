---
name: research-spike-and-poc
description: Runs timeboxed technical exploration to reduce unknowns before commitment. Use when you must choose between technologies, prove feasibility, estimate effort for unfamiliar work, or answer "can we integrate X" before writing production code.
---

# Research Spike and Proof of Concept

## Overview

Spikes trade calendar time for information. They answer specific technical questions under a strict timebox, produce evidence (code notes, benchmarks, integration sketch), and end with a clear recommendation — proceed, pivot, or stop. They are not a substitute for a product spec (`spec-driven-development`) or open-ended brainstorming (`idea-refine`).

## When to Use

- Unknown integration effort (new API, SDK, protocol, cloud service)
- Competing libraries or frameworks need an evidence-based choice
- Performance or scale question that docs cannot answer
- "Will this run in our environment?" (build, deploy, compliance constraints)
- Need a rough order-of-magnitude estimate grounded in a prototype

## When NOT to Use

- Requirements are still vague (use `idea-refine` then `spec-driven-development`)
- Work is already well understood — implement with `incremental-implementation` and `test-driven-development`
- Spike used to bypass review or ship throwaway code to production

## Process

### 1. Write the spike charter (before coding)

Answer in writing:

- **Question:** What single decision or unknown does this spike answer?
- **Success criteria:** What evidence will count as "answered"?
- **Non-goals:** What this spike will explicitly not do (no UI polish, no full test suite, etc.)
- **Timebox:** Wall-clock limit (e.g., 4 hours, 2 days). When time is up, stop and report.

### 2. Explore under constraints

- Prefer the smallest code that touches the real integration surface (real API, real compiler, real dependency).
- Document as you go: commands run, versions used, failures, surprises.
- Do not gold-plate — spikes may be deleted after the decision.

### 3. Capture evidence

Produce at least one of:

- Minimal repro or integration snippet (in branch or doc)
- Benchmark numbers with methodology
- Checklist of blockers or required follow-up work
- Comparison table for options (criteria weighted by project needs)

### 4. Recommendation

End with a decisive summary:

| Outcome | Meaning |
|---------|---------|
| **Proceed** | Evidence supports the chosen path; list assumptions for implementation |
| **Pivot** | Another option won; summarize why |
| **Stop** | Not feasible within constraints; say what would need to change |

### 5. Handoff

- If **Proceed:** Link findings to `planning-and-task-breakdown` tasks; production work follows `incremental-implementation`.
- If architectural: consider an ADR via `documentation-and-adrs`.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We'll just build it and learn" | Unbounded build is expensive. A timebox bounds downside. |
| "No time to document the spike" | The value is the decision; undocumented spikes get re-litigated. |
| "Let's keep this spike code in main" | Spike code rots. Merge only what meets prod standards after proper implementation. |
| "One more day will make it perfect" | Extend the charter explicitly or stop; open-ended spikes become projects. |

## Red Flags

- Spike without a written question or success criteria
- No timebox, or repeated "just one more" extensions without new charter
- Production secrets or PII in spike branches committed to shared repos
- Spike bypasses security or compliance review when the question was about those risks (involve the right reviewers)

## Verification

- [ ] Charter (question, success criteria, timebox, non-goals) exists before deep work
- [ ] Timebox respected or formally renegotiated with rationale
- [ ] Evidence artifact exists (doc, branch, benchmark output) that a teammate could review
- [ ] Clear Proceed / Pivot / Stop recommendation with next steps
- [ ] Throwaway spike code either deleted or quarantined — not mistaken for production-ready
