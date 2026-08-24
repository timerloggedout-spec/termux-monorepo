# Agent Team Orchestration

## Purpose

`termux-monorepo` is an Agentic Development Environment. The optimization target is **teamwork**, not raw model popularity or nominal API price.

A useful route is the one that produces a correct, integrated change with the least wasted human/agent time, redundant context, conflicting edits, retries, and feedback cycles.

## Moneyball / 3L0 model

Treat each agent/model/provider as a player and each orchestration policy as a manager. Managers compete through controlled multivariate experiments; weak policies are culled and strong policies are cherry-picked into the next generation.

The custom 3L0 score is an inference matrix, not a claim of objective model intelligence. It should combine:

- task outcome / acceptance
- useful feedback cycles
- time to integrated result
- latency and requests used
- retry / failure rate
- conflict and duplicate-work rate
- human intervention
- context efficiency
- attribution confidence
- provider availability and quota

`$0` is therefore **not** the ROI metric. Free capacity is valuable only when its return on effort/time/context is better.

## Team roles

### Manager

Chooses a coordinated plan: sequencing, parallelism, waiting, escalation, and culling. A manager should optimize the whole workstream rather than maximize calls.

### Router

Selects an eligible provider/model from the current live catalog. Model IDs are **data**, not architecture. No model should be hardcoded as a permanent special route when it can be selected from catalog state.

### Specialists

Gemini CLI, OpenRouter peers, OmniRoute, Jules, Felo models, and other agents are specialists. Jules is an escalation/specialist worker, not the default sink for every task.

### Evidence collector

Records actual invocations and outcomes. A declared route earns no performance credit until it actually executes.

## Dynamic libraries and parallelism

The provider/model library is continuously expanding. `continuous-evaluation.yml` therefore builds its MVT matrix from the **live provider catalogs on every run** instead of maintaining a fixed five-model list.

A newly discovered eligible model can become a treatment automatically; a disappeared model becomes stale/unavailable evidence rather than a permanent routing failure.

The workflow deliberately does **not** specify `strategy.max-parallel`. GitHub's default behavior maximizes matrix jobs according to runner availability. GitHub still imposes platform/account limits, including a documented maximum of 256 matrix jobs per workflow run; those are platform constraints, not an application-imposed concurrency ceiling. The manager should optimize admission, quota, cooldown, and sequencing rather than encode an arbitrary local `max-parallel` number.

The long-term matrix is:

`project + scope + task + cohort + provider + model + prompt + manager + sequencing + validation`

This permits simultaneous A..Z lanes when capacity and task independence justify them while retaining the ability to wait when downstream context depends on another lane.

## Synchrony, not fallback drift

The intended behavior is cooperative orchestration:

1. classify the work
2. split independent work
3. run genuinely independent tasks concurrently
4. wait when downstream context depends on another agent
5. ingest the useful response once
6. integrate once
7. escalate only when the team lacks a needed capability

"Fallback" should not mean a permanent hierarchy such as Gemini-primary → OpenRouter-secondary → Jules. It should mean **dynamic recovery from unavailable capacity or an unmet capability**.

The conductor must prevent duplicate work, conflicting writers, stale-SHA work, needless parallel prompt consumption, and quota waste.

## Adaptive waiting / steering

Latency is primarily a **lead/lag and control signal**, not a correctness score.

A long-running task should continue while it produces useful state change, evidence, computation, or a changing response. A manager should distinguish:

- progressing → keep waiting
- useful new evidence → keep waiting
- slow but active → keep waiting
- repeated identical state → investigate loop
- no evidence + repeated action → steer/retry conditionally
- verified failure → diagnose and route

There is no arbitrary short request timeout in the HTTP invocation action. Provider/model output is requested up to the currently observed capability rather than a fixed 4096-token ceiling; actual `finish_reason`, output tokens, and provider constraints remain separate observations.

## Live provider/quota evidence

Catalog polling is dynamic and provenance-bearing. It records model IDs, context, published pricing/access classifications, documented trial evidence, discovery timestamps, and safe provider response metadata.

For Felo, the current official OX Alpha documentation identifies model `ox-alpha` as a free-trial route with 1M context and 128K maximum output. The public Felo Harness documentation also documents 200 daily free credits for Free Standard accounts for Search API; **account-level remaining balance is not assumed from that public entitlement**. Account/quota state must be treated as observed only when the authenticated provider API or response headers actually exposes it.

Every invocation records safe operational metadata such as request ID, rate-limit/quota/credit response headers when present, HTTP status, tokens, completion state, and error class. Credentials are never persisted.

If an authoritative Felo account/balance endpoint becomes documented or discoverable, the catalog/manager should add it as an explicit account-observation source rather than guessing a dashboard endpoint.

## Agent attribution

GitHub commits/comments may be authored through the repository owner's PAT and therefore appear under `timerloggedout-spec`. Git identity alone is insufficient attribution.

Build a provenance layer that correlates:

- workflow run/job/step
- event and issue/PR number
- head SHA
- commit SHA and parent
- comment timestamp/body markers
- workflow actor and triggering actor
- provider/model invocation telemetry
- session/export provenance when available

The provenance layer must expose an **attribution confidence** value rather than pretending uncertain identity is known.

Chat/session export harvesting, fragment matching, and provenance reconstruction can be used as a conceptual template for backfilling historical agent attribution. Historical attribution must remain explicitly inferred.

## Performance index

The performance index has two populations:

1. **execution observations** — what actually ran
2. **interaction observations** — what each agent contributed to the integrated result

Do not score an agent merely because a workflow claims it selected that agent.

Minimum observation identity:

`manager + task + role + provider + model + workflow_run + head_sha`

Recommended experiment identity:

`manager + policy_version + cohort + task_family + task_instance`

This permits multivariate testing of manager policies, model mixes, prompt budgets, concurrency, and sequencing.

## Task outcome and evidence quality

`PASS/FAIL` is the task-level outcome and must carry notes/evidence. It is not interchangeable with route execution status.

An observation should distinguish, where relevant:

- task outcome: PASS / FAIL / UNKNOWN
- correctness / working state
- tests and verification
- warnings/errors and severity
- integration status
- relevant Big-O / compute characteristics
- requests/tokens/quota consumption
- context/prompt efficiency
- human intervention
- latency
- provider/dispatch/manager failure class

Latency never upgrades a wrong result. A slow verified result can outrank a fast incorrect result.

## Promotion / culling

Managers should be promoted only after sufficient observations and should be compared on confidence intervals or equivalent uncertainty-aware statistics. Do not crown a model after one successful run.

Cherry-pick useful policies into the next experiment generation. Cull policies that repeatedly waste requests, create conflicts, require excessive human intervention, or fail to integrate results.

## OpenRouter / Felo promotional capacity

Promotional/free capacity is an experiment opportunity, not a hardcoded route. The catalog must record promotion metadata when available:

- provider
- model
- pricing classification
- promotion identifier
- start/end time if published
- discovery timestamp
- source URL
- eligibility/terms

The scheduler should exploit a verified promotional window while it is open, but must degrade gracefully when it expires. No workflow should require a promotional model by name.

`FELO_AI_API` is treated as an available provider credential when a workflow explicitly supports that provider; secrets are never written to source, logs, artifacts, or telemetry.

## Human UX and agent sovereignty

Agents should have clear bounded authority, observable decisions, and durable handoff state. Humans should be able to inspect why an agent was selected, what it consumed, what it produced, and why another agent was or was not invoked.

The goal is an environment where agent autonomy and human UX reinforce each other rather than competing.
