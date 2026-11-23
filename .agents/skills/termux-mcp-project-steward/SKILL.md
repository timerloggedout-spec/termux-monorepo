---
name: termux-mcp-project-steward
description: Operate a constrained Android Termux agentic hub alongside GitHub repository projects for health checks, PR/issue stewardship, lean worktrees, device resource triage, tunnel-aware MCP operations, and safe project reporting.
---

# Termux MCP Project Steward

Use this skill for repository stewardship through a connected Android/Termux MCP.

## Operating modes

- read-only unless an action is explicitly requested;
- apply only for an explicit repository/device mutation request;
- never automatically merge, close, delete, force-push, rotate/revoke credentials, create swap, or clear data.

## Preflight

1. Confirm the Termux MCP is the Android device, not a sandbox.
2. Inspect resource pressure before expensive work.
3. Keep MCP checkouts, caches, sessions, tunnels, and generated logs outside tracked worktrees.
4. For edits, use a clean isolated worktree from the requested remote base.
5. Read [Contribution Style Preflight](../../../docs/ops/CONTRIBUTION-STYLE-PREFLIGHT.md) before implementation, drafting, comments, commits, PRs, or issue work.
6. Run `python3 scripts/ci/check_do_statement_style.py --preflight --base origin/master` before commit or publication; pass `--text-file PATH` for collaboration drafts.
7. Before commit, run `git diff --check`, the smallest relevant test, and `git status --short`.

## WAIT + loop

```text
OBSERVE → CHOOSE → ACT → VERIFY → RECORD → WAIT / STEER → REPEAT
```

WAIT means re-reading authoritative state after asynchronous work. Stop on `success`, `clean no-op`, `blocked`, `approval-required`, `exhausted`, or `stagnated`.

## Repository discipline

Use a submodule only for a reviewed external source dependency that the repository actually needs to pin and build. Do not use submodules as configuration documentation.

For GitHub stewardship, preserve SHA/run/job/artifact provenance and distinguish committed, executed, validated, and promoted states.

## References

- `CLAUDE.md`
- `SKILLS.md`
- `docs/ops/SKILLS-INVENTORY.md`
- `.agents/skills/adaptive-wait/SKILL.md`
- `.agents/skills/adaptive-feedback-cycle/SKILL.md`
- `docs/ops/CONTRIBUTION-STYLE-PREFLIGHT.md`
- `docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md`
- `docs/proposals/active/notation-sets/SIGLARY-STANDARD.md`
- `docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md`
