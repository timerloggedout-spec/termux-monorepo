# Production Reconciliation Skill

## Purpose

Provide a repeatable, evidence-first loop for reconciling any Git ref against any baseline without hard-coding a PR branch and without rewriting history.

This skill is the **promotion/reconciliation layer**. Historical corpus collection and Moneyball/3L0 inference remain separate concerns.

## Required loop

`RECON → PLAN/MEASURE → IMPLEMENT/ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

**WAIT/WATCH are mandatory methodological stages, not optional prose.** A dispatch, commit, or queued run is not an observation. After any execution-triggering action, the operator/automation must observe the runtime state, wait for a terminal or diagnostically useful state, re-fetch the authoritative state, and compare it with the pre-action baseline before deciding what happens next.

The loop terminates only when the current immutable SHA is aligned or intentionally accepted, current review/check evidence is terminal, runtime observations have been collected where execution was expected, and no actionable current finding remains.

### Watcher protocol

For every dispatched or scheduled execution:

1. **Capture admission:** run/workflow ID, attempt, triggering event, input/ref, source SHA, baseline SHA, and start timestamp.
2. **WAIT:** do not classify queued/in-progress as success, failure, or completion.
3. **WATCH:** inspect jobs, steps, checks, artifacts, logs, and relevant comments/receipts as they become available.
4. **WAIT again** when the runtime is still active; do not manufacture completion from elapsed time.
5. **VALIDATE:** inspect the actual output, not merely the workflow conclusion.
6. **RE-FETCH:** refresh the run, SHA, branch/PR, and authoritative corpus/receipt after execution.
7. **COMPARE:** calculate the before/after delta and detect drift, no-op, regression, or improvement.
8. **CLASSIFY:** distinguish routing/admission failure, provider/model failure, coordination failure, validation failure, and successful effect.
9. **RECORD:** persist a compact evidence receipt/observation bound to immutable identifiers.
10. **REPEAT:** continue the loop for the next state/window until the declared stopping condition is reached.

A failed execution is an observation. Do not automatically rerun merely to make dashboards green. Rerun only when retry policy or a new diagnosis warrants it, and record the retry as a separate event.

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
- every continuation window must emit runtime evidence sufficient to prove the page actually executed and advanced.

## Quality-first measurement

Time is a performance dimension, not a quality proxy. Throughput metrics such as TCV, WTCV, RPI, action density, parallel yield, ATES, TPV, CIE, tool delay, and handoff latency must be interpreted with outcome, integration, validation, realization, attribution confidence, retries, conflicts, and human intervention. Never introduce a speed-only promotion gate.

Complexity-adjusted comparisons should prefer explicit task complexity when available; otherwise use a documented structural fallback and preserve the raw inputs. Never silently substitute missing complexity with zero.

## Runtime observers

Existing watcher infrastructure should be reused and extended rather than bypassed. Incident-only watchers are insufficient for autonomous loops: progression observers must capture **requested → queued → in_progress → completed**, current job/step evidence, artifact availability, and final outcome. Observer workflows must not execute untrusted candidate code.

## Rollback/recovery

A deletion is not automatically a rollback. Compare the target against the baseline, identify exact removed paths, classify each as authoritative source, generated evidence, intentional replacement, or unknown, and preserve forensic evidence before replacement. Correct forward when possible.

## Safety

Do not execute untrusted PR code from the control plane. Keep observer permissions read-only except narrowly scoped notification writes. Any mutating reconciliation must occur in a separately reviewed workflow with explicit authorization and conflict-stop behavior.

## State distinctions

`COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` are independent states. Never infer validation from commit existence or promotion from mergeability metadata. Likewise, `DISPATCHED`/`QUEUED`/`IN_PROGRESS` are runtime states, not evidence of effect.
