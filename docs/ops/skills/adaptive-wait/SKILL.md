<!-- Local docs mirror. Canonical policy: .agents/skills/adaptive-wait/SKILL.md -->

# Adaptive WAIT — operational mirror

**Canonical:** .agents/skills/adaptive-wait/SKILL.md

## Control

Waiting is evidence collection, not an idle timer. Every cycle resolves the watched immutable SHA, records evidence delta, decides whether new evidence can change the next action, and identifies the authoritative next check.

## States

- ACTIVE — state is changing or useful work is executing; re-fetch adaptively.
- QUIET — no material delta but the operation remains live; back off and do disjoint work.
- STALLED — repeated identical state, deadlock, deadline, or non-informative retries; stop blind retries and change approach.
- TERMINAL — authoritative outcome exists; validate current SHA and close.
- BLOCKED — required authority/input/capacity is missing; record the blocker.

## Cadence

- Immediate re-fetch after material commits, dispatches, reruns, steering, review responses, or new failures.
- Short waits while steps/logs/artifacts/reviews are progressing.
- Backoff when authoritative state is live but observations contain no material delta.
- Retry only when the next attempt has an evidence-backed difference.
- Use one-shot execution when no new feedback can change the next action.

## Mandatory chain

SHA -> workflow/run -> jobs -> steps/logs/artifacts -> reviews/comments -> resulting SHA/status

Older-SHA evidence is historical when the head changes.

## Disjoint work

While waiting, do only bounded work that cannot invalidate the watched operation. Do not duplicate writes, dispatches, or competing branches merely to stay busy.

## Receipt

Record observed_at, watched repo/ref/SHA, state, run/job/review/artifact IDs, evidence delta, decision, reason, next authoritative check, and outcome. Never store secrets, authorization headers, raw private discussion bodies, or session state.

## Promotion

Require current-SHA/base alignment, terminal relevant validation, verified task outcome, no unresolved actionable finding, and attributable evidence. Dual-gate is necessary where defined but does not substitute for task-outcome verification.

## Terminal

success | clean-no-op | blocked | approval-required | exhausted | stagnated

Never report stalled, exhausted, or blocked as success.

**Related:** adaptive-feedback-cycle, review-loop, production-reconciliation, evidence-envelope.

## Bounded feedback-loop integration

Adapt the user-supplied Loopy six-phase pattern to existing repository owners; do not create a parallel runtime or receipt store.

**Observe → Choose → Act → Verify → Record → Repeat**

- Observe: fresh immutable SHA, exact-root graph context, run/job/review evidence.
- Choose: one authorized proposal item using priority, risk, dependency, and measurable outcome.
- Act: one bounded change on an isolated branch/worktree.
- Verify: deterministic tests and required gates on the candidate SHA.
- Record: native evidence envelope, orchestration receipt, and relationship evidence.
- Repeat: continue only on measurable progress or a material evidence delta; otherwise back off, do disjoint work, or stop.

Keep execution state, task outcome, and promotion separate. Use success, clean-no-op, blocked, approval-required, exhausted, and stagnated as terminal states. A green run is not task success. A task pass is not automatic promotion.

No new scheduler, provider invocation, spending, external message, production change, credential movement, or merge authority is introduced. The source was supplied as a JSON skill attachment without a source commit/version; this is an adapted pattern, not an upstream-published loop.
