# GitHub Actions Quota Optimization Plan

**Date:** 2026-11-22  
**Status:** proposed; evidence-first; workflow mutations require cadence-owner review  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Triggering alert (operator supplied):** 78%+ usage; 1,555+ minutes  
**Scope:** distinguish billable compute from operational runtime, then reduce avoidable runner work without weakening required validation.

## Executive decision

Treat the 1,555-minute alert as **unclassified pending billing-scope verification**. The repository is public, and the current quota registry classifies standard GitHub-hosted runner minutes for this public repository as `not-a-quota`. GitHub documents standard hosted runner usage in public repositories and self-hosted runner usage as free. Private/internal repository compute can draw from included account compute.

Therefore, first identify the exact product/SKU, billing owner, billing cycle, repository scope, runner OS, and whether the displayed minutes are operational runtime or billable included-compute usage. Do not disable required CI based solely on an unverified aggregate.

## 1. Resource map

```text
                         GITHUB RESOURCE BUDGET
                                  |
             +--------------------+---------------------+
             |                    |                     |
             v                    v                     v
     COMPUTE / MINUTES       API REQUESTS             STORAGE
     - private/internal     - GITHUB_TOKEN            - Actions cache
       hosted runners       - user/PAT                - artifacts
     - larger runners       - App installations       - logs/retention
     - cloud sandbox         - REST / GraphQL
             |                    |                     |
             v                    v                     v
     job timestamps       rate-limit headers       cache/artifact usage
     + billing report     + per-principal ledger   + retention policy
             |                    |                     |
             +--------------------+---------------------+
                                  |
                                  v
                       QUOTA DISPATCH TREE
                  admission / watermarks / cadence
                                  |
             +--------------------+---------------------+
             |                    |                     |
             v                    v                     v
        EVENT LANES          SCHEDULED LANES        HEAVY COMPUTE
      PR / push / issue      collectors / probes   Muse VM / Buildkite
      workflow completion    watchdogs / census    where appropriate
             |                    |                     |
             +--------------------+---------------------+
                                  |
                                  v
                       EVIDENCE + OPTIMIZATION
               minutes per outcome / API calls / reliability
```

### Resource classes and current evidence

| Resource | Repository evidence | Interpretation |
|---|---|---|
| Actions minutes | `ops/quota/registry.json` | Public standard-runner minutes are classified `not-a-quota`; larger runners are billed |
| Actions minutes live reading | `docs/ops/generated/quota-status.json` | 2026-11-18 row is `unknown`; used and limit are null |
| Actions cache | Same quota snapshot | Status `ok`; 10 GB repository allowance |
| GITHUB_TOKEN API | Same quota snapshot | Status `watch`; 1,000 requests/hour/repository |
| User-token API | Same quota snapshot | Status `unknown`; registry records 5,000 requests/hour |
| App installation API | `ops/quota/registry.json` | Separate installation buckets; per-app attribution where instrumented |
| Operational Actions runtime | `docs/ops/GITHUB-OBSERVABILITY.md` | Reconstruct from job timestamps; runtime is distinct from billable minutes |

The operator-supplied 1,555-minute figure is not independently verified by the repository connector. If the allowance is 2,000 minutes, 1,555 represents 77.75% and leaves 445 minutes; confirm the actual denominator and billing period before using this arithmetic operationally.

## 2. Existing control plane

The repository already has a central quota dispatcher and related controls:

- `.github/workflows/quota-dispatch-tree.yml` — event-driven admission plus a 30-minute schedule backstop.
- `scripts/ci/dispatch_admission.js` — lane-aware admission and in-flight pressure controls.
- `ops/quota/quota-usage.json` — quota registry context and derived series.
- `scripts/quota_usage_pack.py` — deterministic quota pack builder.
- `scripts/dashboards/actions_observe.py` — bounded stride-sampled Actions run observation.
- `she/metrics/job_timestamps` — durable job-duration reduction from `started_at` and `completed_at`.
- `docs/ops/REVIEW-MERGE-QUOTA-AND-HYGIENE.md` — trigger, cancellation, deduplication and adaptive-wait policy.
- `docs/ops/DEVOPS-REGISTER.md` — schedule-delivery and Actions health evidence.

The central dispatcher already uses a single-flight concurrency group and lane-aware admission. Preserve its event triggers, lane authorities and independent concurrency groups while consolidating duplicate cadence owners.

### Existing high-frequency candidates for audit

These are candidates for measurement and cadence review, not instructions to disable them:

- `que-cadence-kick.yml` — five-minute schedule plus push/dispatch recovery.
- `que-feed-collect.yml` — ten-minute schedule.
- `bucket-headroom-watch.yml` — ten-minute schedule.
- `dispatch-watchdog.yml` — fifteen-minute schedule.
- `dispatch-executor.yml` — fifteen-minute schedule.
- `shared-observer-poller.yml` — fifteen-minute schedule.
- `openrouter-bracket-snapshot.yml` — fifteen-minute schedule.
- `quota-dispatch-tree.yml` — thirty-minute backstop plus event wakes.

The QUE cadence kick exists specifically because GitHub schedule delivery has been unreliable under queue saturation. Retain its producer-recovery role unless measured evidence proves an equivalent reliable wake path.

## 3. P0 — immediate actions (0–2 hours)

1. **Classify the 1,555-minute meter.** Capture the billing page/report, exact product/SKU, billing cycle, included allowance, repository scope, and runner OS.
2. **Separate runtime from billable compute.** Public-repository and self-hosted job runtime may be operationally measurable without consuming included billable Actions minutes.
3. **Protect critical work.** Preserve required PR checks, security scans, release/promotion gates, credential checks, and durable evidence writes.
4. **Defer discretionary work only when the billing scope confirms exposure.** Prioritize optional research, duplicate advisory reviews, broad recon sweeps, repeated snapshots, and manually dispatched experiments.
5. **Stop polling loops.** Use completion events and bounded adaptive waits. One state read after a bounded wait replaces repeated run/check/PR polling.
6. **Respect cadence ownership.** Submit cadence changes through the quota-aware cadence (QAC) owner with trigger accounting; preserve workflow IDs when consolidating schedules.

## 4. P1 — establish the real cost ranking (within 24 hours)

Build a 30-day workflow cost table using the GitHub billing detailed usage report and durable Actions job timestamps.

Required columns:

- workflow path and repository;
- billing SKU and runner OS;
- run count, job count and attempts;
- operational job minutes and billable minutes, separately;
- median and p95 job duration;
- skipped, cancelled, failed and successful job counts;
- rerun minutes and cancellation-after-work minutes;
- trigger class: event, schedule, workflow cascade, manual;
- output value / accepted outcome count.

Rank by **billable minutes first**, then operational minutes, then minutes per accepted outcome. Include the top 20 workflows and every workflow with repeated retries or cancellation waste.

Use `started_at` and `completed_at` from workflow-job records. GitHub's legacy workflow/run timing endpoints are closing down; keep them out of new instrumentation. The existing sampled `actions_observations.json` is dated 2026-10-30 and is not a current billing report.

## 5. P1 — execution efficiency changes (24–72 hours)

Apply these controls to measured high-cost workflows:

- Add narrow `paths` / `paths-ignore` filters where the workflow's correctness contract permits them.
- Put cheap admission and change-detection jobs before expensive runner jobs.
- Use job-level conditions to avoid allocating runners for irrelevant events.
- Cache dependency and compiler outputs with lockfile-derived keys and bounded restore scopes.
- Prefer Linux standard runners for portable work; reserve macOS/Windows for platform-specific validation.
- Set explicit `timeout-minutes` based on observed p95 plus documented slack.
- Remove duplicate setup, repeated checkout, redundant dependency installs, and unnecessary matrix dimensions.
- Use matrix `fail-fast` when sibling results have no independent diagnostic value; preserve full matrices where complete evidence is required.
- Use `cancel-in-progress: true` only for idempotent, replaceable work keyed by the true input identity (for example PR + head SHA). Keep it false for migrations, release/promotion, queue work, and evidence writes.
- Avoid automatic reruns. Record failures, classify the cause, and retry only under a bounded policy.

## 6. P1 — cadence and trigger consolidation (3–7 days)

1. Reconcile the generated workflow catalog against actual workflow files and observed runs.
2. Group schedule owners by shared source data and decision nodes.
3. Move eligible cadence decisions into the existing quota dispatch tree; keep lane-specific permissions, concurrency and execution ownership in the lane workflows.
4. Replace periodic polling with `workflow_run`, push, PR, issue or repository-dispatch events when those events represent the real demand signal.
5. Keep a single scheduled reconciler for shared inventories; remove duplicate schedules only after proving an equivalent trigger and freshness SLA.
6. Add a drift guard that rejects unapproved new cron owners and verifies the workflow catalog.
7. Preserve explicit watchdogs for schedule-starvation detection and recovery.

## 7. P2 — offload and execution placement (within 2 weeks)

Use existing compute surfaces for suitable work:

- Muse VM: CPU-bound, checkpointable, low-memory jobs already allocated to that host.
- Buildkite: workloads already mirrored there, using the existing cache volume.
- GitHub Actions: short event-driven CI, security gates, release/promotion, and work that requires GitHub's hosted execution context.

Keep secrets and privileged repository mutations within the approved identity boundary. Every offloaded job must return a signed or hash-verifiable receipt, immutable input identity, result status, and retry/checkpoint state. Do not move work merely to reduce a counter if it increases operator time, reliability risk, or total cost.

## 8. Budget controls and alerts

Use separate thresholds for each verified resource pool:

| Utilization | Control |
|---|---|
| 70% | Watch; publish current trend and forecast |
| 78% | Alert; classify SKU and freeze expansion of discretionary recurring work |
| 85% | Defer low-priority optional work when it consumes the affected pool |
| 90% | Reserve remaining capacity for required CI, security and release work |
| 95% | Stop discretionary dispatches; preserve recovery and owner-authorized critical work |

Thresholds apply only to a confirmed metered pool. Public standard-runner minutes must not be throttled as though they were a private-repository included-minutes quota.

Forecast remaining usage as:

`forecast = observed_usage + (recent_daily_burn × days_remaining)`

Use at least a 7-day trend when available, annotate billing-cycle boundaries, and separate estimates from measured billing data.

## 9. Success measures

Establish a fresh 7-day baseline, then compare matched task cohorts.

- Billable minutes per accepted outcome: reduce by at least 25% where the affected pool is genuinely metered.
- Duplicate/superseded execution minutes: reduce by at least 50%.
- Unnecessary scheduled starts: reduce by at least 50% in migrated lanes while preserving freshness SLAs.
- Required CI correctness and security coverage: 100% retained.
- Retry storms: zero unbounded retries.
- Every quota reading: source, timestamp, pool, unit, window and confidence recorded.
- Every cadence change: trigger count, expected run count, API calls/run and rollback path documented.

A successful optimization improves accepted outcomes per unit of scarce compute, not merely fewer runs.

## 10. Evidence gaps and owner inputs

The current repository evidence does not establish:

- the live 1,555-minute reading, denominator or billing period;
- whether the alert belongs to Actions, Codespaces, cloud sandbox compute, or another metered SKU;
- a current per-workflow billable-minute ranking;
- a current full-fleet schedule/run census;
- whether the user's account-wide usage includes private/internal repositories outside this public repository.

The detailed billing report in GitHub's web UI is required for workflow-path cost attribution. The available connector does not expose the user's billing page or a current detailed billing CSV.

## 11. Source of truth

- `ops/quota/registry.json`
- `docs/ops/generated/quota-status.json`
- `ops/quota/quota-usage.json`
- `ops/compute/ALLOCATION.md`
- `docs/ops/GITHUB-OBSERVABILITY.md`
- `docs/ops/ACTIONS-METRICS-INTEGRATION.md`
- `docs/ops/QUOTA-ATTRIBUTION.md`
- `docs/ops/DEVOPS-REGISTER.md`
- `docs/ops/REVIEW-MERGE-QUOTA-AND-HYGIENE.md`
- `docs/proposals/active/quota-aware-cadence-rfp/RFP.md`

External billing references:

- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/billing/reference/billing-reports
- https://docs.github.com/en/actions/how-tos/monitor-workflows/view-job-execution-time

**Promotion rule:** this document is a plan-only change. Schedule changes, workflow disablement, concurrency changes, and runner migrations require a measured cost ranking, cadence-owner approval, regression coverage, and a rollback path.
