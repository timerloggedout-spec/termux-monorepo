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

Latency is primarily a control/diagnostic signal. Long execution is acceptable when useful evidence is accumulating. Repeated identical activity, no-progress intervals, retry storms, deadlocks, or exhausted budgets are stall/loop signals.

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

Never infer success from a workflow/job `success` alone.

### Classify

Use separate states for:

- dispatch requested / event observed / run created / job started / provider request / response received
- provider capability or entitlement
- model execution
- response completeness
- correctness
- tests
- integration
- manager/orchestration
- context/prompt quality
- infrastructure

Use `PASS`, `FAIL`, `UNKNOWN`, `WARNING`, `SKIPPED`, or `STALLED` with notes. A disabled paid probe can be policy-healthy while its capability remains unknown.

### Adaptive waiting

Do not use a fixed short timeout merely because a response is slow.

- Wait while progress/evidence is changing.
- Re-check run/job state and timestamps before acting.
- Extend waiting for long-running useful work within the configured task budget.
- Detect stalls using lack of state/log/artifact progress, repeated identical retries, or deadline exhaustion.
- Retry only when the failure class is retryable and the retry is likely to add information.
- Prefer a fresh experiment variant when regeneration is more informative than an identical retry.
- Preserve every attempt and its evidence.

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

### MVT / Moneyball

Run simultaneous lanes when capacity permits. Vary provider/model, prompt/context, manager, task cohort, and sequencing deliberately. Record the justification for each prompt/context variation. Compare task outcome and correctness before latency.

### Context-ingestion efficiency

Construct prompts from stable context plus relevant delta:

```text
stable context + new delta + unresolved findings + relevant history
```

Track context scope, token/size estimates when available, historical depth, exclusions, and why a variation was selected. Avoid repeatedly shipping unchanged history.

### GitHub audit model

Maintain one continuous audit PR/specimen where practical. Audit every event on that PR and feed findings forward. Automated workflows are the default; there is no manual audit gate in the production loop. A human may inspect or steer, but the system must continue without synchronous approval when policy allows.

### Regression rule

No rollback of evidence. A later improvement must reference the prior observation and preserve its artifacts. A regression is a new finding that triggers diagnosis and a successor change.

### Promotion gate

A candidate is promotable only when the evidence supports the requested task outcome and correctness/integration gates. Provider availability, HTTP 200, workflow success, or low latency are not sufficient.

## Continual update contract

When this skill is used in production:

1. Inspect current GitHub state before acting.
2. Read recent commits from other agents before editing.
3. Check run timestamp vs. tested SHA before interpreting results.
4. Make the smallest evidence-backed improvement.
5. Commit the improvement with a specific message.
6. Wait for the resulting automation to execute.
7. Inspect jobs, steps, logs, artifacts and receipts.
8. Record what was proven and what remains unproven.
9. Update this skill when the process itself improves.

The skill is a living operational contract, not a frozen tutorial.
