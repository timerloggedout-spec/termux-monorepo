# ML recon binder v0.7.0

Observe-only extract for Issue #175. Not a merge.

| Role | SHA | Promote? |
|------|-----|----------|
| Product (last dual-gate recorded by command center) | `8d36f149214f4a147932188bc424e7c29b8de444` | only with a fresh dual-gate on **this** SHA |
| Observer tip (help-wanted refresh, 2026-10-09) | `9dc1e437088d2983d26043a16e608e2051f46d38` | no |
| Generated board writer | `cb940cc3eafc8105e913010b76757f255fa46511` | no |
| Stale issue body stamp | `8424a50c` | no — edit the body, do not pulse-comment |

## Locks

- Wholesale ML `#432 #549 #601 #682 #746 #787 #817` stay EXTRACT.
- Minesweeper / Jules peers stay EXTRACT. Do not overwrite their branches.
- `#48` and `#788` stay on `master-staging`.
- `#806` / `#809` need a small rebase plus dual-gate. Do not promote the stale base.
- Actions incidents `#1023`–`#1026` are evidence gaps, not promote gates.
- CodeRabbit's ~100-file budget is advisory.

```text
python3 -m ml.pipelines.cli recon
python3 -m ml.pipelines.cli steward
```

`steward` returns `"writes": false`.
