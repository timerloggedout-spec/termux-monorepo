# GitHub Observability — Evidence Ledger + Derived Metrics

**Status:** architecture SSOT (2026-08-24)  
**Owner:** ArchW1z / evidence-led-monorepo-ops  
**Audience:** operators, SHE, ML pipeline (MoneyBall / 3L0 / L1V3 SWE-bench eval lanes)

## Correct final claim

> **GitHub does not provide a documented public endpoint for the exact pre-aggregated Performance Metrics UI tables.** We reconstruct **equivalent, versioned metrics** from documented run, job, repository-statistics, traffic, and GraphQL Project/Discussion APIs, while retaining UI CSV exports as **reconciliation evidence**. Derived results are labeled **locally reconstructed performance metrics**, not “GitHub UI metrics,” unless a reconciliation job proves match within tolerance.

Timing/usage endpoints (`.../runs/{id}/timing`, workflow `/timing`) are **closing down** (changelog 2025-02-02). Prefer job `started_at` / `completed_at` (and optional `queued_at` where present).

## Access validation (parity)

| Surface | Public API? | Parity path |
|---------|-------------|-------------|
| **Projects** | GraphQL ProjectV2 | Extract projects/fields/items; `read:project` for read-only |
| **Actions usage** | Partial | Operational duration from job timestamps; billable minutes only for GH-hosted private (legacy timing deprecated) |
| **Actions performance UI** | No aggregate export API | Reconstruct from runs + jobs; UI CSV = reconciliation |
| **Commit activity** | REST `stats/commit_activity` | Weekly last-year snapshot |
| **Code frequency** | REST `stats/code_frequency` | Weekly adds/deletes; **422** if >10k commits → `git log --numstat` fallback |
| **Traffic** | REST traffic/* | **14-day retention only** → daily append-only snapshots required |
| **Discussions** | GraphQL preferred | Categories, answers, reactions, comments |

## Architecture (three layers)

```text
GitHub APIs / UI exports
          |
          v
  Raw, dated snapshots  (JSON / CSV / NDJSON + hash)
          |
          v
  Normalized facts      (run_id, job_id, project_item_id, …)
          |
          v
  Derived aggregates    (metric_version, window, generated_at, sources)
          |
          v
  Docs / Projects / ML feature store
```

1. **Raw evidence** — append-only; manual UI CSVs under `docs/ops/generated/`; future API dumps under `ops/github-telemetry/raw/` (or object storage + Git manifest).
2. **Normalized facts** — stable keys: `run_id`, `job_id`, `project_item_id`, `discussion_id`, `issue_number`, `commit_sha`.
3. **Derived aggregates** — period metrics with explicit `metric_version`, query window, generation timestamp, source refs.

Config lives in `ops/github-telemetry/config/` (`metric-policy.yaml`, `sources.yaml`).

## Metric definitions (governed)

See `ops/github-telemetry/config/metric-policy.yaml`.

$$
\text{failure rate} =
\frac{\#(\text{jobs with conclusion in failure set})}
{\#(\text{completed jobs eligible})}
$$

$$
\text{runtime} = \text{completed\_at} - \text{started\_at}
$$

$$
\text{queue time} = \text{started\_at} - \text{queued\_at}
\quad (\text{when queued\_at present})
$$

Default failure set: `failure`, `timed_out` (policy may add `cancelled`, `action_required`).  
Excluded: `skipped`, `neutral`, unfinished.  
Rerun view default: **latest attempt** (raw retains all attempts).

Windows: 7d / 30d / 90d / 365d (UTC).

## In-repo pure reducers

| Module | Role |
|--------|------|
| `she.metrics.job_timestamps` | Duration, queue, run/window aggregates from jobs payloads |
| Future `ops.github_telemetry.collect` | Network fetch (gh/Octokit) → raw |
| Future `ops.github_telemetry.reduce` | Raw → normalized → derived |

Caller owns HTTP; SHE stays pure (stdlib, no network).

## ML pipeline / L1V3 SWE-bench priority

Operational metrics feed the same evidence plane as **MoneyBall / 3L0** and **L1V3 SWE-bench-style evaluation lanes**:

- Failure rate + runtime distributions = reliability features for agent/provider ranking.
- Workflow-failure canaries (e.g. agentic-report) = live stress signals for SHE L0.
- Traffic + commit activity = repo health covariates (not promotion gates alone).
- Authority > ranking: hard policy always dominates leaderboard scores.

Upgrade **L1V3 SWE-bench priority** by treating reconstructed Actions performance + SHE incident fingerprints as first-class inputs to the eval/feature pipeline—not isolated dashboards.

## Implementation sequence

1. Keep dated UI CSVs (done).
2. Job-timestamp reducer (done — `she.metrics`).
3. Metric-policy + sources config (this commit).
4. Collector workflow (scheduled) for runs/jobs → optional derived CSV under `docs/ops/generated/`.
5. Traffic daily (SLO: never miss 14-day window).
6. Projects GraphQL extractor (generic field inspector).
7. Discussions + stats + code-frequency fallback.
8. Reconciliation report vs UI CSV for same window.

## Anti-patterns

- Claiming exact UI parity without reconciliation.
- Building on deprecated `/timing` endpoints.
- Scraping HTML metrics pages.
- Letting dashboards become the only authority (ledger first).
- Deleting prior dated CSV snapshots.

## Related

- `docs/ops/ACTIONS-METRICS-INTEGRATION.md`
- `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md`
- `docs/ops/generated/CORRELATION-2026-08-24.md`
- SHE roadmap: `docs/architecture/SELF-HEALING-ENGINE-ROADMAP.md`
