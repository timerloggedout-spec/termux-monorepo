# Actions Metrics Integration — Reference vs Duplicate

**Status:** research + operator policy (2026-08-24)  
**Owner:** ArchW1z / evidence-led-monorepo-ops

## Reality check (no Performance Metrics API)

GitHub does **not** expose a public REST/GraphQL endpoint that returns the aggregated tables shown under:

- `https://github.com/<owner>/<repo>/actions/metrics/performance` (Job failure rates, average run times)
- the companion total-minutes / usage views

Community consensus (Discussions #188189, #181231 and others): the UI is internal; the only automated path is to **re-derive** metrics from the standard Actions endpoints.

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

Reconstruct the same signals with the public API:

| Goal | Endpoint(s) |
|------|-------------|
| List runs | `GET /repos/{owner}/{repo}/actions/runs` (filter `status`, `created`, `workflow_id`) |
| Per-run jobs | `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs` |
| Billable / duration | `GET /repos/{owner}/{repo}/actions/runs/{run_id}/timing` (note: usage endpoints are sunsetting; prefer job `started_at`/`completed_at`) |
| Workflow list | `GET /repos/{owner}/{repo}/actions/workflows` |

**Aggregation recipe (stdlib or gh + jq):**

1. Page runs for the target workflow(s) in the desired window.
2. For each completed run, count `conclusion == failure` vs total.
3. Compute average duration from job timestamps or timing payload.
4. Emit a row compatible with the CSV schema so SHE / priority matrix can consume either source.

Community helpers that already do this style of work:

- `fchimpan/gh-workflow-stats` (gh extension — success rate + execution time)
- Custom scripts that walk runs → jobs → steps (rate-limit aware)

### 3. Reference, do not re-duplicate numbers in prose

- Priority matrices and disposition notes **link** to the latest CSV path and/or the live workflow runs page.
- When a number is needed inline, cite the dated file + row (e.g. `agentic-repository-operations-report.lock.yml @ 2026-08-24 CSV → 100%`).
- SHE observers (`she/ingest/actions.py`) already normalize individual run/job payloads; they do not need the aggregated UI table.

### 4. Future thin wire

A scheduled workflow that:

1. Uses `gh api` / Octokit to aggregate the last N days.
2. Writes a fresh `actions-metrics-*-$(date +%F).csv` under `docs/ops/generated/`.
3. Opens a PR or commits directly under authority gate (same pattern as context-relationship index bots).

Until that exists, operator export + commit remains the authoritative path.

## Mapping to SHE P0

- **P0.2 ingest** already consumes individual Actions events → Incident.
- Aggregated failure rates from CSVs / reconstructed metrics feed the **priority matrix** and canary selection for `intents_for_workflow_failure`.
- Live token-bearing re-run (next P0.3 wire) uses `run_id` from a concrete failed run, not the aggregate percentage.

## Anti-patterns

- Scraping the HTML performance page (fragile, ToS risk).
- Treating a single CSV as permanent truth without dating it.
- Re-typing failure percentages into multiple markdown files instead of linking the artifact.
