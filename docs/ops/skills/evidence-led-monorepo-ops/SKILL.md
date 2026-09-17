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

## Current production anchors (2026-09-16T24:02Z)

| Item | State |
|------|-------|
| Master HEAD | `820ecd2f` (#562 squash; prior `f1d59dc5` #560, `263c3dd9` #558) |
| Dual gates on `820ecd2f` | repo-gate 35160492303 success; termux smoke 35160492248 success |
| Extra-red HOLD | #549 ML (#175); #432 sibling; #563 Jules linguist (1-file / unstable) |
| HOLD mega | #523 #527 #142 #455 #48 #543 #545 |
| HOLD generated drift | #561 Jules catalog-only; not lane SSOT |
| Observatory | full checkout SHA pinned in #562 |
| Comment-storm-skip | Gemini/Jules/ECC `issue_comment` skipped ≠ gate |
| Docs-refresh | mermaid render fail (35160492333) — not dual-gate |

## Extract recipe

Create branch from current master. Do not force-update dirty branches.

BIUDL. Agent-Identity: Grok (Administrator)
