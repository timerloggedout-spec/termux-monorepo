# DoE / MVT Reliability Remediation

**Status:** implementation branch; hosted verification required before merge or promotion.

## Changes in this branch

### Agent MVT

- Replaces the private `agent-mvt-v1` payload with the canonical `EXPERIMENT.schema.json` version `1.0` record.
- Adds `scripts/doe/experiment_record.py` to build and validate canonical records.
- Runs the selected suite against both immutable baseline and candidate commits using a detached baseline worktree.
- Preserves both exit codes, run/attempt identity, failed stage, failure reason, commit SHAs, merge base, suite, and an Actions run evidence URL.
- Emits evidence through an unconditional step and uploads canonical records, pre-canonical failure envelopes, path diffs, and both test logs.
- Does not invent a SHA when ref resolution fails. Such a failure is explicitly marked as a blocked, non-canonical envelope.
- A metadata-only comparison is `observed`, never `passed`. A test comparison is `passed` only if both refs return exit code zero.

### Team MVT

- Removes manager selection based on the UTC wall-clock minute. Manager policy is now an explicit workflow-dispatch input, with a deterministic fallback for event-triggered runs.
- Removes the calculated `sequence_slot` that was recorded but did not control GitHub matrix execution.
- Records `sequence_control=uncontrolled_matrix_dispatch`; matrix order is not randomized or counterbalanced.
- Labels A/B as `primary_same_task` and C/D/E as `diagnostic_non_comparable`.
- Reports primary and diagnostic cell counts separately and states that C/D/E are excluded from pooled treatment effects.
- Keeps promotion blocked while task correctness and independent evaluator evidence remain UNKNOWN.

### Tests

`tests/test_doe_experiment_record.py` covers:
- canonical schema validation of a successful record;
- failure status when either side fails;
- missing exit code handling;
- metadata-only status;
- rejection of unresolved refs and unknown schema properties;
- pre-resolution failure preservation without fabricated SHA values.

Run locally:

```bash
python -m pip install jsonschema pytest
python -m pytest -q tests/test_doe_experiment_record.py
```

The Agent MVT workflow installs the same validation dependencies before running its suites.

## Remaining gates / known limitations

1. **Hosted checks have not yet run on this branch.** The GitHub connector cannot execute the repository's test commands locally; merge requires current-head CI evidence.
2. **Team MVT does not yet consume a generated randomized DoE assignment.** Its matrix is intentionally declared uncontrolled rather than falsely described as randomized. A future scheduler must own assignment, persist seed and intended order, and enforce it at dispatch.
3. **Team MVT lane receipts are not yet projected into canonical EXPERIMENT records.** This branch corrects their comparability labels and the Agent MVT contract; a dedicated adapter is still needed to map lane identity and treatment fields without inventing configured-instance prompt/tool hashes.
4. **Independent correctness evaluation and ATES scoring remain separate gates.** No UNKNOWN outcome is promoted to a pass.
5. **Dashboard feeds and historical backfill are not rewritten here.** They must be migrated from canonical records in a versioned backfill with before/after reconciliation.

## Acceptance criteria

- Every Agent MVT terminal run uploads either a schema-valid canonical record or a clearly marked non-canonical blocked failure envelope.
- Baseline and candidate execute the same named suite on immutable SHAs.
- A failing or missing test result cannot produce `passed`.
- Team MVT primary and diagnostic counts are separate; no pooled comparison across A/B and C/D/E.
- No production policy promotion occurs from this branch alone.
