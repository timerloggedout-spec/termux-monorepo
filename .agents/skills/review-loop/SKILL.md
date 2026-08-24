---
name: review-loop
description: Evidence-first continuous review loop for agentic GitHub development. Reconstruct prior work, correlate events to SHAs and runs, ingest reviews/comments/artifacts, classify proven versus candidate findings, apply minimal improvements, validate repeatedly, and feed results forward.
---

# Review Loop

## Mission

Review is an operational feedback loop, not a final human checkpoint. The loop seeks the desired task outcome with correctness first, while preserving all attempts and provenance.

## Required sequence

1. **Recon** — inspect current branch/SHA, recent commits, open PRs/issues, reviews/comments, workflow runs, artifacts, relevant `.agents/skills/`, SSOTs, decision matrices, Mermaid/process records, provider/library adapters, cooldown/quota policy, command libraries, and related templates/proposals.
2. **Relationship mapping** — use the canonical context-relationship graph discipline. Start with exact roots/permalinks; distinguish verified relationships from candidates; preserve evidence URLs and temporal bounds.
3. **Agent attribution** — use explicit agent identity, co-author/signoff, workflow actor, tool output, or other provenance. Do not attribute work solely from a shared GitHub PAT identity.
4. **SHA/run binding** — correlate tested SHA, workflow revision, run, attempt, job, step, artifact, review, and resulting commit before interpreting feedback.
5. **Review ingestion** — classify substantive findings separately from provider-control notices, cooldown notices, stale/superseded comments, and duplicate feedback. Historical repository work demonstrates that provider-control comments can create unwanted Jules feedback loops; those controls must not be mistaken for substantive review.
6. **Prior-art cherry-pick analysis** — search existing branches, PRs, commits, comments, reviews, templates, and proposals for already-solved or partially-solved mechanisms. Prefer the smallest compatible existing implementation over re-invention. Preserve provenance when transplanting a solution.
7. **Change selection** — rank findings by correctness risk, severity, reproducibility, expected information gain, regression risk, and resource/quota impact. Latency is a diagnostic factor, not a correctness override.
8. **Implement** — make the smallest evidence-backed change. Do not silently narrow provider/model capability, concurrency, or output capacity to make the run appear successful.
9. **Validate** — execute multiple runs per cycle when a change affects orchestration, routing, provider/model selection, quotas, concurrency, or feedback behavior. Inspect jobs → steps → logs → artifacts → receipts.
10. **Review again** — consume new provider/agent reviews and workflow evidence after the change. Do not stop at the first green signal.
11. **Promote/cull** — promote only when the desired task outcome and correctness/integration gates are verified. Cull low-ROI treatments while preserving their evidence; do not delete unsuccessful attempts.
12. **Feed forward** — update the adaptive-feedback skill, SSOT, relationship graph, experiment lineage, or other process documentation when the review itself teaches a new reusable rule.
13. **LOOP** — repeat until the desired outcome is confirmed or a documented terminal condition requires new input.

## Review classification

Every finding should be classified where evidence permits:

```text
SUBSTANTIVE_REVIEW
PROVIDER_CONTROL
COOLDOWN
DUPLICATE
SUPERSEDED
ENVIRONMENT
INFRASTRUCTURE
SECURITY
CORRECTNESS
REGRESSION
UNKNOWN
```

A provider-control comment may be operationally important without being a code finding. A cooldown may justify waiting without implying failure. An environment failure may be a run failure without proving the implementation is incorrect.

## Historical intelligence

The repository contains prior implementations worth reusing, including:

- CodeRabbit/Qodo review cooldown ingestion and provider-cycle coalescing.
- Event-driven verified second-pass peer dispatch and controls that keep provider UI/control notices out of the Jules feedback relay.
- Provider review request automation and bounded peer-review waits.
- Decision-tree/control-plane documentation from the Issue #192 workstream.
- Self-Healing Engine P0.1 incident identity, P0.2 observer ingestion, and P0.3 deterministic L0 recovery intent planning.

These are evidence-backed prior mechanisms. Inspect their current implementation and validation state before introducing a parallel mechanism.

## Outcome contract

Record:

```text
PASS / FAIL / UNKNOWN + notes
correctness
integration
checks/tests
warning/error rate + severity
complexity / Big-O where relevant
compute/resource use
feedback/rework cycles
context/prompt efficiency
provider/library quota/resource use
latency
```

Workflow success, HTTP success, a completed review, low latency, or a large response is not sufficient evidence of task success.

## Provenance-preserving promotion

Never rewrite history merely to make a preferred attempt look original:

```text
X
├── review-fix A → SHA A
├── review-fix B → SHA B
└── review-fix C → SHA C ← promoted
```

A cherry-picked implementation should retain its source commit/PR/issue references where possible. If the exact source cannot be safely transplanted, reproduce the behavior with a new commit and record the provenance relationship.

## Regression protection

A later failure creates a new finding and successor attempt. Preserve the previous run, review, artifact, and promotion evidence. Compare before/after behavior rather than declaring a rollback merely because a new run differs.

## Closeout

Do not report "fixed" until the desired behavior is verified. State what was proven, what remains unproven, what prior work was reused, and which new observations should feed the next cycle.
