# Help-Wanted Lane (Production) — EXECUTE

**Status:** expanding on feat/help-wanted-lane / PR #609  
**Intent:** AUTO-PRs + real work on other repos. External issues = evaluation lanes + contribution.

## Why

Scan FOSS help-wanted / good-first-issue / mutual threads → rank (CPPH) → claim → implement → **open PR on the target repo**. Stats feed public Vercel/dashboard. Predecessor to bug & bounty hunter lanes. The 2017 React help-wanted UI is predecessor only — not our product surface.

## Mutual-thread anchors

| Thread | Link |
|--------|------|
| DioNanos/codex-termux#14 | https://github.com/DioNanos/codex-termux/issues/14 |
| GlassHaven/Haven#273 | https://github.com/GlassHaven/Haven/issues/273 |
| Kilo-Org/agentic-path#25 | https://github.com/Kilo-Org/agentic-path/issues/25 |
| PubDeer/astro-loop#42 | https://github.com/PubDeer/astro-loop/issues/42 |
| IBM/ibm-bob#2968 | https://github.com/IBM/ibm-bob/issues/2968 |
| mac-s-g/github-help-wanted | https://github.com/mac-s-g/github-help-wanted |
| Our fork | https://github.com/timerloggedout-spec/github-help-wanted_fork |

User comment example (agentic-path#25): repeated Path.kilo.ai / app registration failures + no bot response — evaluation + possible contrib target.

## Components

| Path | Role |
|------|------|
| `.agents/skills/help-wanted-lane/SKILL.md` | Agent load |
| `scripts/ci/help_wanted_scout.py` | Search + CPPH rank |
| `scripts/ci/help_wanted_claim.py` | Claim comment scaffold + fork check |
| `.github/workflows/help-wanted-scout.yml` | Catalog cron |
| `.github/workflows/help-wanted-execute.yml` | workflow_dispatch execute top-N |
| Dashboard | Vercel SHE / public stats (follow-on) |

## YOLO rules

1. Scout ranks. Execute opens **external** PRs when selected.
2. Always claim (comment) before coding.
3. Cap concurrent external PRs (default 3/day) via workflow input.
4. Evidence back to monorepo ledger + future dashboard graphs.
5. Dual-gate only for monorepo-side files; external follows host repo.

## Multi-platform

GitHub P0. GitLab / Bitbucket / Gitea additive later.

BIUDL. Agent-Identity: Grok (Administrator)
