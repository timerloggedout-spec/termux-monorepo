# GitHub Actions Run Observability

## Current state

`she.ingest.actions` already provides the repository's observer-side normalization for `workflow_run` / job events into stable Incident records, with deterministic fingerprints and evidence references. The Self-Healing Engine roadmap treats this as P0.2 event ingestion; recovery, verification, learning, attestation, and promotion remain separately gated contracts.

`Actions Run Watcher — incident notification` (`.github/workflows/actions-run-watcher.yml`) is the operational notification edge. It listens for completed runs, but only creates or updates an incident for `failure`, `timed_out`, or `action_required` conclusions. Routine `cancelled` runs are observed without incident notification because concurrency cancellation is an expected operational state in this repository. The watcher is intentionally observer/notification-only and does not bypass SHE authority or verification gates.

The watcher keeps its incident filter at the **step level** rather than making the whole job conditional. This keeps the observer job runnable for every completed event while limiting issue writes and incident receipts to the explicit incident conclusion set.

## Conclusion policy

| Conclusion | Watcher behavior | Rationale |
|---|---|---|
| `failure` | incident notification + structured receipt | actionable workflow failure |
| `timed_out` | incident notification + structured receipt | actionable execution timeout |
| `action_required` | incident notification + structured receipt | explicit human/action gate |
| `cancelled` | observation only | routine concurrency cancellation is not itself a failure |
| `success`, `skipped`, `neutral` | observation only | non-incident completion |
| unfinished / missing | not emitted by `completed` trigger | outside this watcher contract |

This distinction is specific to the notification edge. Other repository metrics may intentionally count cancellation as a separate operational signal; those metrics must not be conflated with incident notification.

## Evidence contract

The watcher should be treated as the first notification surface, not the canonical evaluation ledger. Correlation remains:

`issue/comment ↔ PR/review ↔ commit/SHA ↔ workflow/run/job/step ↔ artifact ↔ benchmark/treatment/evaluator`

Minimum useful run evidence is:

- repository/ref and head SHA;
- workflow identity and revision;
- workflow run and attempt;
- job/step identity when available;
- stable failure fingerprint;
- run URL and artifact/log references;
- provider/model/manager/treatment identity when the run is an experiment;
- timestamps and wait/retry/skip rationale;
- outcome separate from operational conclusion.

## GitHub semantics note

A skipped GitHub Actions **job** is reported as `Success`; therefore the historical hypothesis that a job-level `if` on this watcher caused an otherwise empty workflow to become a failed run is not supported by GitHub's documented job-skipping semantics. The production fix here addresses the concrete notification-noise defect—treating routine `cancelled` completions as incidents—rather than relying on an unsupported zero-jobs-failed premise.

## Grafana / OTLP / Sentry implementation note

Observability integrations discovered in `*_fork` templates, including Grafana/OTLP and Sentry-oriented reporting, are **reference integrations, not unconditional production dependencies**. The `gh-aw_fork` audit demonstrated why: importing a shared OTLP fragment can silently make workflows depend on environment-specific telemetry secrets.

The target architecture should therefore use capability-gated telemetry:

1. emit local structured evidence first;
2. preserve run/job/step IDs and stable correlation keys;
3. export OTLP metrics/traces/logs only when an explicitly configured telemetry endpoint is available;
4. support Grafana as a visualization/query target through the configured OTLP-compatible path;
5. support Sentry for error/event correlation where configured;
6. never make benchmark correctness or workflow execution depend on telemetry availability;
7. never persist authorization headers, API keys, or tokens in evidence;
8. record telemetry availability as an infrastructure signal, not a task-quality score.

Candidate telemetry dimensions include workflow conclusion, job duration, queue/wait time, retry count, stalled interval, provider/model lane, experiment/cohort/treatment ID, correctness outcome, regression state, and resource/quota observations. High-cardinality identifiers should remain in traces/logs rather than becoming unbounded metric labels.

## MVT / DOE integration

The Actions watcher and telemetry layer must not flatten MVT/DOE into a collection of green/red workflow badges. AEF defines evaluation identity and explicitly links provider/model, prompt/version, manager, workflow/run/job/step, logs/artifacts, evaluator, and outcome. DOE requires explicit hypotheses, factor levels, treatment assignment, stable cohorts, sequencing, repetition, and preservation of skipped/unavailable/censored observations.

For provider/model experiments, distinguish:

`admission → execution → response completeness → correctness → integration → regression → resource cost`

A skipped route is not a model failure. HTTP success is not task success. Telemetry latency is not correctness.

## BIUDL / continuous loop

```text
OBSERVE
  ↓
CORRELATE
  ↓
CLASSIFY
  ↓
WAIT / STEER / RETRY
  ↓
VERIFY
  ↓
PROMOTE or QUARANTINE
  ↓
FEED FORWARD
  ↺
```

This document records the observability implementation boundary so future fork reconciliation can reuse useful Grafana/OTLP/Sentry patterns without inheriting their secret or runtime assumptions.

## Related SSOTs

- `docs/architecture/SELF-HEALING-ENGINE-ROADMAP.md`
- `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md`
- `.agents/skills/adaptive-feedback-cycle/SKILL.md`
- `.agents/skills/multivariate-doe/SKILL.md`
- `she/ingest/actions.py`
- `.github/workflows/actions-run-watcher.yml`
