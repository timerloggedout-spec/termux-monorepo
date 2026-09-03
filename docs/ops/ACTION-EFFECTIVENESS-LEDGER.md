# Action Effectiveness Ledger

The Action Effectiveness Ledger measures whether orchestration activity produces useful, validated change. It is an evidence ledger, not a productivity scoreboard based on raw volume.

## Core principle

`activity != effectiveness`

Commit count, comment count, review count, and PR size are contextual telemetry. Quality is determined by the relationship between an action, the resulting tree/evidence delta, validation, and the resulting alignment state.

## Measurement layers

### 1. Change layer

For the complete `merge-base..head` range:

- `commit_count`: all commits in the PR range.
- `empty_commit_count`: commits whose tree has no file delta from their parent.
- `metadata_only_commit_count`: commits with file entries but zero textual additions/deletions (for example, pure rename/mode metadata).
- `effective_commit_count`: commits with a non-zero tree/content delta.
- `gross_additions/deletions`: cumulative per-commit churn.
- `final_additions/deletions/files`: retained `base..head` diff.
- `ahead/behind`: graph alignment relative to the selected base.

Gross churn and final diff MUST NOT be conflated. A large amount of historical churn can collapse to a small retained diff after revisions.

### 2. Discussion/review layer

Measure separately:

- conversation comments;
- reviews;
- inline review comments;
- approvals;
- changes-requested reviews;
- actionable-comment heuristic counts.

These are evidence sources. They are not equivalent to completed work.

### 3. Validation layer

At the measured head SHA, record:

- total checks;
- successful checks;
- failed checks;
- pending checks.

A review request or provider request is not review completion. A workflow dispatch is not execution success. Execution success is not validation. Validation is not promotion.

## Action-to-effect model

Every actionable event should be classified along this chain:

`ACTION → NEW HEAD? → TREE EFFECT? → VALIDATION? → FINDING RESOLVED? → ALIGNMENT IMPROVED?`

Recommended classifications:

- `NOOP`
- `DISCUSSION_ONLY`
- `METADATA_ONLY`
- `ACTION_EXECUTED`
- `ACTION_VALIDATED`
- `ACTION_RESOLVED`
- `ACTION_REGRESSED`
- `STALE_ACTION`
- `PROVIDER_PENDING`
- `UNVERIFIED`

## Delta metrics

### No-op rate

`(empty commits + metadata-only commits) / total commits`

Use as a diagnostic signal, never as a standalone quality score.

### Realization ratio

`final retained diff size / gross historical churn`

This describes how much historical churn remains represented in the final tree. It is not a correctness score and should be interpreted alongside review and validation evidence.

### Action yield

`validated actions / actionable actions`

### Resolution yield

`resolved findings / actionable findings`

### Regression rate

`actions that introduce a new failure or reopen a finding / validated actions`

### Alignment delta

Compare the before/after state of the selected alignment signals: merge-base relationship, behind count, current-head findings, failed checks, unresolved review findings, and provider-pending state.

## Control-plane rules

1. Re-fetch the PR head SHA before every decision cycle.
2. Tie review and check evidence to a specific SHA.
3. Treat old-head findings as historical until revalidated.
4. Never equate comments or commits with progress without an observable effect.
5. Update a stable ledger comment in place; do not create a new bot comment for every measurement cycle.
6. Keep measurement read-only with respect to PR source execution.
7. Keep privileged mutation outside telemetry workflows.
8. Record `COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` separately.

## Optimization loop

`RECON → MEASURE → CLASSIFY → PLAN → ACT → WAIT → VALIDATE → RE-MEASURE → COMPARE → REPEAT`

The optimization target is not fewer commits or fewer comments. The target is higher validated/resolved action yield with lower no-op churn, lower regression rate, and better alignment evidence.
