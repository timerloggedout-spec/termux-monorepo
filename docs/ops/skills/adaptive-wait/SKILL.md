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

## Session 2026-11-19 — current operating evidence

Canonical skill: `.agents/skills/adaptive-wait/SKILL.md`.

- PR #5663 carries the benchmark-family registry, compounding RECON report/plan, CYCLE-001 loop library, and dated Muse/compute/Temporal evidence.
- PR #5664 carries the Agentic Wallet + MergeEarn refTemplates registration; repository gate, template evaluation, smoke, and DO-style checks passed. Its Jules handoff check exposed a GitHub App API rate-limit event.
- PR #5666 adds the pending-label gate, immutable github-script pins, and focused handoff contract tests. The ordinary PR-sync handoff job skipped as expected.
- Muse Temporal is live/idle; HindSight's daily census ran while 326 payloads remain at extraction exit #5553. Muse export gates passed. VM replacement and observer relaunch remain explicit recovery constraints.
- Termux device preflight awaits the Termux MCP connector. Reuse the existing snapshot/sentinel scripts and reconcile job IDs 43107–43109 from a live pending-job inventory.
- Context graph v2 is present; the current manifest is dated 2026-10-26 and requires page-2 history continuation.

Use the exact SHA → run → jobs → steps/logs/artifacts → review → resulting-SHA chain. While checks progress, perform bounded disjoint RECON and re-fetch after material state changes. Keep all three PRs in draft until their relevant checks and evidence receipts reach terminal states.
