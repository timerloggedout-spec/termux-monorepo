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

## Current production anchors (2026-09-16T22:08Z)

| Item | State |
|------|-------|
| Master HEAD | `263c3dd9` (advanced under #559; prior `ff81cb6b` #557) |
| Dual gates on `ff81cb6b` | smoke 35151853839 + hygiene 35151853836 **success** |
| #559 | dirty / superseded-candidate after master move |
| Extra-red HOLD | #549 ML (#175); #432 sibling |
| HOLD mega | #523 #527 #142 #455 #48 #543 #545 |
| Hist-eval | 35155850816 setup fail: shortened checkout SHA. This extract pins full SHA. |
| Observatory sibling | `repository-observatory.yml` still short SHA — next extract |
| Comment-storm-skip | Gemini/Jules `issue_comment` skipped ≠ gate |

## Extract recipe

Create branch from current master. Do not force-update dirty branches.

BIUDL. Agent-Identity: Grok (Administrator)
