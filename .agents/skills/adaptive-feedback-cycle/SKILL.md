---
name: adaptive-feedback-cycle
description: Continuously improve agentic GitHub development by observing workflow runs/jobs/logs, classifying evidence, adapting wait/retry/steering behavior, preserving provenance, and feeding validated improvements forward. This skill is intentionally versioned and continually updated from production observations.
---

# Adaptive Feedback Cycle

## Purpose

Operate the repository as an agentic development environment. The objective is compounding production improvements, not merely fast responses or green workflow badges.

## Historical evaluation scope

**Every observable GitHub event is eligible for continuous historical evaluation.** Do not use a single issue, PR, benchmark, or incident as the historical boundary. The minimum population is issues, issue comments, pull requests, commits, reviews, review comments, branches, workflow runs, jobs, steps, artifacts, benchmark cases, fork lineage, and their temporal relationships. A case study such as #390 is a stress specimen for a particular failure mode; it is not the corpus boundary.

The canonical join substrate is SHA/refs + stable GitHub object IDs + workflow/run/job/artifact IDs + timestamps. Preserve both positive and negative attempts. A missing correlation is evidence of an observability gap, not permission to discard the event.

`.github/workflows/historical-evaluation-correlation.yml` produces periodic immutable correlation snapshots and checks workflow references documented under `docs/`. `docs/ops/ACTIONS-HISTORICAL-CORRELATION.md` defines the matrix. The historical ledger answers **what happened**; AEF/MVT/DOE answers **under which treatment and with what outcome**.

## Non-negotiable priority

1. Correct, working implementation.
2. Verified task outcome and integration.
3. Tests, invariants, warnings/errors and severity.
4. Rework/feedback efficiency and human intervention avoided where policy permits.
5. Relevant complexity/compute/resource use.
6. Context and prompt-ingestion efficiency.
7. Provider/request cost and quota efficiency.
8. Latency.

Latency is primarily a control/diagnostic signal. Long execution is acceptable when useful evidence is accumulating. Repeated identical activity, no-progress intervals, retry storms, deadlocks, or exhausted provider quotas are stall/loop signals.

## Universal resource/model policy

Apply the same evidence model to **every** provider, API/library, model, agent, router, catalog, quota system, execution lane, benchmark, dataset, environment, and user-owned fork that may become a treatment or implementation reference. No provider, agent, or fork gets a hardcoded exception merely because it is currently favored.

Poll authoritative availability/catalog metadata whenever supported. Discover new models/libraries/providers and relevant user-owned forks automatically; newly discovered candidates enter Scout research and cohort classification rather than silently becoming production routing rules. Disappeared or unavailable entries become stale/unavailable observations. Preserve historical identities so longitudinal MVT results remain comparable.

Never encode an arbitrary application-level response, concurrency, provider count, model-count, benchmark-instance, or fork-count ceiling. Requested output may use the highest capability reported by current provider/model metadata; current production invocation requests 131072 output tokens (128 Ki tokens) when the provider accepts the parameter. This is not a universal capability claim. Actual provider/model capability, request acceptance, finish reason, output tokens, truncation, and errors are independent observations. If an experiment intentionally varies output length or concurrency, that is an explicit MVT dimension with a recorded justification, not a hidden budget.

## Continuous loop

```text
OBSERVE -> CLASSIFY -> WAIT/STEER/RETRY -> VERIFY -> PROMOTE OR QUARANTINE -> FEED FORWARD -> REPEAT UNTIL DESIRED OUTCOME IS CONFIRMED
```

The loop does not terminate because one command returned successfully. It terminates when the requested outcome is verified, or when a documented terminal condition makes the desired outcome impossible without new authority/input. Multiple workflow runs, experiments, retries, refinements, and manager changes are expected within a cycle.

## Observe

For every relevant GitHub event and every provider request, capture event type/action and timestamp, workflow run/attempt/job/step, repository SHA/ref and workflow revision, manager policy and agent/provider/model identity, prompt/context variant and experiment ID, artifact/log evidence, outcome/warnings/errors, lead/lag timestamps, request count, catalog revision, and provider/quota/rate-limit evidence. Record cooldown/debounce state and why admission/wait/skip occurred. Never infer success from workflow/job `success` alone.

For each event class, build explicit edges rather than only a flat activity log:

```text
issue/comment <-> PR/review/comment <-> commit/SHA <-> workflow/run/job/step <-> artifact
       \                                              /
        \-> benchmark/task/treatment -> evaluator -> outcome
branch/ref/fork lineage ----------------------------^ 
```

This graph is longitudinal: later evidence may update the evaluation of an earlier event, but never rewrite the original observation.

## Classify

Use separate states for dispatch/event/run/job/provider request/response, provider capability, pricing, trial, account entitlement, quota, model execution, response completeness, correctness, tests, integration, manager/orchestration, context/prompt quality, infrastructure, benchmark/dataset version, and fork lineage. Use `PASS`, `FAIL`, `UNKNOWN`, `WARNING`, `SKIPPED`, or `STALLED` with notes. Do not collapse policy health, catalog availability, entitlement, execution, task correctness, or benchmark validity.

## MVT population, dynamic libraries, benchmarks, and quota-aware lanes

Treat the experiment as a categorical/subcategory matrix:

```text
agent × provider × model × prompt × manager × cohort × sequencing
```

This is extensible. Future dimensions may include task type, repository scope, validation class, bug-bounty/help-wanted/CTF treatment, reviewer, tool-chain, context strategy, benchmark family/version, environment image, fork revision, and other experimentally justified factors.

The provider/model/library/agent/benchmark population is live data, not a fixed roster. Poll current catalogs/availability and generate the eligible MVT population. Newly discovered eligible models, agents, benchmark variants, and user-owned reference forks are incorporated into Scout/cohort discovery automatically; disappeared entries are recorded as stale/unavailable evidence. OX Alpha and any other model are selectable treatments, never permanent router rules.

## Adaptive waiting and multiple-run cycles

Do not use a fixed short timeout merely because a response is slow. Wait while progress/evidence changes; re-check run/job state and timestamps; extend useful long-running work within platform/task constraints; detect stalls via lack of state/log/artifact progress, repeated identical retries, deadlocks, or deadline exhaustion; retry only when informative; prefer a fresh experiment variant when better than identical regeneration; preserve every attempt; and run multiple validation cycles for orchestration/provider changes. After each run inspect jobs -> steps -> logs -> artifacts -> receipts -> resulting SHA/status before deciding to wait, steer, retry, refine, or promote. Latency is diagnostic; correctness is promotion priority.

## Existing cooldown intelligence is feed-forward

Before inventing timing policy, inspect prior SSOTs, decision matrices, agent responses, command libraries, cooldowns, debounces, quota gates, and orchestration receipts. Historical values are evidence, not immutable constants. Ingest prior observations; distinguish provider cooldown from orchestration debounce; avoid re-admission during known cooldown unless deliberately experimenting; record why waiting/skipping occurred; adapt when evidence disproves old timing; cull low-ROI treatments while retaining evidence; and reintroduce treatments when new availability/capability evidence changes expected value.

## Reconnaissance before implementation

Before changing production orchestration, inspect **all relevant existing skills and process artifacts**, not just this skill. Search `.agents/skills/`, context-relationship graph skills including naming variants, SSOTs, decision matrices, Mermaid/process diagrams, command libraries, agent-manager documents, provider adapters, cooldown/quota code, benchmark registries, evaluation contracts, and recent agent-authored commits. Treat workflow definitions and documentation that references them as coupled artifacts.

Treat other agents' recent commits, comments, reviews, and workflow artifacts as operational intelligence. Agent attribution requires provenance/confidence evidence; shared-PAT GitHub identity alone is insufficient.

## GitHub audit model

Maintain one continuous audit PR/specimen where practical. Audit **every event**, not merely the current PR or a selected case study, and feed findings forward. Automated workflows are the default; there is **no manual audit gate** in the production loop. A human may inspect or steer, but the system continues without synchronous approval when policy permits.

## Promotion gate and task outcome

A candidate is promotable only when evidence supports the requested task outcome and correctness/integration gates. Provider availability, HTTP 200, workflow success, response length, low latency, or resource efficiency are not sufficient.

Represent task outcome as `PASS / FAIL + notes` when verification is possible, while separately recording correctness, warning/error rate and severity, relevant complexity/Big-O or compute, integration/test status, rework/feedback cycles, context efficiency, request/quota efficiency, and latency. Preserve `UNKNOWN` when verification is unavailable.

## Continual update contract: the 12-step production loop

1. Inspect current GitHub state.
2. Read other agents' recent commits, comments, reviews, and artifacts.
3. Search historical SSOTs, decision matrices, Mermaid/process records, cooldowns, command libraries, and related skills before inventing a mechanism.
4. Verify current provider/library/model catalogs and authoritative documentation.
5. Check SHA ↔ run ↔ workflow-revision correlation before interpreting results.
6. Make the smallest evidence-backed improvement that advances the desired outcome.
7. Commit the improvement with a specific message.
8. Wait adaptively; do not confuse elapsed time with failure.
9. Inspect jobs -> steps -> logs -> artifacts -> receipts and every relevant provider request.
10. Record what was proven, disproven, changed, and what remains unproven.
11. Update this skill and related SSOT/graph documentation when the process itself improves.
12. **LOOP — repeat until the desired outcome is confirmed**, running multiple validation cycles and continuing to improve rather than stopping at the first green-looking signal.

The skill is a living operational contract, not a frozen tutorial.
