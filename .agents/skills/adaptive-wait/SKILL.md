---
name: adaptive-wait
description: Adaptive WAIT stage for agentic GitHub ops. After any dispatch, commit, rebase, or merge request — re-check jobs/steps/logs/artifacts, do concurrent non-conflicting work, classify stalls, and only promote when dual gates + task outcome are verified. Triggers when waiting on CI, after PR open/update, during /continue cycles, or when operator says wait adaptively. Cross-session SSOT — always load from master, never chat-only.
---

# Skill: adaptive-wait

**Owner:** ArchW1z / Grok Administrator  
**Complements:** `evidence-led-monorepo-ops`, `adaptive-feedback-cycle`, `production-reconciliation`, `review-loop`, `ml-pipelines`

While one PR's checks run: preserve immutable IDs; work on a disjoint path; do not idle.

Promote only when dual gates success, extract-clean scope, and task outcome verified.

HEAD observed (`c082f53379d230f4617f201d32c114f198dd63a1` after docs-branch-index).
Master dual-gate last terminal SUCCESS on `eefc068`: smoke 35301928043; repo-gate 35301928066.
Historical-eval catalog freshness FAIL 35356132030 is extra-red ≠ gate (stall class `effect` / docs freshness).
#549 dirty vs live master: stall class `update-branch-conflict` — reconstruct, do not force-update.
#589 update-branch vs `01083fcc`: CONFLICTed — stall class `update-branch-conflict`; extract-later.
#596/#597/#598 unstable vs `c082f533` — re-observe dual-gate after this extract; do not triple-merge skill-record/Jules lanes.

Session 2026-09-18T16:15Z UTC: extract ML observe-mode onto live master. GitHub MCP + `gh` as timerloggedout-spec.

BIUDL. Agent-Identity: Grok (Administrator)
