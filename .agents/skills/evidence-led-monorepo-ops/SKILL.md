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

## Current production anchors (2026-09-17T21:05Z)

| Item | State |
|------|-------|
| Master HEAD | `f779b9a2fd550` (`ops(skills): record #581 landing` #582) |
| Just landed | #576 Sentinel `4d532a9e5655`; #577 Bolt `92d704c0f8c8`; #579 `60a742a6d2f0`; #580 `96a04af3839d4`; #581 `d886560b8a546`; #582 record landing `f779b9a2fd550` |
| Dual gates last verified | Master push dual-gate on `d886560`: smoke 35269615266 success; repo-gate 35269615325 success. #582 PR dual-gate: agentic termux smoke + hygiene + portability gate success. Parent `96a04af` dual-gate: smoke 35258129320 + repo-gate 35258129342 |
| Observe (not merged) | #583 Grafana MCP boundary (hygiene green; extra-red mix). #584 MVT context-safe budget (dual-gate green; `validate-pull-request` extra-red FAIL ≠ gate) |
| Extra-red HOLD | #549 ML (#175) dirty/behind base `6df9b66`; sibling #432 HOLD — extract later from live master |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 #466 #456 #453 |
| Draft | #578 accounting/bidding schema pilot |
| Comment-storm-skip | Gemini/Jules/ECC/`coderabbitai` `issue_comment` cancelled/success mix ≠ gate |
| Extra-red non-gate | Vercel rate-limit historically on #545/#549 |
| Non-gates | historical-eval / swe-reference-evaluation fail; mermaid docs-refresh; agent-jules-on-issues / actions-run-watcher startup_failure; OpenRouter free catalog sync fail |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. #549 remains dirty/behind — do not merge; extract later from `f779b9a2`.

BIUDL. Agent-Identity: Grok (Administrator)
