# Production Reconciliation Skill

## Purpose

Provide a repeatable, evidence-first loop for reconciling any Git ref against any baseline without hard-coding a PR branch and without rewriting history.

This skill is the **promotion/reconciliation layer**. Historical corpus collection and Moneyball/3L0 inference remain separate concerns.

## Required loop

`RECON → PLAN → IMPLEMENT → COMMIT → WAIT → VALIDATE → RE-FETCH → CLASSIFY → RECORD → REPEAT`

The loop terminates only when the current immutable SHA is aligned or intentionally accepted, current review/check evidence is terminal, and no actionable current finding remains.

## Ref model

- Inputs may be branch, tag, or commit SHA.
- Resolve every ref to an immutable commit before comparison.
- Record target SHA, baseline SHA, merge-base, ahead/behind, changed paths, and timestamps.
- Never force-push, reset, or silently discard an experimental state.
- A staging/experiment branch may rotate; each state must remain addressable by SHA.

## Drift classification

- `aligned`: baseline is an ancestor and target is current.
- `candidate-ahead`: target contains baseline and is ahead.
- `diverged`: neither side contains the other; stop and require a reviewed merge/reconciliation strategy.
- `behind`: target lacks baseline; stop unless an explicit reconciliation operation is separately authorized.

## Evidence rules

A workflow success is evidence about that workflow, not proof of repository correctness. Bind reviews, checks, generated artifacts, telemetry, and experiment observations to the SHA that produced them. Treat skipped/quota-limited reviews as non-approval evidence.

Every material reconciliation should leave a compact corpus observation or referenceable receipt. The receipt is a projection; the corpus remains the longitudinal source for later comparisons.

## Historical and experiment continuity

For DOE/MVT work:

- freeze the baseline SHA;
- assign a stable experiment/cohort ID;
- bind candidate SHA and suite to the observation;
- record result, provenance, and confidence;
- compare only like-for-like treatment cohorts;
- keep promotion separate from measurement.

For historical backfill:

- page-bounded collection is valid only when its bounds are recorded;
- `next_start_page` must drive continuation;
- partial history must never be described as complete;
- merge/promotion of the index is separate from collection.

## Rollback/recovery

A deletion is not automatically a rollback. Compare the target against the baseline, identify exact removed paths, classify each as authoritative source, generated evidence, intentional replacement, or unknown, and preserve forensic evidence before replacement. Correct forward when possible.

## Safety

Do not execute untrusted PR code from the control plane. Keep observer permissions read-only. Any mutating reconciliation must occur in a separately reviewed workflow with explicit authorization and conflict-stop behavior.

## State distinctions

`COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` are independent states. Never infer validation from commit existence or promotion from mergeability metadata.
