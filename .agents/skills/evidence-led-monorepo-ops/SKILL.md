---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo. Load every admin session.
---

Local mirror. Canonical is master `.agents/skills/evidence-led-monorepo-ops/SKILL.md`.

Master: `fb382c4893ff07f413b1834f633081081f6973d7`.
#609/#613/#614 MERGED. #617 WAIT dual-gate (validate-registry green; ledger extra-red on master).
#608 HOLD extra-red / behind / validate-PR red — do not force-merge.
#627 OPEN extract: balanced pr-production-ledger script onto live master. This is the extra-red repair path.
#601/#549/#432 ML HOLD dirty/behind. #605 Paper2Agent observe. #620 Jules observe.
HOLD mega: #523 #527 #455 #48 #543 #545 #485 #500.
Record PRs WAIT: #619 #622 #623 #624 #625 #626 + this session.

This session (2026-09-18 23:18 PDT):
- Recon confirmed ledger extra-red: SyntaxError Unexpected end of input on pendingChecks addRaw quote mismatch (run 35425503714).
- Extracted #608 script onto master-based branch `fix/ledger-syntax-extract-fb382c48` → PR #627. Did not merge #608.
- help-wanted-execute.yml dry_run claim queued: GlassHaven/Haven#273.
- Copilot review requested on #617.
- Dual-gate: do not merge #617/#623-family while master ledger extra-red; #627 is the repair.
- No issue comments (comment-storm is a FAILURE).

Agent-Identity: Grok (Administrator)
