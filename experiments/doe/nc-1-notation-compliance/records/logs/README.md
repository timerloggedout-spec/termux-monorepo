# nc-1 continuous logs

Append-only diagnostic logs written by the `doe-nc1-continuous-log`
workflow (daily 07:41 UTC + dispatch; Swarm app token; single-writer).

- `population-log.jsonl` — one line per run: population size, source
  files + content hash, per-stratum counts / density mean+median /
  token totals / layer-verdict mix / class hints. A run that cannot
  aggregate appends a `status: DEFER` line with the reason instead
  (fail-soft; gaps are visible, never silent).
- `density-stats.jsonl` — one line per stratum per run, same figures
  in flat form for downstream consumers (e.g. the 3L0 density view).

These logs are DIAGNOSTIC ONLY. They are not scored runs: no verdicts
are computed, no floors are checked, and tau is never derived or
moved here. Scored evaluation runs live in `doe-nc1-eval.yml`
(workflow_dispatch only) and their records land as
`records/run-*-EXPERIMENT.json`.
