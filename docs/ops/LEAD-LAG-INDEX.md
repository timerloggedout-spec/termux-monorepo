# Lead/Lag Index — SSOT Audit Plane

## Status

Operational specification for the continuous GitHub audit system. This index is intentionally adjacent to the repository's control-plane documentation rather than embedded in a model-specific workflow.

## Why it exists

A GitHub interaction is not automatically a useful development event. We need to distinguish **lead signals** (context, prompts, reviews, dispatches, checks, observations) from **lag outcomes** (correctness, tests, integration, regression, merge, rework).

Latency is a diagnostic dimension, not the primary optimization objective. A slow correct result outranks a fast incorrect result. Long execution is acceptable while the system remains observable, makes forward progress, and does not loop or consume resources without progress.

## SSOT anchor

Every audit observation is anchored to:

`repository + source_sha + event_id + observed_at`

A rotated staging/audit branch is a presentation surface only. The immutable source SHA and event identity remain the evidence anchor. Never rewrite history to improve a score.

## Lead signals

Examples:

- issue / PR creation or edit
- PR synchronize / review request
- prompt/context ingestion
- relationship-graph discovery
- provider/model catalog observation
- agent dispatch request
- workflow queued / started
- code review / review thread
- test/check started
- prior finding fed into the next prompt

## Lag outcomes

Examples:

- test/check success or failure
- task PASS/FAIL with notes
- correctness verdict
- warning/error count and severity
- review thread resolution
- integrated commit
- merge/close
- regression detected
- rollback/reversion detected
- corrective follow-up

## Lead → lag pair

A lead is paired with a lag when both share a stable correlation key such as:

`task_id`, `pr_number`, `issue_number`, `head_sha`, `workflow_run_id`, `experiment_id`, or an explicit `context_key`.

The index records:

- lead timestamp
- lag timestamp
- elapsed duration
- event ordering
- source SHA
- correlation key
- actor/agent attribution when available
- attribution confidence
- outcome class
- evidence URI/run/artifact

## Outcome hierarchy

The canonical evaluation order is:

1. **Correctness / working behavior**
2. **Integrated task outcome**
3. **Tests and verification**
4. **Error/warning rate and severity**
5. **Rework / feedback cycles / human intervention**
6. **Relevant compute or algorithmic complexity**
7. **Context/prompt efficiency**
8. **Resource usage / request count**
9. **Latency**

Latency can expose a loop, provider stall, retry storm, deadlock, or pathological context expansion. It must not override correctness.

## PASS / FAIL

Every evaluated task gets:

`PASS | FAIL | INCONCLUSIVE`

with notes and evidence. `INCONCLUSIVE` is mandatory when the observation boundary ended before correctness/integration could be established. HTTP 200, workflow success, or generated text alone is never a task PASS.

## Time-loop / Continue model

A task may run through multiple attempts. Each attempt is immutable evidence. A later successful trunk may be promoted as the current working state while earlier branches/attempts remain addressable by SHA and event ID.

Conceptually:

`attempt x → diagnose → attempt x+1 → verify → promote winning state`

This is compatible with ChronoMancer-style consolidation, but Git history and audit receipts remain the authoritative evidence; no prior message/event is silently rewritten.

## Monitoring states

- `RUNNING` — active and producing progress
- `WAITING` — waiting on a declared external dependency
- `STALLED` — no expected progress beyond a policy threshold
- `LOOP_SUSPECTED` — repeated equivalent events without new evidence
- `FAILED` — execution or verification failure
- `PASS` — correctness and integration gates satisfied
- `INCONCLUSIVE` — insufficient evidence

A long-running task is not a failure merely because it is slow. The monitor escalates based on **lack of progress**, repeated work, error growth, quota exhaustion, or resource runaway.

## Regression rule

The index is append-only. The last known-good control-plane SHA is compared with each observation. A regression is a new event that becomes evidence for a forward correction; it is not erased by rollback.

## Relationship to #337 / #335 / #336

- **#337** is the continuous-evaluation control plane.
- **#335** supplies time-series/repository-history discovery.
- **#336** supplies repository-history reconstruction and reusable findings.
- The relationship graph is the context-ingestion map connecting those systems.

## Maintainer rule

The Manager/Conductor owns orchestration policy. The audit index owns evidence. Provider/model routers select candidates. Specialists execute bounded work. Human review remains the final authority for ambiguous/high-impact changes.
