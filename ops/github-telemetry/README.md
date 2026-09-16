# github-telemetry

Evidence ledger + derived metrics for termux-monorepo.

## Config

- `config/metric-policy.yaml` — failure set, windows, reconciliation tolerances
- `config/sources.yaml` — upstream REST/GraphQL surfaces

## CLI

```bash
# Network collect (needs gh + token)
python -m ops.github_telemetry collect --with-jobs --with-traffic --max-runs 40

# Pure reduce (jobs JSON → docs/ops/generated/actions-performance-reconstructed-YYYY-MM-DD.json)
python -m ops.github_telemetry reduce --jobs-glob 'ops/github-telemetry/raw/actions-jobs/**/*.json'

# Reconcile vs UI CSV export
python -m ops.github_telemetry reconcile \
  --csv docs/ops/generated/actions-metrics-job-failures-2026-08-24.csv \
  --derived docs/ops/generated/actions-performance-reconstructed-2026-08-24.json
```

## Pure reducers (SHE)

`she.metrics.job_timestamps` — duration, queue, window aggregates (`metric_version=actions-perf-v1`, label=`locally_reconstructed`).

## Workflow

`.github/workflows/github-telemetry-snapshot.yml` — daily 03:17 UTC + dispatch.

## Docs

- `docs/ops/GITHUB-OBSERVABILITY.md`
- `docs/ops/ACTIONS-METRICS-INTEGRATION.md`
