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

## Required contribution preflight

**Read [Contribution Style Preflight](docs/ops/CONTRIBUTION-STYLE-PREFLIGHT.md) before implementation or collaboration.** It publishes the exact DO-first gate rules, CAVEMAN-6, the winning Siglary standard, notation classes, comment/commit/PR requirements, and the local preflight command.

Run the linguistic preflight before committing or posting:

```bash
python3 scripts/ci/check_do_statement_style.py --preflight --base origin/master
```

For comment, review, issue, or discussion drafts, pass the exact draft with `--text-file PATH`. Apply the same DO-first + Siglary contract to code comments, commit subjects/bodies, PRs, issues, reviews, discussions, workflow directives, skills, and project chat.

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
