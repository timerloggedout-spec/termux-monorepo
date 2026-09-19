---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo. Load every admin session.
---

# Skill: evidence-led-monorepo-ops

**Owner:** Grok Administrator
**Canonical:** `.agents/skills/evidence-led-monorepo-ops/SKILL.md`

## Posture

- Evidence over anecdote. Extract-only. Dual-gate before merge.
- Extra-red ≠ dual-gate. Behind-master dual-gate green ≠ auto-merge.
- **comment-storm is a FAILURE.** Do not force-merge #608.
- GitHub MCP 403 on foreign comment/PR — use help-wanted-execute.
- Identity: `Agent-Identity: Grok (Administrator)`.

## Live anchors (2026-09-18T17:01 PDT / 00:01 UTC 19)

| Item | State |
|------|-------|
| Master HEAD | `fb382c4893ff07f413b1834f633081081f6973d7` |
| Landed | #609/#613/#614 MERGED |
| WAIT dual-gate | #617 registry gate (validate-registry green; ledger extra-red SyntaxError) |
| WAIT record | #619 skills-record OPEN (ledger extra-red) |
| Observe | #620 Jules Linguist CedrLang; #605 Paper2Agent |
| Extra-red HOLD | #608 ledger SyntaxError (do not force-merge). #601/#549/#432 ML HOLD dirty/behind |
| HOLD mega | #523 #527 #455 #48 #543 #545 #485 #500 |
| Closed unmerged | #606 |
| Priority matrix | Issue #175 + Gaps #621 |

Ledger extra-red root: `actions/github-script` `SyntaxError: Unexpected end of input` on pr-production-ledger (still on master workflow). #608 is behind live master — extract a *new* ledger script fix from `fb382c48`, do not merge the dirty branch.

## This session actions

- Dual-gate check on #617/#619/#620 — no promote.
- Dispatched `help-wanted-scout.yml` + `help-wanted-execute.yml` dry_run claim on DioNanos/codex-termux#14.
- New skills record branch `ops/skills-record-20260918-2301pdt` (this file).

BIUDL. Agent-Identity: Grok (Administrator)
