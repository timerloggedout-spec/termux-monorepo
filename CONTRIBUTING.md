# Contributing

## Required contribution preflight

Read [Contribution Style Preflight](docs/ops/CONTRIBUTION-STYLE-PREFLIGHT.md) before implementation, drafting, or external collaboration.

- Apply DO-first CAVEMAN-6 and the winning Siglary Standard to code comments, commits, PRs, issues, reviews, discussions, workflow directives, skills, and project chat.
- Preserve exact technical literals; keep OPERATORS / GLYPHS / CHORDS distinct; resolve chords in their named domains.
- Run `python3 scripts/ci/check_do_statement_style.py --preflight --base origin/master` before commit or publication.
- Add `--text-file PATH` to validate the exact text of a comment, review, issue, or discussion draft.
- Apply `origin/master-staging` as the base when contributing to the staging lane.


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
