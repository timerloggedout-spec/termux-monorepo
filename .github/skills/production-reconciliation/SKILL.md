# Production Reconciliation Skill

## Purpose

Provide a repeatable, evidence-first loop for reconciling any Git ref against any baseline without hard-coding a PR branch and without rewriting history.

This skill is the promotion/reconciliation layer. Historical corpus collection and Moneyball/3L0 inference remain separate concerns.

## Required loop

`RECON → PLAN/MEASURE → IMPLEMENT/ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

**WAIT/WATCH are mandatory methodological stages, not optional prose.** A dispatch, commit, queued run, or elapsed wall-clock interval is not an observation. After any execution-triggering action, the operator/automation must observe runtime state, wait for a terminal or diagnostically useful state, re-fetch authoritative state, and compare it with the pre-action baseline before deciding what happens next.

### Active-wait rule: never sit idle

WAIT means **concurrent useful work**, not sleep-only behavior. While one runtime cohort is waiting:

1. preserve the cohort's immutable run/attempt/SHA identity and last observed state;
2. work an independent non-conflicting phase: documentation, static inspection, provenance reconciliation, test-design review, complexity analysis, adapter research, or another authorized read-only task;
3. do not mutate the same files/branch in a way that could invalidate the watched cohort;
4. re-check the watched cohort at the next evidence boundary and after every material mutation;
5. record what was done during the wait so idle-time reduction itself is measurable.

The goal is **zero avoidable idle time**, not reckless parallel mutation. Never manufacture progress merely to fill time.

### Watcher protocol

For every dispatched or scheduled execution:

1. **Capture admission:** run/workflow ID, attempt, triggering event, input/ref, source SHA, baseline SHA, and start timestamp.
2. **WAIT:** do not classify queued/in-progress as success, failure, or completion.
3. **WATCH:** inspect jobs, steps, checks, artifacts, logs, and relevant comments/receipts as they become available.
4. **WAIT again** when the runtime is still active; continue independent non-conflicting work instead of becoming idle.
5. **VALIDATE:** inspect actual outputs, not merely workflow conclusions.
6. **RE-FETCH:** refresh run, SHA, branch/PR, and authoritative corpus/receipt after execution.
7. **COMPARE:** calculate before/after deltas and detect drift, no-op, regression, stall, or improvement.
8. **CLASSIFY:** distinguish routing/admission failure, provider/model failure, coordination failure, validation failure, hung/stalled execution, and successful effect.
9. **RECORD:** persist a compact evidence receipt/observation bound to immutable identifiers.
10. **REPEAT:** continue the loop for the next state/window until the declared stopping condition is reached.

### Stall / hung-event detection

A runtime must never remain indefinitely `queued` or `in_progress` without a diagnosis. Stall detection is evidence-based and state-aware:

- **Admission stall:** requested/queued but no job/step admission evidence after the configured observation window.
- **Queue stall:** queued with no transition and no scheduler/job evidence after the configured queue window.
- **Execution stall:** in-progress with no job/step/log/check/artifact progress across repeated observations.
- **Heartbeat stall:** a workflow exposes timestamps or step state but those values remain unchanged across multiple watches.
- **Effect stall:** workflow reaches terminal success but the expected authoritative effect (commit, artifact, receipt, corpus advancement, or check) does not appear after its declared propagation window.
- **Pagination stall:** a continuation run completes but `next_start_page` does not advance, repeats the same page, or advances while authoritative record counts/hashes show no corresponding effect.
- **Routing loop:** repeated admissions for the same immutable SHA/input produce the same cancellation/failure without a changed diagnosis.

Use **relative baselines**, not universal hard-coded timeouts, whenever the workflow supplies expected durations. Otherwise use explicit workflow-specific thresholds documented by the watcher. A stall is a classification/alert first; it is **not** permission to blindly rerun.

For every suspected stall record:

`cohort_id, run_id, attempt, sha, ref, state, first_seen, last_seen, observation_count, last_progress_marker, expected_effect, observed_effect, classification, retry_decision, reason`.

A stalled run can be retried only when the retry policy or a new diagnosis warrants it. The retry must receive a new event identity and must preserve the original stall observation.

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
- merge/promotion of the index is separate from collection;
- every continuation window must emit runtime evidence sufficient to prove the page actually executed and advanced;
- **no-page-advance is a first-class stall signal**, not a silent no-op;
- a complete corpus requires authoritative `next_start_page == null`.

## Quality-first measurement

Time is a performance dimension, not a quality proxy. Throughput metrics such as TCV, WTCV, RPI, action density, parallel yield, ATES, TPV, CIE, tool delay, and handoff latency must be interpreted with outcome, integration, validation, realization, attribution confidence, retries, conflicts, and human intervention. Never introduce a speed-only promotion gate.

Complexity-adjusted comparisons should prefer explicit task complexity when available; otherwise use a documented structural fallback and preserve the raw inputs. Never silently substitute missing complexity with zero.

## Runtime observers

Existing watcher infrastructure should be reused and extended rather than bypassed. Incident-only watchers are insufficient for autonomous loops: progression observers must capture **requested → queued → in_progress → completed**, current job/step evidence, artifacts, timestamps, progress markers, and final outcome. Observer workflows must not execute untrusted candidate code.

A watcher should expose enough evidence to answer: **what was expected, what changed, when did it last change, and what authoritative effect proves success?**

## Active phase scheduling

When a watched run is active, the orchestrator may advance independent phases in parallel. Each phase must declare:

- inputs and immutable baseline;
- files/resources it may mutate;
- evidence required to call it executed/validated;
- dependencies that block it;
- rollback/recovery boundary;
- next observation point.

Phase status must use at least `NOT_STARTED`, `READY`, `RUNNING`, `BLOCKED`, `COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED`, with `STALLED` available for runtime/process blockage. A phase being documented or designed is not equivalent to implementation.

## Rollback/recovery

A deletion is not automatically a rollback. Compare the target against the baseline, identify exact removed paths, classify each as authoritative source, generated evidence, intentional replacement, or unknown, and preserve forensic evidence before replacement. Correct forward when possible.

## Safety

Do not execute untrusted PR code from the control plane. Keep observer permissions read-only except narrowly scoped notification writes. Any mutating reconciliation must occur in a separately reviewed workflow with explicit authorization and conflict-stop behavior.

## State distinctions

`COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` are independent states. Never infer validation from commit existence or promotion from mergeability metadata. Likewise, `DISPATCHED`/`QUEUED`/`IN_PROGRESS` are runtime states, not evidence of effect.
