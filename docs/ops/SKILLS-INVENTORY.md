# Skills Inventory (termux-monorepo)

**Version:** 2026-09-16 · **Last refreshed SHA:** `56f0edee` (docs-branch-index; post-#548)  
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

## Cycle snapshot (2026-09-16T17:16Z)

- Master `56f0edee`.
- #550 / #551: dual-gate green on `5b40df04` base — extract onto current master.
- #549: dual-gate green + validate-PR/registry red — HOLD (#175 ML).
- HOLD mega: #523 #527 #142 #455 #48.
- #543 #545 HOLD.

## Entry fold

- #488 / #534 / #537 / #542 / #546 / #547 / #548 landed.
- This extract refreshes anchors after the docs-branch-index commit on `56f0edee`.

## Cross-session rule

Skill content other sessions must load **must** live on **master** under `.agents/skills/<name>/SKILL.md`.

BIUDL. Agent-Identity: Grok (Administrator)
