# Actions Metrics Integration — Reference vs Duplicate

**Status:** research + operator policy (2026-08-24, Timing API clarified + job-timestamp module)  
**Owner:** ArchW1z / evidence-led-monorepo-ops

## Reality check (no Performance Metrics API)

GitHub does **not** expose a public REST/GraphQL endpoint that returns the aggregated tables shown under:

- `https://github.com/<owner>/<repo>/actions/metrics/performance` (Job failure rates, average run times)
- the companion total-minutes / usage views

Community consensus (Discussions #188189, #181231 and others): the UI is internal; the only automated path is to **re-derive** metrics from the standard Actions endpoints.

## Actions Timing / Usage API status (critical)

| Endpoint | Status (2026-08) | Notes |
|----------|------------------|-------|
| `GET /repos/{o}/{r}/actions/runs/{run_id}/timing` | **Closing down** | Changelog 2025-02-02: "Actions Get workflow usage and Get workflow run usage endpoints closing down". Still listed in docs with WARNING; do not build new automation on it. |
| `GET /repos/{o}/{r}/actions/workflows/{id}/timing` | **Closing down** | Same deprecation. |
| Product-specific billing (`/settings/billing/actions` etc.) | **Closed** | Migrated to consolidated billing usage platform (2025). |
| New billing usage endpoint | **Live** | Summarizes by SKU / org / repo — **no per-workflow or per-run detail**. |

**Durable duration source (preferred):**

```
GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs
→ each job: started_at, completed_at, conclusion, steps[]
```

Compute `duration_ms = completed_at - started_at` (or sum step durations). This path is not deprecated and is what `gh-workflow-stats` and similar tools already use.

## In-repo pure aggregator (SHE)

Module: **`she.metrics.job_timestamps`** (SHE 0.3.2+)

| Function | Role |
|----------|------|
| `duration_ms_from_job(job)` | Single job `started_at` → `completed_at` |
| `duration_ms_from_jobs(jobs)` | Wall span min(start) → max(complete) |
| `aggregate_run_job_stats(payload)` | One run: failed_jobs, avg/median job ms, wall ms |
| `aggregate_workflow_window([...])` | Multi-run: failure_rate_pct, avg durations |

Pure stdlib. Accepts already-fetched jobs payloads (no network). Tests: `tests/test_she_job_timestamps.py`.

Caller still owns the HTTP fetch (`gh api` / Octokit); SHE only normalizes timestamps into priority-matrix-compatible stats.

## Recommended architecture for this monorepo

### 1. Dated CSV snapshots (keep for time-series)

Operator (or future workflow) exports the UI tables and commits them under:

```
docs/ops/generated/
  actions-metrics-job-failures-YYYY-MM-DD.csv
  actions-metrics-total-minutes-YYYY-MM-DD.csv
```

**Why keep duplicates over time?**

- The UI aggregation window and internal sampling are not guaranteed stable.
- Point-in-time ground truth supports SHE prioritization audits and MoneyBall/3L0 calibration.
- Cheap storage; high value for regression of failure-rate trends.

Do **not** delete prior dated files when a newer export arrives.

### 2. Live programmatic reference (preferred for automation)

Reconstruct the same signals with the **durable** public API:

| Goal | Endpoint(s) | Notes |
|------|-------------|-------|
| List runs | `GET /repos/{owner}/{repo}/actions/runs` | filter `status`, `created`, `workflow_id` |
| Per-run jobs + duration | `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs` | **preferred** for started_at / completed_at |
| Legacy timing (avoid for new code) | `GET .../runs/{run_id}/timing` | deprecated; may still respond |
| Workflow list | `GET /repos/{owner}/{repo}/actions/workflows` | |
| Org/repo usage summary | billing platform usage endpoint | no per-workflow breakdown |

**Aggregation recipe:**

1. Page runs for the target workflow(s) in the desired window.
2. For each run, fetch jobs; pass payload to `aggregate_run_job_stats` / `aggregate_workflow_window`.
3. Emit a row compatible with the CSV schema so SHE / priority matrix can consume either source.

Community helpers that already do this style of work:

- `fchimpan/gh-workflow-stats` (gh extension — success rate + execution time from runs/jobs)
- In-repo: `she.metrics.job_timestamps`

### 3. Reference, do not re-duplicate numbers in prose

- Priority matrices and disposition notes **link** to the latest CSV path and/or the live workflow runs page.
- When a number is needed inline, cite the dated file + row (e.g. `agentic-repository-operations-report.lock.yml @ 2026-08-24 CSV → 100%`).
- SHE observers (`she/ingest/actions.py`) already normalize individual run/job payloads; they do not need the aggregated UI table.

### 4. Future thin wire

A scheduled workflow that:

1. Uses `gh api` / Octokit to aggregate the last N days via **runs + jobs** only.
2. Feeds payloads into `she.metrics.job_timestamps`.
3. Writes a fresh `actions-metrics-*-$(date +%F).csv` under `docs/ops/generated/`.
4. Opens a PR or commits directly under authority gate (same pattern as context-relationship index bots).

Until that exists, operator export + commit remains the authoritative path.

## Mapping to SHE P0

- **P0.2 ingest** already consumes individual Actions events → Incident.
- Aggregated failure rates from CSVs / reconstructed metrics feed the **priority matrix** and canary selection for `intents_for_workflow_failure`.
- Live token-bearing re-run (next P0.3 wire) uses `run_id` from a concrete failed run, not the aggregate percentage.
- Duration for canary selection should come from job timestamps (`she.metrics`), not the deprecated timing endpoint.

## Anti-patterns

- Scraping the HTML performance page (fragile, ToS risk).
- Building new automation on `/timing` or product-specific billing endpoints.
- Treating a single CSV as permanent truth without dating it.
- Re-typing failure percentages into multiple markdown files instead of linking the artifact.
