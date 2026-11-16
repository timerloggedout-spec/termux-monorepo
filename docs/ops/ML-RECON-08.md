# ML recon binder v0.8.0

Observe-only extract for Issue #175. Not a merge. Keeps `ml/pipelines` v0.6.0 DAG.

| Role | SHA | Promote? |
|------|-----|----------|
| Product (last dual-gate recorded by command center) | `8d36f149214f4a147932188bc424e7c29b8de444` | only with a fresh dual-gate on **this** SHA |
| Observer tip (sweep receipt, 2026-10-10) | `677a2d72d6c251e4f12e81e1bdba3b787671b2d6` | no |
| Stale recon07 cut | PR #1188 on base `0acc8d24` | no — superseded by this live cut |

The frozen catalog is a subset (69 PRs + 8 issues). The generated
lane board remains the full writer (`open_prs_observed=202`).

## Locks

- Wholesale ML `#432 #549 #601 #682 #724 #746 #787 #817` stay EXTRACT.
- Minesweeper / Jules peers stay EXTRACT. Do not overwrite their branches.
- `#48` and `#788` stay off `master`. Never retarget.
- Actions incidents `#1023`–`#1026` are evidence gaps, not promote gates.
- `#772` Vercel rate-limit is non-gate.
- `#184` is names-only. No secret values.
- Do not restamp `docs/ops/LANE-MATRIX.md`. Do not pulse-comment #175.
- CodeRabbit's ~100-file budget is advisory.

```text
python3 -m ml.pipelines.cli recon
python3 -m ml.pipelines.cli steward
```

`steward` returns `"writes": false`.
