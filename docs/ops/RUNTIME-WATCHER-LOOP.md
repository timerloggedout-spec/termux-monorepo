# Runtime Watcher Loop

## Purpose

The repository is an automated environment. Runtime observation is therefore part of the method, not a human-only follow-up. The objective is to eliminate **wait-and-see latency** without eliminating the evidence that waiting produces.

The canonical operational loop is:

```text
RECON
  ↓
PLAN / MEASURE
  ↓
IMPLEMENT / ACT
  ↓
COMMIT
  ↓
WAIT
  ↓
WATCH
  ↓
VALIDATE
  ↓
RE-FETCH
  ↓
COMPARE
  ↓
CLASSIFY
  ↓
RECORD
  ↓
REPEAT ➿
```

## Why `WAIT` is a real phase

A dispatch only proves admission. A queued run proves scheduling. An in-progress run proves execution has started. None of these prove effect.

The watcher must preserve these distinctions:

| Runtime state | What it proves | What it does not prove |
|---|---|---|
| `DISPATCHED` / `REQUESTED` | an execution request was admitted | execution happened |
| `QUEUED` | the scheduler accepted work | a job started |
| `IN_PROGRESS` | work is executing | success or useful effect |
| `COMPLETED` | execution reached a terminal state | correctness of the produced state |
| `VALIDATED` | output passed the declared validation | promotion/merge |
| `PROMOTED` | the validated state was intentionally advanced | future correctness |

## Watcher responsibilities

For each execution expected to produce evidence, capture:

- workflow/run ID and attempt;
- triggering event and inputs;
- source/head SHA and relevant baseline SHA;
- branch/ref identity;
- run status and conclusion;
- job and step status;
- check conclusions;
- artifact names, sizes, retention/expiry state;
- output/receipt identifiers and hashes when available;
- timestamps sufficient for latency and handoff measurements.

Watchers should be **observer-first**: they may publish narrowly scoped notifications/receipts, but they must not execute untrusted candidate code or silently rerun failed work.

## Failure is data

A failed run is an observation. Do not rerun solely to turn red into green. Classify the failure before deciding whether a retry has expected value:

- routing/admission failure;
- provider failure;
- model/agent failure;
- coordination failure;
- environment/dependency failure;
- validation failure;
- authorization/quota failure;
- genuine transient failure.

A retry is a new event with its own run ID/attempt and must be linked to the original observation.

## Backfill-specific progression

Historical corpus continuation is page-bounded and resumable. The canonical manifest's `history_window.next_start_page` is the continuation cursor. Each successful window must demonstrate that:

1. the run actually executed against the intended source SHA;
2. the recorded start page matches the cursor observed before execution;
3. the output manifest advances the cursor or reaches `null`;
4. the resulting corpus artifacts are internally consistent;
5. the resulting commit, if any, is the exact observed delta;
6. the next watcher cycle re-fetches the new `master` state before beginning another window.

No partial corpus may be described as complete.

## Quality-first telemetry

Time is a performance dimension, not a quality score. ATES/TCV/TPV/RPI/action-density/parallel-yield observations must be paired with outcome, integration, validation, realization, attribution confidence, conflicts, retries, and human intervention.

Complexity adjustment should use explicit task complexity where available. Structural fallback may use documented churn/files inputs, but missing complexity must remain missing rather than becoming a fabricated zero.

## Existing infrastructure

`actions-run-watcher.yml` remains the incident notification lane. The context-relationship backfill watcher adds **progression observation** for the autonomous historical continuation lane. The two responsibilities are complementary:

- incident watcher: notify on failure/action-required states;
- progression watcher: observe requested/in-progress/completed states and runtime evidence.

## Assistant/operator behavior

When an execution is initiated, the same methodology applies outside Actions:

`ACT → WAIT → RE-FETCH → INSPECT JOBS/LOGS/ARTIFACTS → VALIDATE → COMPARE → RECORD → REPEAT`.

Do not report "done" because a job is merely queued. Do not report "validated" because a workflow is green. Do not report "promoted" because a PR is mergeable.

This is the repository's **meticulous MAXIMUM-EFFORT** operating discipline: accelerate the feedback cycle, not the evidence boundary.
