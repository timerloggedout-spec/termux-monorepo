---
name: adaptive-wait
description: Adaptive WAIT stage for agentic GitHub ops. After any dispatch, commit, rebase, or merge request — re-check jobs/steps/logs/artifacts, do concurrent non-conflicting work, classify stalls, and only promote when dual gates + task outcome are verified. Triggers when waiting on CI, after PR open/update, during /continue cycles, or when operator says wait adaptively. Cross-session SSOT — always load from master, never chat-only.
---

# Skill: adaptive-wait

**Owner:** ArchW1z / Grok Administrator  
**Complements:** `evidence-led-monorepo-ops`, `adaptive-feedback-cycle`, `production-reconciliation`, `review-loop`

While one PR's checks run: preserve immutable IDs; work on a disjoint path; do not idle.

Promote only when dual gates success, extract-clean scope, and task outcome verified.

HEAD observed (`6af1e12c5afb2caf` after #595). #595 PR dual-gate SUCCESS: smoke 35309791148; hygiene 35309791199.
#594 PR dual-gate SUCCESS: smoke 35306172380; hygiene 35306172362.
Master dual-gate on `eefc068` SUCCESS: smoke 35301928043; repo-gate 35301928066.
#583 dual-gate green on `a2d8415a` with extra-red `validate-pull-request` FAIL ≠ gate.
#589 update-branch vs `01083fcc`: CONFLICTed — stall class `update-branch-conflict`; extract-later.
Master push dual-gate on `6af1e12c` admitted (in flight at record).

Session 2026-09-18T23:27Z PDT: recorded #595 landing. GitHub MCP write as timerloggedout-spec.

BIUDL. Agent-Identity: Grok (Administrator)
