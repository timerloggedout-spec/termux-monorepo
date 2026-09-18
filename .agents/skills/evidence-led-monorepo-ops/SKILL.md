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
- **comment-storm is a FAILURE**, not skippable noise. Mitigate with concurrency groups + `cancel-in-progress: false` on SHA-bound ledgers. Do not treat cancelled ledger runs as green.
- Identity: `Agent-Identity: Grok (Administrator)`.
- GitHub MCP write works as `timerloggedout-spec` even when local sandbox has no OPERATOR PAT / `gh`.

## Current production anchors (2026-09-18T17:03Z UTC)

| Item | State |
|------|-------|
| Master HEAD | `dc30bf83fc17b394510f99328f7a081b6a64f28c` (#603 squash) |
| Just landed | #603 comment-storm ledger fix. Prior: #602 catalog MD fingerprint; #600 skills SSOT. |
| Observe | #583 Grafana MCP; #584 MVT budget. Jules #597/#598. |
| Extra-red HOLD | #601 ML extract dirty/behind (`c082f533` base vs live `dc30bf83`). #549/#432 HOLD extract-later. |
| HOLD mega | #523 #527 #545 #543 #455 #485 #483 #481 |
| Draft | #578 accounting/bidding schema pilot |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. Do not wholesale-merge HOLD mega or #601/#549/#432.

CodeRabbit `queue: max` on GHA concurrency is **not a valid key** (only `group` + `cancel-in-progress`). Do not apply.

BIUDL. Agent-Identity: Grok (Administrator)
