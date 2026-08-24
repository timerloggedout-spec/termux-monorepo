# github-telemetry

Evidence ledger + derived metrics for termux-monorepo.

- **Config:** `config/metric-policy.yaml`, `config/sources.yaml`
- **Pure reducers:** `she.metrics.job_timestamps` (stdlib, no network)
- **Raw / normalized / derived dirs:** reserved; prefer object storage for high-volume raw; keep Git-tracked manifests + compact derived reports under `docs/ops/generated/`

See `docs/ops/GITHUB-OBSERVABILITY.md`.

Collector CLI (`python -m ops.github_telemetry.collect`) is a future thin wire — not required for SHE L0 intents.
