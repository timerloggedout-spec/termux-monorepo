---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo. Load every admin session.
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

## Current production anchors (2026-09-19T09:06 PDT)

| Item | State |
|------|-------|
| Master HEAD | `dc45d50e66acd67e10e162bc08cecfb45af61e00` (docs-branch-index after `fb382c48`) |
| Extra-red repair | #627 OPEN extract of balanced `pr-production-ledger` script. **Not merged.** Ledger still extra-red on master (`issue_comment` storm + SyntaxError path). |
| HOLD | #608 dirty/behind — do not force-merge. |
| WAIT dual-gate | #617 validate-registry green; do not promote while master ledger extra-red. |
| Observe Jules | #629 Sentinel symlink (dirty). #630 dashboard rich fallback (dirty). #620 Linguist. |
| ML HOLD | #601/#549/#432 dirty/behind. Keep pipelines. |
| HOLD mega | #523 #527 #455 #48 #543 #545 #485 #500 |
| Record PRs WAIT | #619 #622 #623 #624 #625 #626 #628 + this session |

## This session (2026-09-19 09:06 PDT)

- Recon: master moved `fb382c48` → `dc45d50`. Ledger runs 9328–9335 on master still failure/cancelled on `issue_comment` (CodeRabbit/Vercel bots). comment-storm = FAILURE.
- Dual-gate: do **not** merge #617/#623-family/#608/#629/#630 while extra-red.
- #627 remains the extract repair path; Copilot re-requested.
- help-wanted-execute.yml dry_run claim queued: GlassHaven/Haven#273.
- Copilot requested on #629 and #630. Observe only — mergeable_state dirty.
- No issue comments (comment-storm is a FAILURE).

Create branch from current master. Do not force-update dirty branches. Do not wholesale-merge HOLD mega or #601/#549/#432.

CodeRabbit `queue: max` on GHA concurrency is **not a valid key** (only `group` + `cancel-in-progress`). Do not apply.

BIUDL. Agent-Identity: Grok (Administrator)
