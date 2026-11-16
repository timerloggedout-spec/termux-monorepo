# nc-1 continuous logs

Append-only diagnostic logs written by the `doe-nc1-continuous-log`
workflow (every 6h at :41 UTC + dispatch; Swarm app token;
single-writer; cadence per CADENCE-AMENDMENT-2026-11-01.md — frequency
changes only on significance evidence, never calendar defaults).

- `population-log.jsonl` — one line per run: population size, source
  files + content hash, per-stratum counts / density mean+median /
  token totals / layer-verdict mix / class hints. A run that cannot
  aggregate appends a `status: DEFER` line with the reason instead
  (fail-soft; gaps are visible, never silent).
- `density-stats.jsonl` — one line per stratum per run, same figures
  in flat form for downstream consumers (e.g. the 3L0 density view).
- Backfill lines (`kind: backfill`, stamped with the source
  evidence_hash) carry the one-time historical baseline from
  ops/telemetry/density-stats.json. Cumulative per-stratum n in each
  run line = backfill baseline + current population snapshot
  (snapshots are never summed across runs). Strata below n>=30 are
  flagged NOT_ESTABLISHED in-line, never hidden.

These logs are DIAGNOSTIC ONLY. They are not scored runs: no verdicts
are computed, no floors are checked, and tau is never derived or
moved here. Scored evaluation runs live in `doe-nc1-eval.yml`
(workflow_dispatch only) and their records land as
`records/run-*-EXPERIMENT.json`.
