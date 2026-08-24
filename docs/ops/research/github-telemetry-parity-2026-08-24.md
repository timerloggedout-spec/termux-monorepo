# Research provenance — GitHub telemetry parity (2026-08-24)

Operator-supplied research (access validation + architecture) integrated into:

- `docs/ops/GITHUB-OBSERVABILITY.md`
- `ops/github-telemetry/config/metric-policy.yaml`
- `ops/github-telemetry/config/sources.yaml`
- `she.metrics.job_timestamps` (queue + policy hooks)

## Refined claim (adopted)

GitHub exposes underlying run/job data to reproduce **most** repository-level metrics; it does **not** expose the exact pre-aggregated Performance Metrics UI tables as a single endpoint.

## Primary citations (operator research)

- Projects API (GraphQL): docs.github.com — Using the API to manage Projects
- Workflow runs / jobs REST: docs.github.com/rest/actions/*
- Timing/usage closing down: github.blog/changelog/2025-02-02-actions-get-workflow-usage-and-get-workflow-run-usage-endpoints-closing-down
- Traffic 14-day retention: docs.github.com/rest/metrics/traffic
- Statistics: stats/commit_activity, stats/code_frequency (422 >10k commits)
- Actions Performance Metrics GA: github.blog/changelog/2025-03-14-actions-performance-metrics-are-generally-available-…

## L1V3 SWE-bench / ML pipeline

Metrics and Termux-init process feed an ML pipeline. Locally reconstructed Actions performance + SHE fingerprints are prioritized as features for L1V3 SWE-bench-style evaluation and MoneyBall/3L0 decision support (authority still dominates ranking).
