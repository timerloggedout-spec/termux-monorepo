# PR Evidence Evaluation Skill

## Purpose

Evaluate pull requests by the quality and freshness of evidence rather than raw commit count, changed-file count, PR age, or comment volume. Large PRs are not penalized merely for being large when their diffs are relevant, reviewed, validated, and iteratively improved.

This skill is an **evaluator over the historical evidence corpus**. It is not the corpus, not a receipt generator, and not a substitute for DOE/MVT or Moneyball/3L0 inference.

## Evidence hierarchy

Weight evidence in this order:

1. **Current-SHA diff evidence** — what actually changed, including additions, deletions, replacements, and affected contracts.
2. **Current-SHA review evidence** — substantive review findings, requested changes, approvals, and inline comments attached to the current diff.
3. **Review-cycle continuity** — comments and provider cycles that identify a head SHA, request an action, report completion, or explicitly remain pending.
4. **Validation evidence** — terminal checks, test results, deployment/preview evidence, and reproducible artifacts bound to the candidate SHA.
5. **Provenance/attribution** — linkage to the stated task, issues, proposal lineage, workflow/provider/session evidence, and confidence.
6. **Recency** — evidence from the current head dominates stale evidence from superseded heads.
7. **Size metadata** — commit count, file count, additions/deletions are context only and never a quality proxy by themselves.

## Current-SHA rule

Every evaluation resolves the PR head to an immutable SHA and compares it with the current base SHA. A review or check attached only to an older head is historical evidence, not current approval. When the head changes, start a new evaluation cycle and retain the previous observation.

## Corpus rule

Every PR is represented in the longitudinal corpus as an observation when collection coverage permits. A PR does **not** require a heavyweight Markdown receipt. Compact metadata records are preferred; receipts are projections for notable cycles/promotions.

When history is paginated or bounded, record the exact page/window, next-page cursor, collection timestamp, omitted fields, and parser/API failures. Never silently call a partial window complete.

## Mega-PR rule

A large or long-lived PR can score highly. Do not use thresholds such as “too many commits” or “too many files” as automatic failures. Evaluate coherence, review coverage, finding disposition, validation coverage, and current-SHA alignment.

## Review finding weighting

Suggested finding weights:

- High/security/correctness: 10
- Medium/maintainability/reliability: 5
- Low/style/nit: 1

A finding is current only when it applies to the current head/diff or remains explicitly unresolved across a head transition. Duplicate provider comments are collapsed by normalized finding text/path before scoring.

## Cycle states

`REQUESTED → ACKNOWLEDGED → REVIEWING → FINDINGS → IMPLEMENTING → VALIDATING → REFETCH → CLASSIFY → REPEAT`

Provider cooldown, skipped review, stale review, missing workflow execution, and unobserved validation are **UNVERIFIED**, not green.

## Scoring guidance

A reference implementation may allocate:

- 35% diff/task relevance and contract coverage
- 25% substantive review evidence and finding disposition
- 20% validation/check evidence
- 10% provenance and review-cycle continuity
- 10% freshness/current-SHA alignment

Raw commit/file/comment counts contribute 0% to the quality score. They may be reported as context.

## DOE/MVT and 3L0

For comparable experiments, freeze the baseline and candidate identity, record treatment assignment, collect evidence before evaluation, and keep promotion separate from measurement.

Moneyball/3L0 should aggregate **integrated outcomes and orchestration-policy performance** from corpus observations. Never promote a model/provider merely because it has a high activity count or isolated score.

## Required loop

`RECON → WEIGHT → PLAN → IMPLEMENT → COMMIT → WAIT → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

Never promote from a stale snapshot. Never treat a successful external preview as proof of repository correctness. Keep mutation separate from observation and evidence collection.
