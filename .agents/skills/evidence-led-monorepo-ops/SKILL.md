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

## Current production anchors (2026-09-18T01:26Z)

| Item | State |
|------|-------|
| Master HEAD | `3d062325b62d5` (`ops(skills): record #588 landing` #590) |
| Just landed | #576 `4d532a9e5655`; #577 `92d704c0f8c8`; #579 `60a742a6d2f0`; #580 `96a04af3839d4`; #581 `d886560b8a546`; #582 `f779b9a2fd550`; #585 `9f4c7fa2a5808`; #586 `11c56e46c0365`; #588 `ea5aa867645c4`; #590 `3d062325b62d5` |
| Dual gates last verified | Master push dual-gate on `3d062325`: smoke **35295241188** success; repo-gate **35295241175** success. #590 PR dual-gate: smoke 35290155849 + hygiene 35290155715 success. Prior master dual-gate on `11c56e46`: smoke 35285651963 + repo-gate 35285652100 |
| Observe (not merged) | #583 Grafana MCP. #584 MVT context-safe budget (`validate-pull-request` extra-red FAIL ≠ gate). #587 Jules date-only merged-branch-audit bump. #589 Jules CedrLang placeholder-callback extract (PR dual-gate green on `ea5aa867`; update-branch after #590) |
| Extra-red HOLD | #549 ML (#175) dirty/behind base `6df9b66`; sibling #432 HOLD — extract later from live master |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 #466 #456 #453 |
| Draft | #578 accounting/bidding schema pilot |
| Comment-storm-skip | Gemini/Jules/ECC/`coderabbitai` `issue_comment` cancelled/success mix ≠ gate |
| Extra-red non-gate | Vercel rate-limit historically on #545/#549; merge-promotion-queue inventory fail on master ≠ gate |
| Non-gates | historical-eval / swe-reference-evaluation fail; mermaid docs-refresh; agent-jules-on-issues / actions-run-watcher startup_failure; OpenRouter free catalog sync fail |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. #549 remains dirty/behind — do not merge; extract later from `3d062325`.

BIUDL. Agent-Identity: Grok (Administrator)
