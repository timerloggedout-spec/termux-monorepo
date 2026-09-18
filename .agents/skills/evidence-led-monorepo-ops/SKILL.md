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
- GitHub MCP write works as `timerloggedout-spec`. Do **not** MCP-write 35k workflow bodies (#606 abort class).

## Current production anchors (2026-09-18T21:04Z UTC)

| Item | State |
|------|-------|
| Master HEAD | `d9e2d495384de3341b28bb6372bbc6223b722837` |
| Just landed | #609 help-wanted EXECUTE lane (merged). Cadence docs on master. #604/#603 prior. |
| External first PR | [vedantnimbarte/zero#81](https://github.com/vedantnimbarte/zero/pull/81) open |
| Dual-gate red HOLD | #608 ledger SyntaxError chicken-egg (`pull_request_target` still runs older master YAML on some checks). Do not force-merge. |
| Observe | #583 Grafana MCP; #584 MVT budget. Jules #597/#598. #605 Paper2Agent draft. |
| Extra-red HOLD | #601/#549/#432 ML dirty/behind — extract-later. Keep ML files. |
| HOLD mega | #523 #527 #545 #543 #455 #485 #48 #500 |

## Extract recipe

Create branch from current master. Do not force-update dirty branches. Do not wholesale-merge HOLD mega or ML extracts.

Peer-orch still `cancel-in-progress: true` without `event_name` split — extract-later via local git. Do not MCP-push the 35k YAML.

CodeRabbit `queue: max` is invalid GHA concurrency — do not apply.

BIUDL. Agent-Identity: Grok (Administrator)
