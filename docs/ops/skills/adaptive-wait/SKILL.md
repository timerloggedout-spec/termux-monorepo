---
name: adaptive-wait
description: Adaptive WAIT stage for agentic GitHub ops. After any dispatch, commit, rebase, or merge request — re-check jobs/steps/logs/artifacts, do concurrent non-conflicting work, classify stalls, and only promote when dual gates + task outcome are verified. Triggers when waiting on CI, after PR open/update, during /continue cycles, or when operator says wait adaptively. Cross-session SSOT — always load from master, never chat-only.
---

# Skill: adaptive-wait

**Owner:** ArchW1z / Grok Administrator  
**Complements:** `evidence-led-monorepo-ops`, `adaptive-feedback-cycle`, `production-reconciliation`, `review-loop`

While one PR's checks run: preserve immutable IDs; work on a disjoint path; do not idle.

Promote only when dual gates success, extract-clean scope, and task outcome verified.

## Failure / stall classes (do not soft-pedal)

| Class | Severity | Notes |
|-------|----------|-------|
| **comment-storm** | **FAILURE** | issue_comment / bot / ledger fan-out that cancels useful jobs. Mitigate: concurrency by event_name, `cancel-in-progress: false` on ledgers. Landed #603 on `dc30bf83`. |
| dual-gate red | FAILURE | Block promote |
| update-branch-conflict | STALL | Extract-later; do not force dirty |
| dirty-behind-master | STALL | Rebase/extract from live master |
| extra-red | FAILURE (non-gate) | Fix root cause |

HEAD after #604: `20de2a5458698d805f97e77c8c2d4c204077a60a`. #603 ledger event_name split landed. peer-orch still cancelled on issue_comment until this extract.

Session 2026-09-18T18:08Z: #605 Paper2Agent draft + CodeRabbit comment-storm cancelling peer-orch. #601 ML dirty HOLD.

BIUDL. Agent-Identity: Grok (Administrator)
