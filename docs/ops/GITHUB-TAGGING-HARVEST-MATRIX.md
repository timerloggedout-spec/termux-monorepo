# GitHub tagging × data harvest matrix

**Related:** [GITHUB-TAGGING-SYSTEM.md](./GITHUB-TAGGING-SYSTEM.md) · [LANE-MATRIX.md](./LANE-MATRIX.md) · generated [lane-matrix-status.md](./generated/lane-matrix-status.md)

## Decision: KEEP SEPARATE + hooks

Do **not** fold `github-tagging-refresh` into `repository-observatory` or `ops-lane-matrix-sweep`.

| Surface | Cadence | Output |
|---------|---------|--------|
| Observatory | daily ~04:17 UTC | `workspace/llm_map/repositories/repository-index.json` |
| Lane matrix | sweep workflow | `docs/ops/generated/lane-matrix-status.*` |
| Tagging harvest | daily 05:41 UTC | `docs/ops/generated/github-tagging/*` |

## Harvest matrix upgrade (v1.1)

Generated:

- `harvest-matrix.json` — `priority → { domain: n }`
- `visibility-board.json` — P0 / keep-active + cross-board links

Agents and dashboards should read **visibility-board.json** first, then filter `repos_tagged.json` via `tags_flat` / DSL.

## Integrative hooks (allowed)

1. Tagging may **read** observatory index for enrichment fields only
2. Visibility board **links** to lane-matrix + observatory paths
3. Help-wanted / SHE dashboards may consume `tags_flat` without owning the cron

No shared workflow runner. Dual-gate still per product PR.

Agent-Identity: Grok (Administrator)
