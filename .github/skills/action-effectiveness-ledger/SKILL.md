# Action Effectiveness Ledger Skill

## Purpose

Measure orchestration actions by observable effect and outcome rather than raw commit/comment volume. The ledger is a **measurement component of the historical evidence corpus**, not the corpus itself and not the Moneyball/3L0 decision engine.

## System position

`GitHub history + workflow telemetry + provider/session provenance`
→ **historical evidence corpus**
→ `PR/issue observations`
→ `DOE/MVT experiment cohorts`
→ `Moneyball/3L0 inference`
→ `learning records / manager evolution`
→ `next orchestration policy`

A human-readable receipt is a projection of one observation/promotion event. It must never be treated as the complete historical record.

## Required sequence

`RECON → MEASURE → CLASSIFY → PLAN → ACT → WAIT → VALIDATE → RE-MEASURE → COMPARE → REPEAT`

For experimental lanes, bind the same sequence to an immutable candidate SHA and fixed baseline.

## Evidence identity

Every cycle is anchored to:

- PR number or issue/task identifier;
- selected base SHA;
- current head SHA;
- merge-base SHA;
- observation timestamp;
- experiment/cohort ID when applicable;
- provenance/attribution confidence.

Never make a current-state decision from an unverified or stale head SHA.

## Historical corpus contract

Every PR/issue is an **observation candidate**, including closed, merged, superseded, stale, or failed work. The corpus records metadata and evidence relationships; it does not require a heavyweight Markdown receipt per PR.

At minimum, a PR observation should preserve:

- immutable head/base/merge-base identity where available;
- lifecycle state and promotion disposition;
- commit/change accounting;
- issue comments, reviews, review comments, and check/action evidence counts and timestamps;
- exact GitHub evidence URLs/IDs;
- Action→Effect temporal associations;
- attribution confidence;
- collection bounds and known omissions.

Do not persist raw discussion bodies in the corpus. Keep extracted reference tokens in memory and retain only the metadata needed to reproduce the relationship.

## Change accounting

Walk the complete merge-base-to-head commit range when the objects are available. For every commit classify its tree effect as:

- `EMPTY`: no file/tree delta;
- `METADATA_ONLY`: file/tree metadata changes without textual additions/deletions;
- `EFFECTIVE`: substantive tree/content delta.

Record both cumulative historical churn and final base-to-head retained diff.

## Action accounting

Treat comments, reviews, provider requests, workflow dispatches, and agent instructions as actions/evidence—not completed work. Correlate them with subsequent commits and validation.

Recommended outcome classes:

`NOOP`, `DISCUSSION_ONLY`, `METADATA_ONLY`, `ACTION_EXECUTED`, `ACTION_VALIDATED`, `ACTION_RESOLVED`, `ACTION_REGRESSED`, `STALE_ACTION`, `PROVIDER_PENDING`, `UNVERIFIED`.

## Metrics

Track:

- no-op + metadata rate;
- gross churn;
- retained final diff;
- churn-to-retained-diff realization;
- actionable-action count;
- action yield;
- resolution yield;
- regression rate;
- review/check evidence freshness;
- alignment delta;
- time-to-integration;
- useful/duplicate cycles;
- retries, conflicts, provider failures, model failures;
- human intervention;
- attribution confidence.

Do not score PR quality from commit count, comment count, or diff size alone. PR size is context.

## Moneyball / 3L0 boundary

Moneyball/3L0 consumes corpus observations and experiment results. It scores integrated outcomes, not activity:

`outcome + integration + time + useful cycles + context efficiency + retries + conflicts + human intervention + attribution confidence`

Do not turn a provider/model leaderboard into a production authority. Compare **manager/orchestration policies** on comparable cohorts, retain experiment history, and use learning records to inform the next policy.

## Safety

Telemetry workflows must not execute PR source. Use trusted control-plane code and read Git objects as data. Do not auto-merge, close, delete, force-push, revoke credentials, or rotate secrets.

## State distinctions

Always distinguish:

- `COMMITTED`: repository mutation exists at a known SHA.
- `EXECUTED`: a relevant workflow/job actually ran.
- `VALIDATED`: objective checks/evidence confirm the intended result.
- `PROMOTED`: the result was deliberately merged/deployed/promoted.

Never infer one state from another.

## Corpus/receipt rule

`receipt != corpus`.

A receipt is a durable projection of an observation. The historical corpus is the longitudinal substrate from which receipts, experiments, learning, and manager comparisons are derived.

## Closeout

A cycle is not complete merely because a comment was posted, a provider was dispatched, or a commit exists. Re-fetch the current SHA, validate objective evidence, compare against the previous observation, classify the effect, and retain the result for future cohorts.
