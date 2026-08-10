# Contributing

This monorepo is developed with **humans and agents** on Termux and CI.

## Start here

| Audience | Entry |
|----------|--------|
| Agents | [`AGENTS.md`](AGENTS.md) |
| Claude-family | [`CLAUDE.md`](CLAUDE.md) |
| Everyone | [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) |
| Permissions | [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) |
| Operator checklist | [`docs/ARCHW1Z-OPERATOR-CHECKLIST.md`](docs/ARCHW1Z-OPERATOR-CHECKLIST.md) |

## Branch & merge

1. Branch from **`master-staging`** (integration spine).
2. Keep changes small and cite proposal items: `Implements: CE-09`.
3. Ensure gates pass locally if possible:

   ```bash
   python3 scripts/ci/repo_gate.py
   python3 scripts/ci/termux_smoke.py
   ```

4. Open PR **into `master-staging`**.
5. Promote to `master` only when staging is healthy and both gates are green.

## Proposals

- Register under `docs/proposals/active/<id>/` with `MANIFEST.md` + `ITEMS.md`.
- Update `docs/proposals/registry.yaml`.
- Debate in MANIFEST Review log and optional `DEBATE.md` (chat alone is not consensus).
- Closing rules: `docs/proposals/PROCESS.md` (all items terminal, outcome recorded, move to `closed/`).

## Security

- Never commit session stores, browser profiles, cookies, or API keys.
- See `SECURITY.md`, `docs/SECURITY-REMEDIATION.md`, and repo-gate HARD checks.

## Code review

- Critical unresolved threads block merge.
- P0 security / history work needs Operator acknowledgment.
- Prefer disposition comments on PRs that reference Critical-Eval item IDs.

## Recovery / navigation

Root `README.md` remains the recovery cockpit. Prefer ArchWiz indices for day-to-day tool maps (`archwiz/TOOL_INDEX.md`, etc.).
