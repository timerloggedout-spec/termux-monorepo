# Action Effectiveness Ledger Skill

## Purpose

Measure orchestration actions by observable effect and outcome rather than raw commit/comment volume.

## Required sequence

`RECON → MEASURE → CLASSIFY → PLAN → ACT → WAIT → VALIDATE → RE-MEASURE → COMPARE → REPEAT`

## Evidence identity

Every cycle is anchored to:

- PR number or issue/task identifier;
- selected base SHA;
- current head SHA;
- merge-base SHA;
- observation timestamp.

Never make a current-state decision from an unverified or stale head SHA.

## Change accounting

Walk the complete merge-base-to-head commit range. For every commit classify its tree effect as:

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
- alignment delta.

Do not score PR quality from commit count, comment count, or diff size alone. PR size is context.

## Safety

Telemetry workflows must not execute PR source. Use trusted control-plane code and read Git objects as data. Do not auto-merge, close, delete, force-push, revoke credentials, or rotate secrets.

## State distinctions

Always distinguish:

- `COMMITTED`: repository mutation exists at a known SHA.
- `EXECUTED`: a relevant workflow/job actually ran.
- `VALIDATED`: objective checks/evidence confirm the intended result.
- `PROMOTED`: the result was deliberately merged/deployed/promoted.

Never infer one state from another.
