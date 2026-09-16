# Skills Inventory (termux-monorepo)

**Version:** 2026-09-16 · **Last refreshed SHA:** `6df9b66a` (#547)
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
| **evidence-led-monorepo-ops** | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` (+ `docs/ops/skills/…`) | Live state, dual-gate, extract-only, retroactive benchmark review, reviewer-noise classification |
| **adaptive-wait** | `.agents/skills/adaptive-wait/SKILL.md` (+ `docs/ops/skills/…`) | **WAIT stage SSOT** — poll checks, stall classes, active-wait, dual-gate before promote |
| **adaptive-feedback-cycle** | `.agents/skills/adaptive-feedback-cycle/SKILL.md` | Full OBSERVE → CLASSIFY → WAIT/STEER/RETRY → VERIFY → PROMOTE → FEED FORWARD |
| **review-loop** | `.agents/skills/review-loop/SKILL.md` | SHA/run binding, bilateral critique, no-HITL continuous review |
| **production-reconciliation** | `.github/skills/production-reconciliation/SKILL.md` | RECON → PLAN → IMPLEMENT → COMMIT → **WAIT** → VALIDATE → RE-FETCH → CLASSIFY → RECORD |
| **context-relationship-graph** | `.agents/skills/context-relationship-graph/SKILL.md` | File/PR/issue/timeline graph; verified vs candidate edges |
| **termux-monorepo-agentic-governance** | `.agents/skills/termux-monorepo-agentic-governance/SKILL.md` | Permissions, consensus tiers, PR triage bounds |

## Adaptive WAIT (non-negotiable)

**Load:** `.agents/skills/adaptive-wait/SKILL.md` (cross-session master SSOT).

1. After any dispatch/commit/merge request: **WAIT** is a stage, not idle sleep.
2. Re-check run/job state and timestamps; do concurrent non-conflicting work.
3. Stall classes: admission / queue / execution / effect / pagination / routing loop / **comment-storm-skip**.
4. Do not classify `queued`/`in_progress` as success or failure.
5. Do not treat `issue_comment` listener **skipped** conclusions as gate results.
6. Promote only when dual gates green **and** task outcome verified.
7. Preserve every attempt (provenance); never rewrite history to linearize.

Local Grok project mirrors (this chat environment):
- `/home/workdir/.grok/skills/evidence-led-monorepo-ops/SKILL.md`
- `/home/workdir/.grok/skills/adaptive-wait/SKILL.md`

## Retroactive benchmark rule

**PR #390 remains a benchmark specimen, not the historical evaluation boundary.** Evaluate historical GitHub objects continuously and classify automation activity before converting comment volume into failure evidence.

Minimum activity taxonomy: `actionable_finding`, `provider_state`, `reviewer_noise`, `execution_failure`, `not_executed`, `self_trigger_candidate`. ECC-tools/Codex/Qodo quota, billing, availability, permission, and status chatter is provider-state/reviewer-noise unless bound execution evidence demonstrates an actual task failure.

`issue_comment` storms that complete as **skipped** on master (Gemini/DeepSeek/ECC/Jules dispatch) are `not_executed` + `reviewer_noise`, not `execution_failure`.

## Supporting skills (repo)

| Skill | Path |
|-------|------|
| find-skills | `.agents/skills/find-skills/SKILL.md` |
| multivariate-doe | `.agents/skills/multivariate-doe/SKILL.md` |
| blind-agent-evaluation | `.agents/skills/blind-agent-evaluation/SKILL.md` |
| gemini-performance-psychology | `.agents/skills/gemini-performance-psychology/SKILL.md` |
| mvt-experiment | `.github/skills/mvt-experiment/SKILL.md` |
| evidence-envelope | `.github/skills/evidence-envelope/SKILL.md` |
| evidence-provenance | `.github/skills/evidence-provenance/SKILL.md` |
| forensic-recovery | `.github/skills/forensic-recovery/SKILL.md` |
| pr-evidence-evaluation | `.github/skills/pr-evidence-evaluation/SKILL.md` |
| workflow-orchestration | `.github/skills/workflow-orchestration/SKILL.md` |
| action-effectiveness-ledger | `.github/skills/action-effectiveness-ledger/SKILL.md` |

## Entry fold (AGENTS.md → CLAUDE.md)

- **#488 MERGED** (2026-09-11): CLAUDE.md primary; AGENTS.md demoted.
- **#534**: AGENTS.md pure Linguist/CedrLang stub; hard rules in CLAUDE.md only.
- **#537**: README fast-start leads with CLAUDE.md; skills inventory + deploy lanes linked.
- **#542**: Linguist CedrLang document short-circuit + fence guard.
- **#546**: reviewer-noise taxonomy + production anchors on master.
- **#547**: skill anchors refreshed to `97c66653` post-#546; now master is `6df9b66a`.

## Backfill / stall context (ops)

- Historical corpus stalled at **`next_start_page=2`** since **~2026-08-19**.
- **Admission stall** fixed on master (#534): schedule `23 * * * *` on `context-relationship-backfill.yml`.
- **#526** audit landed; Tanka abandoned temporary quota — findings valid.
- **#523** / **#527** remain **HOLD** (mega).
- **#544** superseded by **#546** (do not wholesale-merge).
- **#543** HOLD for skill-quality evaluator extract; `validate-pull-request` still red on stale base.
- **#545** HOLD: `agentic termux smoke` success, `hygiene + portability gate` failure; behind master (`5134b6a7`).
- **#455** / **#48** comment activity fans out skipped listeners on master — observe, do not merge wholesale.

## Cross-session rule

Skill content that other sessions must load **must** live on **master** under `.agents/skills/<name>/SKILL.md`. Chat-only or local-only copies are not sufficient.

When process improves: edit inventory + skill body in one PR, dual-gate, squash-merge, refresh local mirrors.

Implements: skills navigator SSOT · adaptive-wait SSOT · retroactive benchmark continuity · reviewer-noise classification
BIUDL.
