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

## Current production anchors (2026-09-18T03:06Z)

| Item | State |
|------|-------|
| Master HEAD | `eefc06833815d` (`ops(skills): record #591 landing` #592) |
| Just landed | #576 `4d532a9e5655`; #577 `92d704c0f8c8`; #579 `60a742a6d2f0`; #580 `96a04af3839d4`; #581 `d886560b8a546`; #582 `f779b9a2fd550`; #585 `9f4c7fa2a5808`; #586 `11c56e46c0365`; #588 `ea5aa867645c4`; #590 `3d062325b62d5`; #591 `01083fcc3c99e`; #592 `eefc06833815d` |
| Dual gates last verified | #592 PR dual-gate on `07cad51d`: smoke **35297909967** success; hygiene **35297909831** success. Master push dual-gate on `eefc068` admitted: smoke **35301928043** + repo-gate **35301928066** (in flight at record time). Prior master dual-gate on `01083fcc`: smoke 35295339310 + repo-gate 35295339344 success. |
| Observe (not merged) | #583 Grafana MCP (dual-gate green on `a2d8415a` but `validate-pull-request` extra-red FAIL ≠ gate; keep observe). #584 MVT context-safe budget (same extra-red). #587 Jules date-only audit bump. #589 Jules CedrLang placeholder extract: update-branch CONFLICTed vs `01083fcc` — extract later, do not force |
| Extra-red HOLD | #549 ML (#175) dirty/behind base `6df9b66`; sibling #432 HOLD — extract later from live master |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 #466 #456 #453 |
| Draft | #578 accounting/bidding schema pilot |
| Comment-storm-skip | Gemini/Jules/ECC/`coderabbitai` `issue_comment` cancelled/success mix ≠ gate |
| Extra-red non-gate | actions-run-watcher / agent-jules-on-issues / swe-reference-evaluation startup_failure on `eefc068` ≠ gate |
| Non-gates | mermaid docs-refresh; OpenRouter free catalog sync fail; merge-promotion-queue inventory fail |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. #549 remains dirty/behind — do not merge; extract later from `eefc068`. #589 update-branch conflicted — extract CedrLang placeholder change from live master if still valuable.

BIUDL. Agent-Identity: Grok (Administrator)
