# SWE Agent Cohorts

**Role:** reusable external/reference agent cohorts for the Agent Evaluation Framework (AEF).

This registry is deliberately separate from the repository-local development-performance score. SWE-bench-style resolution is a **treatment signal**, not a substitute for integrated repository correctness.

## User-owned fork cohort

| Cohort | Repository | Role | Evidence policy |
|---|---|---|---|
| `swe-agent-fork` | `timerloggedout-spec/SWE-agent_fork` | Full SWE-agent reference implementation; candidate agent treatment | Pin exact revision per trial; record upstream/fork lineage; never treat moving `main` as reproducible evidence. |
| `mini-swe-agent-fork` | `timerloggedout-spec/mini-swe-agent_fork` | Lightweight SWE-agent reference implementation; existing bounded adapter | Pin exact revision; isolate provider credentials; retain only redacted evaluation manifests. |

The repository already contains the bounded mini-SWE reference workflow and contract. The older `feat/swe-performance-evaluation` branch is **lineage evidence**, not a merge target: it diverged from current `master`, so useful files were integrated/reworked on current history rather than merging a stale branch wholesale.

## Benchmark families / cohorts

The external benchmark family should be selectable rather than hard-coded to one leaderboard:

- `swe-bench-full`
- `swe-bench-lite`
- `swe-bench-verified`
- `swe-bench-multimodal`
- `swe-bench-multilingual`
- `swe-bench-live`
- `repository-history`
- `custom-environment`
- `trajectory-validation`
- `deterministic-regression`
- `tool-api-boundary`
- `cognitive-regression`
- `oversight/security`

SWE-bench's public documentation describes Full, Lite, Verified, Multimodal, and Multilingual datasets; SWE-bench-Live adds a live, multi-language/multi-OS direction. External definitions are reference inputs and must be versioned/pinned before being used as a promotion signal.

## MoneyBall / 3L0 treatment model

Each run should produce a row keyed by:

`agent × provider × model × prompt × manager × cohort × sequencing × task_instance × evaluator × blindness_condition`

with separate fields for:

- task outcome: `PASS | FAIL | PARTIAL | UNKNOWN | ERROR`
- patch/test correctness;
- trajectory quality and unnecessary-loop rate;
- tool/API boundary correctness;
- regression/cognitive-regression results;
- resource use: tokens, cost, quota, retries, availability;
- latency as a diagnostic signal, not a correctness gate;
- provenance: source revision, agent revision, task revision, run/job/step, evidence artifact;
- replication count and missingness;
- admission/quarantine decision and reason.

**Do not rank by a single SWE-bench percentage.** MoneyBall should estimate contribution by task family and cohort, with uncertainty and evidence quality attached.

## BIUDL loop

```text
BROAD
  ↓  discover new agents / datasets / environments / tasks
INTEGRATE
  ↓  register pinned treatments + adapters
VALIDATE
  ↓  blinded, reproducible trials + deterministic gates
DEVELOP
  ↓  improve prompts / managers / tools / orchestration
LEARN
  ↓  update MoneyBall / 3L0 + skills + SSOT + cohort registry
  └──────────────→ BROAD
```

### Anti-churn rule

A large PR, issue, or comment history is not automatically a benchmark. Extract a bounded, frozen task with objective acceptance criteria and a known source SHA. Keep the **history stress dimension** separately measurable so context volume can be studied without rewarding churn.

## #390 scenario case study

PR #390 is retained as a **repository-history churn case study**, not as a canonical SWE-bench instance. It is useful because it exposed the need to measure event/comment volume, context reconstruction, relationship discovery, and patch/review effectiveness without confusing activity with value.

The #390 seed belongs in the repository-history cohort and should feed AEF/MoneyBall only after the task boundary, source context, evaluator, and success criteria are frozen.

## Promotion / culling

Cohort evidence may influence MoneyBall/3L0 admission, routing, replication priority, or quarantine. It must never erase provenance. Culling a treatment preserves its observations and reason for exclusion so later BIUDL cycles can re-test it under changed conditions.
