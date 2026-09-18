---
name: adaptive-wait
description: Adaptive WAIT stage for agentic GitHub ops. After any dispatch, commit, rebase, or merge request — re-check jobs/steps/logs/artifacts, do concurrent non-conflicting work, classify stalls, and only promote when dual gates + task outcome are verified. Triggers when waiting on CI, after PR open/update, during /continue cycles, or when operator says wait adaptively. Cross-session SSOT — always load from master, never chat-only.
---

# Skill: adaptive-wait

**Owner:** ArchW1z / Grok Administrator  
**Complements:** `evidence-led-monorepo-ops`, `adaptive-feedback-cycle`, `production-reconciliation`, `review-loop`

While one PR's checks run: preserve immutable IDs; work on a disjoint path; do not idle.

Promote only when dual gates success, extract-clean scope, and task outcome verified.

Stall classes include **comment-storm-skip**, **update-branch-conflict**, and **dirty-behind-master**.

HEAD observed (`c082f53379d230f4617f201d32c114f198dd63a1` after #595 + docs-branch-index bot). #595 PR dual-gate SUCCESS: smoke 35309791148; hygiene 35309791199.
#594 PR dual-gate SUCCESS: smoke 35306172380; hygiene 35306172362.
Master dual-gate on `eefc068` SUCCESS: smoke 35301928043; repo-gate 35301928066.
#583 dual-gate green + extra-red validate-PR ≠ gate.
#589 update-branch vs `01083fcc`: CONFLICTed — extract-later.
#596 unstable/behind; #599 dirty — do not merge; extract catalog regen from live master if still failing.

Session 2026-09-18T16:10Z UTC: recorded live master `c082f533`. GitHub MCP write as timerloggedout-spec.

BIUDL. Agent-Identity: Grok (Administrator)
