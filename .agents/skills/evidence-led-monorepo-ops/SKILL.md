---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo (and similar agentic monorepos). Triggers on priority matrix, master gates, SHE progress, Manus/provider RE, dirty PR triage, Actions hygiene, or when the operator says continue, BIUDL, maximize actions, or /continue. Use for live state pulls, dispositions, small-green extracts, adaptive WAIT, and iterative process improvement documented as skills. Load this skill in every admin session.
---

# Skill: evidence-led-monorepo-ops

**Owner:** ArchW1z / Grok Administrator continuous admin on timerloggedout-spec/termux-monorepo.

**Canonical paths (keep in sync):**
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md` ← **agent load path**
- `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md` ← human/docs mirror
- `docs/ops/SKILLS-INVENTORY.md` ← full skill table + adaptive WAIT

**Primary agent entry:** `CLAUDE.md`.

## Posture

- Evidence over anecdote. Extract-only. Dual-gate before merge.
- Extra-red ≠ dual-gate. Behind-master dual-gate green ≠ auto-merge.
- **comment-storm is a FAILURE**, not skippable noise. Mitigate with concurrency groups + `cancel-in-progress: false` on SHA-bound ledgers. Do not treat cancelled ledger runs as green.
- Identity: `Agent-Identity: Grok (Administrator)`.
- GitHub MCP write works as `timerloggedout-spec` even when local sandbox has no OPERATOR PAT / `gh`.

## Current production anchors (2026-09-18T22:08Z UTC)

| Item | State |
|------|-------|
| Master HEAD | `a55a56894cfe95c2ed88446d6ef42df3bb47ee2a` (#614 squash) |
| Just landed | #614 Approxination lane. #613 BIFROST-006 runbook. #612 inventory. #611 Bifrost. #609 help-wanted. |
| Extract-later | #615 closed (inventory conflict after #614). This branch is the clean extract. |
| Extra-red HOLD | #608 ledger SyntaxError chicken-egg — do not force-merge. #601/#549/#432 ML HOLD dirty/behind. |
| HOLD mega | #523 #527 #455 #48 #543 #545 #485 #500 |
| Draft | #605 Paper2Agent; #578 accounting/bidding |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. Do not wholesale-merge HOLD mega or #601/#549/#432.

Do not MCP-write 35k workflow bodies. Do not comment-storm.

CodeRabbit `queue: max` on GHA concurrency is **not a valid key** (only `group` + `cancel-in-progress`). Do not apply.

GitHub MCP cannot comment/PR foreign repos (403). Use Actions OPERATOR / help-wanted-execute for upstream-pr.

BIUDL. Agent-Identity: Grok (Administrator)
