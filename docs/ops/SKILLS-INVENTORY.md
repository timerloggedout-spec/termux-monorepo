# Skills Inventory (termux-monorepo)

**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)  
**Ops loop trigger words:** `continue`, `BIUDL`, `maximize actions`, `/continue`

## Active ops skills (load these)

| Skill | Path | Role |
|-------|------|------|
| **evidence-led-monorepo-ops** | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` (+ `docs/ops/skills/…`) | Live state, dual-gate, extract-only, priority matrix, dispositions |
| **adaptive-feedback-cycle** | `.agents/skills/adaptive-feedback-cycle/SKILL.md` | OBSERVE → CLASSIFY → **WAIT/STEER/RETRY** → VERIFY → PROMOTE → FEED FORWARD |
| **review-loop** | `.agents/skills/review-loop/SKILL.md` | SHA/run binding, bilateral critique, no-HITL continuous review |
| **production-reconciliation** | `.github/skills/production-reconciliation/SKILL.md` | RECON → PLAN → IMPLEMENT → COMMIT → **WAIT** → VALIDATE → RE-FETCH → CLASSIFY → RECORD |
| **context-relationship-graph** | `.agents/skills/context-relationship-graph/SKILL.md` | File/PR/issue/timeline graph; verified vs candidate edges |
| **termux-monorepo-agentic-governance** | `.agents/skills/termux-monorepo-agentic-governance/SKILL.md` | Permissions, consensus tiers, PR triage bounds |

## Adaptive WAIT (non-negotiable)

From `adaptive-feedback-cycle` + `production-reconciliation`:

1. After any dispatch/commit/merge request: **WAIT** is a stage, not idle sleep.
2. Re-check run/job state and timestamps; do concurrent non-conflicting work.
3. Stall classes: admission / queue / execution / effect / pagination / routing loop.
4. Do not classify `queued`/`in_progress` as success or failure.
5. Promote only when dual gates green **and** task outcome verified.
6. Preserve every attempt (provenance); never rewrite history to linearize.

Local Grok project skill (this chat environment):
`/home/workdir/.grok/skills/evidence-led-monorepo-ops/SKILL.md`

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
- Follow-up: AGENTS.md is a **Linguist/CedrLang stub only**; hard rules live in CLAUDE.md.

## Backfill / stall context (ops)

- Historical corpus / context-relationship backfill stalled at **`next_start_page=2`** since **~2026-08-19**.
- Root cause class: **admission stall** — `context-relationship-backfill.yml` on master has **no schedule**, only `workflow_dispatch` → 0 auto-runs (#526 audit).
- **#526** audit findings **landed** (`docs/ops/AUDIT-FINDINGS-PR523.md`). Independent audit; Tanka abandoned follow-through on temporary quota (operator note 2026-09-15).
- **#523** / **#527** remain **HOLD** (mega); extract schedule/admission only when dual-gate safe.

Implements: skills-inventory / agents-linguist-stub  
BIUDL.
