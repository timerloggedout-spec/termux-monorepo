# Help-Wanted Lane (Production) — EXECUTE

**Status:** LIVE on master (#609 + OPERATOR execute). First external PR: [vedantnimbarte/zero#81](https://github.com/vedantnimbarte/zero/pull/81).
**Parallel capacity:** `docs/ops/HELP-WANTED-PARALLEL.md`

## Why

Scan FOSS help-wanted / good-first-issue / mutual threads → rank (CPPH) → claim → implement → **open PR on the target repo** (or **fork-offer**). Stats → public Vercel/dashboard. Predecessor to bug & bounty hunter lanes. 2017 React help-wanted UI is predecessor only.

## Cadence

| Piece | Frequency |
|-------|-----------|
| Scout | **Every 6h** (`27 */6 * * *`) + dispatch |
| Execute | **Dispatch only** (OPERATOR PAT path) |
| Safe parallel external writes | **2–3** concurrent (token pool) |
| Soft daily cap | **3 upstream PRs / token / day** |

## Delivery modes

1. **upstream-pr** — PR into the author's repo (default when allowed).
2. **fork-offer** — Keep branch on our fork; post issue comment with commit link so they can PR themselves.

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

## Components

| Path | Role |
|------|------|
| `.agents/skills/help-wanted-lane/SKILL.md` | Agent load |
| `docs/ops/HELP-WANTED-PARALLEL.md` | Roster + parallel + fork-offer |
| `docs/ops/AGENT-MONIKERS.md` | Display monikers vs live `@` |
| `scripts/ci/help_wanted_scout.py` | CPPH rank |
| `scripts/ci/help_wanted_claim.py` | Claim + fork check |
| `.github/workflows/help-wanted-scout.yml` | Catalog cron |
| `.github/workflows/help-wanted-execute.yml` | OPERATOR execute |

## Token order (execute)

`OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `ARCHWIZ_GITHUB_TOKEN` → `GITHUB_TOKEN` (last is monorepo-only).

## YOLO rules

1. Scout ranks. Execute opens external PRs or fork-offers when selected.
2. Always claim before coding.
3. Cap concurrent external PRs; prefer fork-offer when upstream is hostile to drive-by PRs.
4. Evidence → ledger + dashboard.
5. Dual-gate for monorepo-side only.

## Multi-platform

GitHub P0. GitLab / Bitbucket / Gitea additive later.

BIUDL. Agent-Identity: Grok (Administrator)
