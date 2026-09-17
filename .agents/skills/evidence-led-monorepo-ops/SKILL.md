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
- GitHub MCP write works as `timerloggedout-spec` even when local sandbox has no OPERATOR PAT / `gh`.

## Current production anchors (2026-09-17T18:18Z)

| Item | State |
|------|-------|
| Master HEAD | `60a742a6d2f02` (`ops(skills): rebase SSOT anchors` #579 after #577/#576) |
| Just landed | #576 Sentinel she.sandbox path/symlink harden `4d532a9e5655`; #577 Bolt observatory opt `92d704c0f8c8`; #579 skill anchors `60a742a6d2f0` |
| Dual gates last verified | On pre-merge heads: #576 smoke+hygiene success; #577 smoke+hygiene success; #579 smoke 35251200546 + repo-gate 35251200551. Master push dual-gate on `60a742a6`: smoke 35257989201 + repo-gate 35257989263 queued (not terminal) |
| Extra-red HOLD | #549 ML (#175) dirty/behind base `6df9b66`; sibling #432 HOLD — extract later from live master |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 #466 #456 #453 |
| Draft | #578 accounting/bidding schema pilot |
| Comment-storm-skip | Gemini/Jules/ECC/`coderabbitai` `issue_comment` cancelled/success mix ≠ gate |
| Extra-red non-gate | Vercel rate-limit historically on #545/#549 |
| Non-gates | historical-eval / swe-reference-evaluation fail; mermaid docs-refresh; agent-jules-on-issues / actions-run-watcher startup_failure; OpenRouter free catalog sync fail |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. #549 remains dirty/behind — do not merge; extract later from `60a742a6`.

BIUDL. Agent-Identity: Grok (Administrator)
