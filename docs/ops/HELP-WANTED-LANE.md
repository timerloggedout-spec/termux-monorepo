# Help-Wanted Lane (Production) — EXECUTE

**Status:** LIVE on master (#609 + OPERATOR execute). First external PR: [vedantnimbarte/zero#81](https://github.com/vedantnimbarte/zero/pull/81).
**Parallel capacity:** `docs/ops/HELP-WANTED-PARALLEL.md`

## Why

Scan FOSS help-wanted / good-first-issue / mutual threads → rank (CPPH) → claim → implement → **open PR on the target (author) repo**. Stats → public Vercel/dashboard. Predecessor to bug & bounty hunter lanes. 2017 React help-wanted UI is predecessor only.

## Cadence

| Piece | Frequency |
|-------|-----------|
| Scout | **Every 6h** (`27 */6 * * *`) + dispatch |
| Execute | **Dispatch only** (OPERATOR PAT path) |
| Safe parallel external writes | **2–3** concurrent (token pool) |
| Soft daily cap | **3 upstream PRs / token / day** |

## Delivery hierarchy

1. **PRIMARY — upstream-pr** — PR into the **author's** repo. This is the goal.
2. **FALLBACK — fork-offer** — only if upstream PR is blocked/not allowed/failed: keep commit on our fork.
3. **PARALLEL NOTICE** — optional issue comment with commit URL **alongside** an upstream PR (or with fallback), so maintainers have a pointer. **Not** a substitute for primary when primary works.

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
| `docs/ops/HELP-WANTED-PARALLEL.md` | Roster + parallel + hierarchy |
| `docs/ops/AGENT-MONIKERS.md` | Display monikers vs live `@` |
| `scripts/ci/help_wanted_scout.py` | CPPH rank |
| `scripts/ci/help_wanted_claim.py` | Claim + fork check |
| `.github/workflows/help-wanted-scout.yml` | Catalog cron |
| `.github/workflows/help-wanted-execute.yml` | OPERATOR execute |

## Token order (execute)

`OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `ARCHWIZ_GITHUB_TOKEN` → `GITHUB_TOKEN` (last is monorepo-only).

## YOLO rules

1. Scout ranks. Execute **opens upstream PRs** when selected.
2. Always claim before coding.
3. Cap concurrent external **upstream** PRs.
4. Fallback / parallel notice only when needed — never demote primary by default.
5. Evidence → ledger + dashboard.
6. Dual-gate for monorepo-side only.

## Multi-platform

GitHub P0. GitLab / Bitbucket / Gitea additive later.

BIUDL. Agent-Identity: Grok (Administrator)
