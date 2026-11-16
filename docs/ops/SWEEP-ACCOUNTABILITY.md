# Sweep Accountability & Historical/Future Evidence Contract

This is the cross-lane accountability contract for **every sweep**: historical backfill, version/iteration pass, scheduled sweep, manual sweep, workflow observation, or event-driven action.

A sweep is an evidence-producing transaction:

\`\`\`
SWEEP
  -> SCOPE -> SNAPSHOT -> OBSERVE -> FINDINGS
  -> ACTIONS -> EFFECTS -> PROVENANCE -> RECEIPT
  -> NEXT CURSOR / NEXT ITERATION
\`\`\`

Every iteration is a new layer. Previous layers are never overwritten.

## Coverage modes

- **HISTORICAL** — backfill prior repository work and previously observed operational events.
- **CONTINUOUS** — observe future actions/events and record each sweep's observations.
- **RECONCILIATION** — compare a new observation against prior receipts and record the delta.
- **CORRECTION** — record a repair to an earlier finding without deleting the original receipt.

A later sweep may supersede a conclusion, but it must not erase the earlier observation.

## Versioned sweep identity

Every receipt carries \`schema_version\`, \`sweep_id\`, \`parent_sweep_id\`, \`sweep_version\`, \`iteration\`, \`mode\`, \`scope\`, timestamps, \`status\`, and continuation cursor.

Thus:

\`\`\`
v1 / sweep 001
        ↓
v1 / sweep 002
        ↓
v2 / sweep 003
        ↓
v3 / sweep 004
\`\`\`

is lineage, not replacement.

## Minimum accountability

Every sweep records:

### Scope / inputs
- repository/ref
- source URLs or API endpoints
- event/action type
- time window
- query/filter
- cursor/page
- source SHA(s)
- input snapshot hash where practical

### Findings
- observed/inferred/unknown/contradicted classification
- evidence references
- confidence
- contradictions and missing evidence
- coverage counts and limits

### Actions
- action ID/type
- actor
- tool/provider
- target
- attempted/succeeded/failed/skipped/cancelled/no-op status
- reason

### Effects
- before/after state where available
- resulting artifact/commit/PR/run IDs
- evidence references

### Provenance
\`\`\`
human / agent / workflow
        ↓
workflow / job / step
        ↓
event
        ↓
issue / PR / commit / artifact
        ↓
SHA + timestamp
        ↓
receipt
\`\`\`

GitHub identity alone is not agent identity.

### Continuation
- \`next_cursor\`
- next start time
- next sweep version/iteration
- reason for partial coverage

## Append-only rule

Generated receipts live under:

\`\`\`
docs/ops/generated/sweep-ledger/
\`\`\`

One immutable JSON object is written per sweep, plus an append-only daily JSONL stream.

Do **not** use a mutable "latest truth" object as the audit record. Dashboards and status files are projections.

## Historical backfill

Historical sweeps must distinguish:

- **OBSERVED** — directly established by a source.
- **INFERRED** — derived from multiple observations.
- **UNKNOWN** — source did not establish it.
- **CONTRADICTED** — later evidence conflicts with the prior observation.

A backfill is **PARTIAL** whenever pagination, retention, inaccessible sources, or missing artifacts prevent complete reconstruction.

Never claim \`history_complete=true\` merely because one local lane's Git history is complete.

## Future-event rule

Every future sweep/action/event receives a receipt even when it:
- fails;
- is cancelled;
- is skipped;
- produces no mutation;
- lacks expected evidence;
- is a no-op.

A failed or cancelled event is data.

## Version / iteration layers

A version is an analytical layer, not a rewrite:

\`\`\`
Layer N
  raw observation
  receipt
  derived finding
       ↓
Layer N+1
  re-observation
  comparison Δ
  correction/supersession
  new receipt
\`\`\`

Raw evidence remains available so attribution and derived metrics can be recomputed.

## Help-Given Tribute relationship

The Help-Given Tribute diff gate is a lane-specific gate inside this broader sweep contract.

It answers:

> Did this claimed/staked upstream contribution actually produce a requirement-linked repository delta with explicit proof?

The sweep ledger answers:

> What did every pass observe, attempt, change, fail to change, and learn—and what evidence proves that history?

Help-Given receipts should reference their sweep when the event is observed by a sweep; sweeps preserve the lane receipt as a source.

## Operational loop

\`\`\`
RECON → HISTORICAL BACKFILL → BASELINE RECEIPT
  → CONTINUOUS SWEEP → OBSERVE → COMPARE → CLASSIFY
  → ACTION / NO-ACTION → EFFECT + PROVENANCE
  → RECEIPT → NEXT CURSOR → NEXT VERSION / ITERATION → REPEAT
\`\`\`

This is the accountability substrate for MoneyBall / MVT-DOE / ATES and manager evolution.


## Trigger and coverage semantics

The accountability invariant applies to every **sweep transaction**, not merely successful code changes. A sweep may be initiated by a push, pull-request event, issue event, issue-comment event, scheduled reconciliation, or explicit manual dispatch. Scheduled/HISTORICAL reconciliation is the authoritative mechanism for event families that GitHub Actions cannot subscribe to generically or whose retained history must be reconstructed from the API.

The implementation deliberately distinguishes:

- **event-trigger coverage** — the triggering event itself receives a receipt;
- **historical source coverage** — retained GitHub/Git/API history is enumerated and recorded with pagination/coverage state;
- **repository-history coverage** — Git commits reachable from the checked-out ref;
- **analytical coverage** — what the current sweep version actually inspected.

No one of these is allowed to masquerade as another. A receipt must report COMPLETE, PARTIAL, or UNKNOWN coverage and preserve the reason/cursor when coverage is incomplete.

Historical census artifacts are stored beneath a unique workflow-run directory. They are therefore append-only across iterations; later sweeps add observations rather than replacing prior census data.
