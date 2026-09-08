# Production Reconciliation Skill

## Purpose

Provide a repeatable, evidence-first loop for reconciling any Git ref against any baseline without hard-coding a PR branch and without rewriting history.

## Required loop

`RECON → PLAN → IMPLEMENT → COMMIT → WAIT → VALIDATE → RE-FETCH → CLASSIFY → REPEAT`

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

## Rollback/recovery

A deletion is not automatically a rollback. Compare the target against the baseline, identify the exact removed paths, classify each as authoritative source, generated evidence, intentional replacement, or unknown, and preserve forensic evidence before replacement. Correct forward when possible.

## MVT / DOE

Use the same validation suite and a fixed baseline for comparable experiments. Candidate identity is immutable. Store experiment ID, candidate SHA, baseline SHA, suite, result, and provenance. Promotion is separate from measurement.

## Safety

Do not execute untrusted PR code from the control plane. Keep observer permissions read-only. Any mutating reconciliation must occur in a separately reviewed workflow with explicit authorization and conflict-stop behavior.
