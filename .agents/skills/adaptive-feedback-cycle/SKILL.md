---
name: adaptive-feedback-cycle
description: Continuously improve agentic GitHub development by observing workflow runs/jobs/logs, classifying evidence, adapting wait/retry/steering behavior, preserving provenance, and feeding validated improvements forward. This skill is intentionally versioned and continually updated from production observations.
---

# Adaptive Feedback Cycle

## Purpose

Operate the repository as an agentic development environment. The objective is compounding production improvements, not merely fast responses or green workflow badges.

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

Do not use a generic "budget" abstraction to silently constrain work. Provider quotas, credits, rate limits, runner capacity, API limits, account entitlements, dataset availability, and benchmark platform limits are distinct resources and must be measured independently. A platform limit is infrastructure evidence, not an application policy ceiling.

## Continuous loop

```text
OBSERVE -> CLASSIFY -> WAIT/STEER/RETRY -> VERIFY -> PROMOTE OR QUARANTINE -> FEED FORWARD -> REPEAT UNTIL DESIRED OUTCOME IS CONFIRMED
```

The loop does not terminate because one command returned successfully. It terminates when the requested outcome is verified, or when a documented terminal condition makes the desired outcome impossible without new authority/input. Multiple workflow runs, experiments, retries, refinements, and manager changes are expected within a cycle.

## Observe

For every relevant GitHub event and every provider request, capture event type/action and timestamp, workflow run/attempt/job/step, repository SHA/ref and workflow revision, manager policy and agent/provider/model identity, prompt/context variant and experiment ID, artifact/log evidence, outcome/warnings/errors, lead/lag timestamps, request count, catalog revision, and provider/quota/rate-limit evidence. Record cooldown/debounce state and why admission/wait/skip occurred. Never infer success from workflow/job `success` alone.

## Classify

Use separate states for dispatch/event/run/job/provider request/response, provider capability, pricing, trial, account entitlement, quota, model execution, response completeness, correctness, tests, integration, manager/orchestration, context/prompt quality, infrastructure, benchmark/dataset version, and fork lineage. Use `PASS`, `FAIL`, `UNKNOWN`, `WARNING`, `SKIPPED`, or `STALLED` with notes. Do not collapse policy health, catalog availability, entitlement, execution, task correctness, or benchmark validity.

## MVT population, dynamic libraries, benchmarks, and quota-aware lanes

Treat the experiment as a categorical/subcategory matrix:

```text
agent × provider × model × prompt × manager × cohort × sequencing
```

This is extensible. Future dimensions may include task type, repository scope, validation class, bug-bounty/help-wanted/CTF treatment, reviewer, tool-chain, context strategy, benchmark family/version, environment image, fork revision, and other experimentally justified factors.

The provider/model/library/agent/benchmark population is live data, not a fixed roster. Poll current catalogs/availability and generate the eligible MVT population. Newly discovered eligible models, agents, benchmark variants, and user-owned reference forks are incorporated into Scout/cohort discovery automatically; disappeared entries are recorded as stale/unavailable evidence. OX Alpha and any other model are selectable treatments, never permanent router rules.

Do not encode a local `max-parallel` ceiling merely to simplify experiments. Expand simultaneous lanes according to current eligible population, runner availability, provider admission, quota, cooldown, benchmark/environment capacity, and manager policy. Platform limits are infrastructure constraints, not application policy ceilings. The manager owns dynamic admission, sequencing, cooldown, quota, culling, and promotion.

Every provider request must produce telemetry containing provider, model, experiment/lane identity, request count, response status, timestamps, and safe quota/rate-limit evidence when exposed. This applies to all libraries/providers/models. Never assume a quota from a secret's existence; record observed entitlement/capacity and reconcile it against authoritative documentation.

## Provider quota/account evidence

Prefer authoritative live account/quota endpoints when documented. If none is documented, do not invent one. Capture safe response headers such as `x-ratelimit-*`, `x-credit-*`, `x-quota-*`, `x-remaining-*`, `retry-after`, and request IDs when exposed; never persist authorization headers or secrets.

For every provider keep separate evidence classes: documented capability; documented public/free-credit entitlement; authenticated account balance when an authoritative endpoint exists; request-observed credit/quota/rate-limit evidence; and actual execution.

For Felo, public documentation identifies `ox-alpha` as a free-trial route with 1M context and 128K maximum output, and public documentation describes 200 daily free credits for applicable Free Standard Search API accounts. Treat those as documented entitlement evidence, not the authenticated account's current remaining balance. If an authoritative authenticated balance endpoint exists, poll it and reconcile it after each request/cycle; otherwise maintain explicit `balance_unknown` while logging every request's observable quota metadata.

## Adaptive waiting and multiple-run cycles

Do not use a fixed short timeout merely because a response is slow. Wait while progress/evidence changes; re-check run/job state and timestamps; extend useful long-running work within platform/task constraints; detect stalls via lack of state/log/artifact progress, repeated identical retries, deadlocks, or deadline exhaustion; retry only when informative; prefer a fresh experiment variant when better than identical regeneration; preserve every attempt; and run multiple validation cycles for orchestration/provider changes. After each run inspect jobs -> steps -> logs -> artifacts -> receipts -> resulting SHA/status before deciding to wait, steer, retry, refine, or promote. Latency is diagnostic; correctness is promotion priority.

## Existing cooldown intelligence is feed-forward

Before inventing timing policy, inspect prior SSOTs, decision matrices, agent responses, command libraries, cooldowns, debounces, quota gates, and orchestration receipts. Historical values are evidence, not immutable constants. Ingest prior observations; distinguish provider cooldown from orchestration debounce; avoid re-admission during known cooldown unless deliberately experimenting; record why waiting/skipping occurred; adapt when evidence disproves old timing; cull low-ROI treatments while retaining evidence; and reintroduce treatments when new availability/capability evidence changes expected value.

## Reconnaissance before implementation

Before changing production orchestration, inspect **all relevant existing skills and process artifacts**, not just this skill. Search `.agents/skills/`, context-relationship graph skills including naming variants, SSOTs, decision matrices, Mermaid/process diagrams, command libraries, agent-manager documents, provider adapters, cooldown/quota code, benchmark registries, evaluation contracts, and recent agent-authored commits. The repository currently contains the canonical `context-relationship-graph` skill; use its verified-vs-candidate discipline. Do not rely on a remembered filename when GitHub can establish canonical spelling/path.

Treat other agents' recent commits, comments, reviews, workflow artifacts, and command outputs as operational intelligence. Agent attribution requires provenance/confidence evidence; shared-PAT GitHub identity alone is insufficient.

## Steering

When steering is available, send a bounded correction referencing current evidence. Do not erase prior attempts. A steering action produces a new linked observation.

## ChronoMancer/time-loop compatibility

Chat-session time loops may consolidate a winning continuation into an earlier conversational trunk while preserving original branches. GitHub should translate the concept into provenance-preserving artifacts:

```text
X
├── attempt A -> SHA A
├── attempt B -> SHA B
└── attempt C -> SHA C <- promoted trunk
```

Never rewrite Git history solely to make the timeline appear linear. Promotion selects the validated successor; it does not delete unsuccessful evidence.

## Context-ingestion efficiency

Construct prompts from stable context plus relevant delta:

```text
stable context + new delta + unresolved findings + relevant history
```

Track context scope, token/size estimates when available, historical depth, exclusions, and why each variation was selected. Avoid repeatedly shipping unchanged history. Prompt variations require explicit experimental justification. Relationship graphs should connect issues, PRs, commits, comments, reviews, files, workflow runs, jobs, provider/model observations, benchmark/fork lineage, and manager decisions with evidence class and temporal bounds.

## GitHub audit model

Maintain one continuous audit PR/specimen where practical. Audit every event on that PR and feed findings forward. Automated workflows are the default; there is **no manual audit gate** in the production loop. A human may inspect or steer, but the system continues without synchronous approval when policy permits.

## Regression rule

No rollback of evidence. Later improvements reference prior observations and preserve artifacts. A regression is a new finding that triggers diagnosis and a successor change. Never label a change green merely because an error disappeared if the requested outcome remains unverified.

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
