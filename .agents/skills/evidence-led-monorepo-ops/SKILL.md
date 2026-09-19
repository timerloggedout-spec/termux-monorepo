---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo. Load every admin session.
---

Local mirror. Canonical is master `.agents/skills/evidence-led-monorepo-ops/SKILL.md`.

Master: `80bcad872194d69513c63e837fb23755961f7808`.
#609/#613/#614/#627 MERGED. #627 extract-only of balanced pr-production-ledger onto live master.
#608 HOLD extra-red / behind / dirty — do not force-merge (repair already extracted).
#629/#630 Jules dirty observe. #601/#549/#432 ML HOLD dirty/behind. #605 Paper2Agent observe. #620 Jules Linguist observe.
HOLD mega: #523 #527 #455 #48 #543 #545 #485 #500.
Record PRs WAIT: #619 #622 #623 #624 #625 #626 #628 #632 + this session.

This session (2026-09-19 10:09 PDT):
- Recon: master `dc45d50` → `80bcad87` via #627 merge.
- Dual-gate on #627 merge SHA: hygiene + portability GREEN, termux smoke GREEN, repo-gate GREEN.
- Ledger issue_comment runs 9359–9366 still show extra-red/cancelled on pre-merge SHA `dc45d50` (Vercel/CodeRabbit/ecc-tools comment-storm). Workflow has no workflow_dispatch. Do not treat cancelled as green. Wait for a push-bound ledger run on `80bcad87`.
- Did not merge #608/#629/#630/#632 (behind or dirty).
- help-wanted-execute dry_run claim queued: DioNanos/codex-termux#14.
- Prior dry_run GlassHaven/Haven#273 succeeded (run 35453898465).
- Dual-gate: record family still WAIT until ledger on live SHA is not extra-red SyntaxError.
- No issue comments (comment-storm is a FAILURE).

Agent-Identity: Grok (Administrator)
