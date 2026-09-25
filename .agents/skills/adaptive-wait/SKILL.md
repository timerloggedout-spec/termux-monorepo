---
name: adaptive-wait
description: Adaptive WAIT for agentic GitHub operations. Re-fetch authoritative state, detect progress or stalls, keep useful disjoint work moving, and promote only from current-SHA evidence.
---

# Adaptive WAIT

Use this skill whenever work is asynchronous: GitHub Actions, reviews, deployments, provider jobs, external agents, or any operation whose next action depends on new state.

## Control objective

Waiting is an evidence-collection phase, not an idle timer. HOLD is not an idle parking state.

The controller must answer, on every cycle:

1. What immutable state am I watching?
2. What evidence changed since the last observation?
3. Can that evidence change the next action?
4. If not, should I back off, do disjoint work, or stop?
5. What authoritative re-fetch will prove the next state?

Continuous Fully Automated Agentic Development: agents auto-promote when dual-gate + task outcome are verified on the candidate SHA. Sovereignty cockpit = ArchWiz + chat (goals/constraints, not a synchronous merge checkpoint).

## State machine

| State | Entry evidence | Action |
|---|---|---|
| ACTIVE | run/job/review/artifact state is changing or useful work is still executing | re-fetch at an adaptive cadence; do not duplicate work |
| QUIET | no meaningful delta, but the operation remains live | increase the wait interval; work on a disjoint bounded task |
| STALLED | repeated identical state, no progress, deadlock, expired deadline, or repeated non-informative retry | stop blind retries; classify and change the experiment/approach |
| TERMINAL | authoritative success/failure/cancellation or task outcome is verified | validate current SHA and close the cycle |
| BLOCKED | required authority, credential, input, or external capacity is missing | record the blocker; request only the missing authority/input |

Never treat elapsed time, HTTP 200, a successful dispatch, or a green individual job as task completion.

## Adaptive cadence

Choose the next observation from evidence, not a universal polling constant:

- Immediate re-fetch: after a material commit, workflow dispatch, rerun, steering action, review response, or newly reported failure.
- Short wait: while a run/job is actively producing new steps, logs, artifacts, or review events.
- Backoff: when repeated observations contain no material delta and the authoritative state remains live.
- Stop retrying: when the same failure repeats without a changed input, environment, or hypothesis.
- One-shot: when no new feedback can change the next action.
- Deadline stop: when the platform/task deadline is authoritative; do not invent a second application-level timeout.

Record why the cadence changed.

## Mandatory re-fetch contract

After every material commit or steering action, re-fetch: SHA -> workflow/run -> jobs -> steps/logs/artifacts -> reviews/comments -> resulting SHA/status.

Bind every conclusion to the SHA that produced its evidence. A newer SHA invalidates approval evidence from an older head unless the evidence is explicitly historical.

## Disjoint-work rule

While useful work is running, continue only with work that cannot mutate or invalidate the watched operation. Good disjoint work includes deterministic documentation or inventory improvements, bounded repository reconnaissance, non-invasive tests, relationship-graph queries, and review/evidence ingestion.

Do not create competing writes, duplicate workflow dispatches, or overlapping branches merely to stay busy.

## Retry / steering rule

Retry only when the new attempt has an evidence-backed reason to differ: changed input or SHA; transient infrastructure/provider failure; recovered capacity/quota; corrected workflow/reference; or a new review finding or authoritative instruction.

Preserve every attempt. Never rewrite history to hide a failed wait cycle.

## Evidence receipt

Each cycle should be representable by a compact receipt:

    observed_at: <UTC>
    watched:
      repo: <owner/name>
      ref: <branch/tag/SHA>
      sha: <immutable SHA>
    state: ACTIVE|QUIET|STALLED|TERMINAL|BLOCKED
    evidence:
      runs: [<run ids>]
      jobs: [<job ids>]
      reviews: [<stable ids>]
      artifacts: [<stable ids>]
    delta: <what changed since prior observation>
    decision: WAIT|BACKOFF|STEER|RETRY|STOP|PROMOTE
    reason: <evidence-backed reason>
    next_check: <authoritative condition>
    outcome: PASS|FAIL|UNKNOWN

Never store secrets, authorization headers, raw discussion bodies, or private session state in the receipt.

## Promotion boundary

Promotion requires: current immutable SHA; current-base relationship verified; relevant validation evidence terminal; requested task outcome verified; no unresolved actionable finding; and evidence attributable to the candidate SHA.

Dual-gate status is necessary where the repository defines it, but it is not a substitute for task-outcome verification.

Repository dual-gate: `hygiene + portability gate` + `agentic termux smoke`. Vercel rate-limit is non-gate (#772). Copilot / CodeRabbit / Devin are advisory only. `mergeable_state=dirty` or a GitHub merge conflict is a hard block even when dual-gate is green — rebase/re-extract onto live tip.

**Mega-merge (Operator 2026-09-24):** Allowed when dual-gate + mergeable. CodeRabbit ~100-file limit is advisory review capacity, not a promote ban. Size alone does not block.

## Terminal states

- success — requested outcome verified;
- clean-no-op — no change required;
- blocked — new authority/input is required;
- approval-required — policy requires escalation;
- exhausted — authoritative task/platform limit reached;
- stagnated — repeated cycles produced no measurable progress.

Never report exhausted, stalled, or blocked as success.

## Closeout

Record what was proven, what remains unproven, the watched SHA, the final authoritative evidence, and the next disjoint action or terminal state.

This skill is the wait/controller layer. adaptive-feedback-cycle owns broader continuous learning; production-reconciliation owns ref alignment; evidence-envelope owns normalized observation fields.

## Session 2026-09-25 14:02 PDT

- Live master `9a63cc58` after #841 PROMOTE.
- Dual-gate SUCCESS on `ac1eb4c7` (repo-gate 36188886425, termux-smoke 36188886444).
- Open #838/#839 NEED_EVIDENCE. #836 rebase requested. #837 SUPERSEDED.
- Do not pulse #175. Do not retarget #48.

Agent-Identity: Grok (Administrator)
