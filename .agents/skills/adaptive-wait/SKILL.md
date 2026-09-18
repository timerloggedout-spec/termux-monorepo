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
| **comment-storm** | **FAILURE** | issue_comment / bot / ledger fan-out that cancels useful jobs. Mitigate: concurrency by event_name, `cancel-in-progress: false` on ledgers. Landed #603. |
| dual-gate red | FAILURE | Block promote. `validate-pull-request` still red on #608. |
| update-branch-conflict | STALL | Extract-later; do not force dirty |
| dirty-behind-master | STALL | #601/#549/#432 ML |
| extra-red | FAILURE (non-gate) | Vercel mcp-hub rate-limit residual; Devin trial expired; CodeRabbit review rate limited |
| **truncated-mcp-write** | **FAILURE** | #606 closed. Do not push 35k workflow via MCP. |
| **ledger-syntax** | **FAILURE** | #608 open — chicken-egg until merge + master YAML is the fixed file. |

Master HEAD: `d9e2d495384de3341b28bb6372bbc6223b722837` after #609 help-wanted + cadence docs.
#607 skills SSOT observe. Do not comment-storm to wake CI.

BIUDL. Agent-Identity: Grok (Administrator)
