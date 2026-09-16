# Skills Inventory (termux-monorepo)

**Version:** 2026-09-16 · **Last refreshed SHA:** `ff81cb6b` (#557; prior #556/#555/#554/#553)  
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)  
**Ops loop trigger words:** `continue`, `BIUDL`, `maximize actions`, `/continue`

> **Single navigation SSOT.** Update this file + any changed skill body in the same PR. Chat-only skill content is not loadable by other sessions.

## Role load matrix

| Role | Load first | Then | Optional |
|------|------------|------|----------|
| **Admin / Grok Administrator** | `evidence-led-monorepo-ops` + `adaptive-wait` | `termux-monorepo-agentic-governance` + `review-loop` | `adaptive-feedback-cycle`, `production-reconciliation` |
| **Collaborator / Codespace agent** | `adaptive-feedback-cycle` | dual-gate (`repo_gate` + `termux_smoke`) + conventions | `review-loop` |
| **Evaluator** | `blind-agent-evaluation` + `multivariate-doe` | `pr-evidence-evaluation` + `mvt-experiment` | `evidence-envelope` |
| **Governance / proposal** | `termux-monorepo-agentic-governance` | `docs/CONSENSUS.md` + `docs/proposals/AGENTIC-PERMISSIONS.md` | `review-loop` |
| **Discovery / extend** | `find-skills` | skills.sh leaderboard + this inventory | — |

## Active ops skills (load these)

| Skill | Path | Role |
|-------|------|------|
| **evidence-led-monorepo-ops** | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` (+ `docs/ops/skills/…`) | Live state, dual-gate, extract-only, extra-red HOLD, behind-master extract |
| **adaptive-wait** | `.agents/skills/adaptive-wait/SKILL.md` (+ `docs/ops/skills/…`) | WAIT stage SSOT |
| **adaptive-feedback-cycle** | `.agents/skills/adaptive-feedback-cycle/SKILL.md` | Full OBSERVE → … → FEED FORWARD |
| **review-loop** | `.agents/skills/review-loop/SKILL.md` | SHA/run binding |
| **production-reconciliation** | `.github/skills/production-reconciliation/SKILL.md` | RECON → … → RECORD |
| **context-relationship-graph** | `.agents/skills/context-relationship-graph/SKILL.md` | Verified vs candidate edges |
| **termux-monorepo-agentic-governance** | `.agents/skills/termux-monorepo-agentic-governance/SKILL.md` | Permissions / triage bounds |

## Adaptive WAIT (non-negotiable)

**Load:** `.agents/skills/adaptive-wait/SKILL.md`.

1. After dispatch/commit/merge request: WAIT is a stage, not idle sleep.
2. Re-check run/job state; do concurrent non-conflicting work.
3. Stall classes include **comment-storm-skip**.
4. Do not treat skipped `issue_comment` listeners as dual-gate results.
5. Dual-gate green + extra-red (`validate-pull-request`, `validate-registry`) → HOLD wholesale.
6. Dual-gate green on a **behind-master** SHA → extract/rebase, do not squash onto stale base.

## Cycle snapshot (2026-09-16T22:05Z)

- Master `ff81cb6b` after #557 merge-queue jq + skill-anchor squash.
- Dual-gate green on that SHA: termux smoke 35151853839 + repo gate 35151853836.
- #549: dual-gate green + validate-PR/registry red — HOLD (#175 ML).
- HOLD mega: #523 #527 #142 #455 #48.
- #543 #545 HOLD.
- Hist-eval 35155850816 failed at setup (shortened actions/checkout SHA). This extract pins full SHA.
- Merge Promotion Queue last scheduled run still 35146657772 on pre-#557 SHA; next `47 * * * *` must prove jq pin.
- Context Relationship + Team MVT success on `ff81cb6b`; comment-storm-skip on Gemini/Jules listeners.

## Entry fold

- #488 / #534 / #537 / #542 / #546 / #547 / #548 / #553 / #554 / #555 / #556 / #557 landed.
- This extract refreshes anchors after #557 and repairs hist-eval checkout pin.

## Cross-session rule

Skill content other sessions must load **must** live on **master** under `.agents/skills/<name>/SKILL.md`.

BIUDL. Agent-Identity: Grok (Administrator)
