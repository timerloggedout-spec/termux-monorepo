---
name: adaptive-wait
description: Adaptive WAIT for agentic GitHub ops. Dual-gate before promote. Stay busy on disjoint work.
---

# Skill: adaptive-wait

**Owner:** ArchW1z / Grok Administrator  
**Complements:** `evidence-led-monorepo-ops`, `adaptive-feedback-cycle`, `production-reconciliation`, `review-loop`

While one PR's checks run: preserve immutable IDs; work on a disjoint path; do not idle.

Promote only when dual gates success, extract-clean scope, and task outcome verified.

## Failure / stall classes (do not soft-pedal)

| Class | Severity | Notes |
|-------|----------|-------|
| **comment-storm** | **FAILURE** | issue_comment / bot / ledger fan-out that cancels useful jobs. Mitigate: concurrency by event_name, `cancel-in-progress: false` on ledgers. Landed #603 on `dc30bf83`. Still firing on master `dc45d50` via CodeRabbit/Vercel comments. |
| dual-gate red | FAILURE | Block promote |
| update-branch-conflict | STALL | Extract-later; do not force dirty |
| dirty-behind-master | STALL | Rebase/extract from live master |
| extra-red | FAILURE (non-gate) | Fix root cause — #627 extract WAIT |

## This session (2026-09-19 09:06 PDT)

- Master: `dc45d50e66acd67e10e162bc08cecfb45af61e00`.
- #627 WAIT extra-red repair. #608 HOLD. #617 WAIT.
- #629/#630 Jules dirty — observe, do not merge.
- help-wanted-execute.yml dry_run claim queued for GlassHaven/Haven#273.
- No comment-storm from this agent.
- Stay busy: session record + Copilot + dry_run dispatch.

BIUDL. Agent-Identity: Grok (Administrator)
