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
- Identity: `Agent-Identity: Grok (Administrator)`.

## Current production anchors (2026-09-17T03:12Z)

| Item | State |
|------|-------|
| Master HEAD | `ebdd4c0f` (#568 skill anchors after #567; prior `5b8f06b0` #567 MCP Docker) |
| Dual gates on `ebdd4c0f` | repo-gate 35177187396 success; termux smoke 35177187383 success |
| Extra-red HOLD | #549 ML (#175); #432 sibling |
| HOLD mega | #523 #527 #142 #455 #48 #543 #545 |
| Landed this cycle | #568 skill anchors; #567 MCP Docker lane; #566 skill anchors; #563 Jules linguist NSE-020 |
| Comment-storm-skip | Gemini/Jules/ECC `issue_comment` skipped ≠ gate |
| Extra-red non-gate | Vercel deployment rate-limit on #545 and #549 (retry 24h) |
| Non-gates | historical-eval / swe-reference-evaluation fail; mermaid docs-refresh; agent-jules-on-issues / actions-run-watcher startup_failure — not dual-gate |

## Extract recipe

Create branch from current master. Do not force-update dirty branches.

BIUDL. Agent-Identity: Grok (Administrator)
