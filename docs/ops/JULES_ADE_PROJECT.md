# Jules ADE Project — Retired Integration Record

**Repository status:** Jules-triggered automation retired effective 2026-11-01 by operator direction.

This document preserves the former Jules-oriented development-environment notes as migration history. The active environment is governed by `CLAUDE.md`, repository-owned proposal scope, GitHub workflows, and the configured agent routes.

## Replacement direction

- Keep task prompts, setup instructions, test commands, permissions, and acceptance criteria in versioned repository files.
- Dispatch work through currently configured agents and repository-owned automation.
- Reuse the GitHub branch, pull-request, review, and gate model.
- Evaluate Google Antigravity or other agents as separate capabilities; verify runtime, permissions, and test execution before adoption.
- Preserve GitHub branches and pull requests as durable code artifacts.

## Vendor timeline

Google's official Jules changelog announced the wind-down on 2026-10-29, set the read-only transition after 2026-11-11, and stated a 2026-12-31 wind-down date: <https://jules.google/docs/changelog>.

The repository's 2026-11-01 retirement is an earlier local automation decision. This record does not assert that Google's service shut down on that date.

See `docs/ops/INTEGRATION-DRIFT-2026-11-19.md` for the current drift ledger.
