# ATES Phase C — Comparable Baseline Protocol

**Status:** contract implemented; measurement cohort not fabricated  
**Purpose:** provide the missing independently measured serial baseline required for `parallel_yield` and ATES.

## Rule

A parallel agent run is comparable only when its task set can be mapped to the **same task contracts** under the **same environment contract**.

The baseline is therefore not a guessed "what one agent would have taken" value. It is an independently measured serial cohort.

## Baseline record

Each cohort declares:

- `cohort_id`
- `task_contract_hash`
- `environment_fingerprint`
- one or more immutable task fingerprints
- positive wall-clock repetitions for every task
- median duration per task

The canonical contract is `docs/ops/ATES-BASELINE-COHORT.schema.json`.

`she.metrics.ates_baseline.BaselineCohort` validates and resolves these records.

## Matching

For a parallel run with task fingerprints:

`F = [f1, f2, ... fn]`

the declared serial baseline is:

`B = median(f1) + median(f2) + ... + median(fn)`

No missing fingerprint is substituted. Duplicate fingerprints are rejected.

The existing ATES reducer can then receive `B` as `sequential_baseline_sec`.

## Measurement protocol

For each task:

1. Freeze the task contract.
2. Compute its canonical SHA-256 task fingerprint.
3. Freeze the environment contract and compute its SHA-256 fingerprint.
4. Execute the task serially under the declared environment.
5. Record positive wall-clock duration.
6. Repeat the same task without changing the contract.
7. Record the median.
8. Repeat for every task in the cohort.
9. Commit the resulting baseline record with provenance.
10. Only then use the baseline for parallel-yield/ATES calculations.

## Do not do this

- infer a baseline from the parallel run;
- convert missing duration to zero;
- use a different task revision;
- silently change environment dependencies;
- mix fingerprints from different cohorts;
- compare a task subset against a full-cohort baseline;
- use a benchmark score as a proxy for wall-clock baseline;
- turn ATES into a merge-quality gate.

## Next runtime integration

The ATES event schema now supports:

- `cohort_id`
- `task_fingerprint`
- `task_contract_hash`
- `environment_fingerprint`

Agent workflows should emit these fields at the task boundary. The existing
`workflow_run` observer supplies run/attempt/SHA provenance, but it intentionally
cannot infer task identity from workflow names or PR churn.

Until task-boundary identity exists, the observer continues to collect useful
runtime evidence while ATES remains `null` where a defensible baseline cannot be
established.
