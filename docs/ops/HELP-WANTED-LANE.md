# Help-Wanted Lane (Production) — EXECUTE

**Status:** LIVE + **adaptive cadence**. First external PR: [vedantnimbarte/zero#81](https://github.com/vedantnimbarte/zero/pull/81).
**Parallel / adaptive:** `docs/ops/HELP-WANTED-PARALLEL.md`

## Why

Scan FOSS → CPPH rank → claim → **upstream PR into the author's repo**. Feed Actions evidence into workbench benchmarks. Predecessor to bug & bounty hunter. 2017 React UI is predecessor only.

## Cadence (adaptive)

| Piece | Frequency |
|-------|-----------|
| Scout | **Every 2h** (`17 */2 * * *`) + dispatch |
| Execute | **Every 4h** + dispatch; **daily budget gate** (default 3 upstream actions/UTC day) |
| Safe parallel writes | **2–3** concurrent (token pool) |

Tune up until rate-limit pain; bench artifacts: `help-wanted-scout-bench.json`, `help-wanted-daily-budget.json`.

## Delivery hierarchy

1. **PRIMARY — upstream-pr** — author's repo.
2. **FALLBACK — fork-offer** — only if primary blocked.
3. **PARALLEL NOTICE** — optional comment + commit URL alongside primary (or fallback).

## Components

| Path | Role |
|------|------|
| `.agents/skills/help-wanted-lane/SKILL.md` | Agent load |
| `docs/ops/HELP-WANTED-PARALLEL.md` | Roster + adaptive limits |
| `scripts/ci/help_wanted_scout.py` | CPPH |
| `scripts/ci/help_wanted_claim.py` | Claim |
| `.github/workflows/help-wanted-scout.yml` | 2h catalog |
| `.github/workflows/help-wanted-execute.yml` | Budgeted execute |

## Token order

`OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `ARCHWIZ_GITHUB_TOKEN` → `GITHUB_TOKEN`.

Next identity: GitHub App + OIDC ephemeral tokens.

BIUDL. Agent-Identity: Grok (Administrator)
