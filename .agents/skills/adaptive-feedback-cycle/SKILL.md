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

## Output policy

Never impose an arbitrary artificial response ceiling merely to make a benchmark finish faster. The request may use the highest response capacity the provider/model metadata supports; the current production default is **131072 requested output tokens (128 Ki tokens)** for the OpenAI-compatible invocation action. This is a requested maximum, not a claim that every provider/model supports it. Provider/model capability and actual `finish_reason`, output tokens, and truncation are recorded independently.

A provider rejection of a large requested maximum is evidence to classify, not a reason to silently lower the experiment ceiling. If a specific experiment deliberately varies output length, that is an explicit MVT dimension and must record its justification.

## Continuous loop

```text
OBSERVE -> CLASSIFY -> WAIT/STEER/RETRY -> VERIFY -> PROMOTE OR QUARANTINE -> FEED FORWARD
```

### Observe

For every relevant GitHub event, capture:

- event type/action and event timestamp
- workflow run ID, attempt, job ID and step
- repository SHA/ref and workflow revision
- manager policy and agent/provider/model identity when available
- prompt/context variant and experiment ID
- artifact IDs and log evidence
- outcome status and warnings/errors
- lead/lag timestamps
- request count and provider/quota/rate-limit evidence

Never infer success from a workflow/job `success` alone.

### Classify

Use separate states for:

- dispatch requested / event observed / run created / job started / provider request / response received
- provider capability, public pricing, documented trial, account entitlement, and quota
- model execution
- response completeness
- correctness
- tests
- integration
- manager/orchestration
- context/prompt quality
- infrastructure

Use `PASS`, `FAIL`, `UNKNOWN`, `WARNING`, `SKIPPED`, or `STALLED` with notes. A disabled paid probe can be policy-healthy while its capability remains unknown. A documented free trial can be a positive catalog/access observation while an individual request failure remains an execution failure. Do not collapse those states.

### MVT population and quota-aware lanes

Treat the experiment as a categorical/subcategory matrix:

```text
provider × model × prompt × manager × cohort × sequencing
```

Add explicit treatment lanes when capacity permits. The current team evaluation has five simultaneous lanes:

1. OpenRouter OX Alpha.
2. OpenRouter independent free/zero-price peer.
3. Felo OX Alpha.
4. Omni/free-or-zero peer when available.
5. Felo independent non-OX peer using the included daily quota opportunity.

Every provider request must produce telemetry containing provider, model, experiment/lane identity, request count, response status, quota/rate-limit evidence, and timestamps. Never assume a quota amount from a secret's existence; record observed entitlement/capacity evidence and reconcile it against provider documentation when available.

### Adaptive waiting

Do not use a fixed short timeout merely because a response is slow.

- Wait while progress/evidence is changing.
- Re-check run/job state and timestamps before acting.
- Extend waiting for long-running useful work within the configured task/run ceiling.
- Detect stalls using lack of state/log/artifact progress, repeated identical retries, deadlocks, or deadline exhaustion.
- Retry only when the failure class is retryable and the retry is likely to add information.
- Prefer a fresh experiment variant when regeneration is more informative than an identical retry.
- Preserve every attempt and its evidence.
- Latency is diagnostic; correctness remains the promotion priority.

### Steering

When steering is available, send a bounded correction that references the current evidence. Do not erase or rewrite prior attempts. A steering action must produce a new event/observation and remain linked to the preceding attempt.

### ChronoMancer/time-loop compatibility

Chat-session time loops may consolidate a winning continuation into an earlier conversational trunk while preserving the original branches. GitHub must translate this into provenance-preserving artifacts:

```text
X
├── attempt A -> SHA A
├── attempt B -> SHA B
└── attempt C -> SHA C <- promoted trunk
```

Never rewrite Git history solely to make the timeline appear linear. Promotion means selecting the validated successor, not deleting unsuccessful evidence.

### Context-ingestion efficiency

Construct prompts from stable context plus relevant delta:

```text
stable context + new delta + unresolved findings + relevant history
```

Track context scope, token/size estimates when available, historical depth, exclusions, and why a variation was selected. Avoid repeatedly shipping unchanged history. Prompt variations require an explicit experimental justification.

### GitHub audit model

Maintain one continuous audit PR/specimen where practical. Audit every event on that PR and feed findings forward. Automated workflows are the default; there is **no manual audit gate** in the production loop. A human may inspect or steer, but the system must continue without synchronous approval when policy allows.

### Regression rule

No rollback of evidence. A later improvement must reference the prior observation and preserve its artifacts. A regression is a new finding that triggers diagnosis and a successor change.

### Promotion gate

A candidate is promotable only when the evidence supports the requested task outcome and correctness/integration gates. Provider availability, HTTP 200, workflow success, response length, or low latency are not sufficient.

Task outcome should be represented as `PASS` or `FAIL` with notes when verification is possible, and related evidence should separately capture correctness, warning/error rate and severity, relevant complexity/Big-O or compute considerations, integration/test status, and rework.

## Continual update contract

When this skill is used in production:

1. Inspect current GitHub state before acting.
2. Read recent commits from other agents before editing.
3. Verify current provider catalogs/documentation before classifying access.
4. Check run timestamp vs. tested SHA and workflow revision before interpreting results.
5. Make the smallest evidence-backed improvement.
6. Commit the improvement with a specific message.
7. Wait for resulting automation using adaptive observation rather than a fixed short timeout.
8. Inspect jobs, steps, logs, artifacts and receipts.
9. Record what was proven and what remains unproven.
10. Update this skill when the process itself improves.

The skill is a living operational contract, not a frozen tutorial.
