# Wingman_fork Integration

## Pinned dependency

- Repository: https://github.com/timerloggedout-spec/Wingman_fork
- Path: `refTemplates/smods/Wingman_fork`
- Branch metadata: `main`
- Pinned commit: `a6d5cea2d48009b5555e138c8d6b8f620388fb1b`
- Source commit: signed/verified upstream merge commit, message: `Claude Code as a provider, CI-fix autopilot, pilot over MCP (0.5.0)`.

The submodule is a reviewed reference/customization/template resource. Updating it is a deliberate reconciliation event; it does not silently move with upstream `main`.

## Why it is here

Wingman supplies useful patterns around semantic repository navigation, provider-neutral agent interfaces, verification gates, pilot/worktree orchestration, and memory/learning loops. The monorepo adopts patterns selectively rather than importing Wingman's governance.

## Boundary

The monorepo remains authoritative for governance, credentials, wait/retry policy, promotion, and evidence. The submodule must not receive secrets, session stores, generated artifacts, or repository-local credentials.

## Update protocol

1. Recon current Wingman and monorepo state.
2. Select a candidate revision.
3. Update the gitlink intentionally.
4. Re-run the Wingman integration skill loop.
5. Validate relevant tests/checks.
6. Re-fetch both SHAs and compare the delta.
7. Record accepted/rejected learnings before promotion.

See `.agents/skills/wingman-project-integration/SKILL.md` and `docs/ops/WINGMAN-WAIT-LOOP.md`.
