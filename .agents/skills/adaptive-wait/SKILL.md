---
name: adaptive-wait
description: Adaptive WAIT stage for agentic GitHub ops. After any dispatch, commit, rebase, or merge request — re-check jobs/steps/logs/artifacts, do concurrent non-conflicting work, classify stalls, and only promote when dual gates + task outcome are verified. Triggers when waiting on CI, after PR open/update, during /continue cycles, or when operator says wait adaptively. Cross-session SSOT — always load from master, never chat-only.
---

# Skill: adaptive-wait

**Owner:** ArchW1z / Grok Administrator  
**Complements:** `evidence-led-monorepo-ops`, `adaptive-feedback-cycle`, `production-reconciliation`, `review-loop`

**Canonical paths (keep in sync on every change):**
- `.agents/skills/adaptive-wait/SKILL.md` ← **agent load path**
- `docs/ops/skills/adaptive-wait/SKILL.md` ← human/docs mirror
- Listed in `docs/ops/SKILLS-INVENTORY.md`

**Anti-pattern:** skill content only in chat memory. **Always commit to master.**

## Purpose

WAIT is a **methodological stage**, not sleep-only idle time. After any action that triggers GitHub Actions or changes mergeability, the agent must observe runtime evidence before classifying success, failure, or next work.

## When to load

- After `create_pull_request`, `update_pull_request_branch`, `merge_pull_request`
- After `create_or_update_file` / push that will fire workflows
- During every `/continue` · `BIUDL` · evidence-led cycle when checks are in flight
- When operator says wait, poll, or adaptive wait

## Non-negotiable rules

1. **WAIT ≠ sleep-only.** Do concurrent non-conflicting useful work while a cohort is in flight.
2. **Never classify terminal from `queued` or `in_progress`.**
3. **Inspect before decide:** jobs → steps → logs → artifacts → receipts → resulting SHA/status.
4. **Dual-gate before promote:** `agentic termux smoke` + `hygiene + portability gate`.
5. **Preserve provenance.** Every attempt stays addressable by SHA.
6. **Stall is a classification, not auto-retry permission.**
7. **Skipped listeners are not gates.** `issue_comment` skipped/cancelled on master is not a gate.

## Stall classes

| Class | Signal |
|-------|--------|
| **admission** | Expected schedule/dispatch produced **0 runs** |
| **queue** | `queued` beyond observation window with no job admission |
| **execution** | `in_progress` with no step/log/artifact progress |
| **effect** | Workflow terminal success but expected effect missing |
| **pagination** | Continuation run completes but `next_start_page` does not advance |
| **routing loop** | Same SHA/input repeatedly cancels/fails without new diagnosis |
| **comment-storm-skip** | Burst of `issue_comment` runs on master with `conclusion=skipped` or cancelled-on-comment. Classify `not_executed` + `reviewer_noise`. |

## Procedure (every wait cohort)

```text
1. CAPTURE admission — run_id, attempt, SHA, ref, started_at, expected effect
2. WAIT — do not declare success/failure yet
3. WORK — independent non-conflicting phase
4. WATCH — re-fetch check_runs / workflow run status
5. VALIDATE — dual-gate conclusions + actual outputs
6. CLASSIFY — PASS | FAIL | STALLED | UNKNOWN + stall class if any
7. ACT — merge | extract | hold | retry-with-new-identity | feed-forward
8. RECORD — brief evidence in disposition / memory / skill if process learned
```

## Active-wait rule

While one PR's checks run: preserve immutable IDs; work on a disjoint path; do not mutate the watched branch; re-check after each material action.

## Promotion gate

Promote only when dual gates success, extract-clean scope, and task outcome verified.

HEAD observed (`f779b9a2fd550` after #582). Master dual-gate on `d886560` terminal SUCCESS: smoke 35269615266; repo-gate 35269615325.
#582 PR dual-gate SUCCESS: agentic termux smoke + hygiene + portability gate.
Master dual-gate on `f779b9a2` admitted this session — not classified terminal yet.

Session 2026-09-17T21:05Z: squash-merged #582 onto master. GitHub MCP write as timerloggedout-spec.

BIUDL. Agent-Identity: Grok (Administrator)
