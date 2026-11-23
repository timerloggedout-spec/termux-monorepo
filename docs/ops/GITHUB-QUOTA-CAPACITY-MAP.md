# GitHub Quota & Capacity Map

**Snapshot:** 2026-11-22  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Default branch:** `master`  
**Status:** Reconnaissance baseline; live balances and account-plan settings remain partially unobserved.

## 1. Evidence model

Use four evidence classes throughout this map:

- **DOCUMENTED** — published GitHub product documentation.
- **LIVE** — current repository metadata, workflow definitions, API responses, or generated feeds.
- **HISTORICAL** — timestamped incident records and prior measured events.
- **GAP / DISPUTED** — account-side settings, live balances, or conflicting measurements awaiting direct verification.

Published entitlements describe capacity. They do not establish remaining balance. For live API enforcement, capture the response's `x-ratelimit-*` headers; GitHub identifies those headers as authoritative when they differ from `GET /rate_limit`.

## 2. Repository and workload snapshot

### Repository facts — LIVE

| Signal | Observed |
|---|---:|
| Visibility | Public |
| Owner type | User account |
| Default branch | `master` |
| Workflow files under `.github/workflows` | 327 |
| Quota registry services | 172 |
| GitHub-provider registry records | 11 |

The 327 workflow files are a repository inventory count. GitHub's published Actions limits page provides execution, queue, concurrency, storage, and rate ceilings; this reconnaissance found no published maximum workflow-file count.

### Recent Actions run sample — LIVE

A paginated sample across ten API pages yielded **956 unique run IDs** between **2026-11-22 16:02:53Z** and **16:16:47Z**. Pages were read while new runs were arriving, so treat 956 as a lower-bound sample rather than a complete fixed-window census.

| Signal | Sample |
|---|---:|
| Unique runs | 956 |
| Distinct workflow names | 48 |
| Event-equivalent rate | ~4,100 runs/hour |
| Completed | 940 |
| In progress | 13 |
| Pending | 2 |
| Queued | 1 |

Event mix:

| Event | Runs |
|---|---:|
| `push` | 391 |
| `workflow_run` | 320 |
| `pull_request` | 185 |
| `pull_request_target` | 30 |
| `dynamic` | 12 |
| `pull_request_review` | 7 |
| `pull_request_review_comment` | 6 |
| `workflow_dispatch` | 3 |
| `create` | 2 |

Conclusions in the sample: 414 success, 251 cancelled, 125 skipped, 119 action_required, 31 failure, and 16 still without a terminal conclusion.

Highest-volume workflows in this sample:

- `repo-tracking-collect`: 64
- `Quota Dispatch Tree`: 64
- `lane events recorder`: 63
- `hark enqueue on failure`: 51
- `n8n SHE bridge`: 51

This is a visible fan-out pattern: `workflow_run` alone accounts for 320 of the sampled runs. The sample's average rate sits well below the published 1,500-trigger-events/10-second and 500-runs-queued/10-second ceilings. Burst maxima per 10-second interval remain unmeasured.

The repository's historical rate-limit audit records a separate one-hour window with 4,799 runs, 51 installation-limit annotations across 28 runs, and bursts of 100 runs in 19 seconds. See [rate-limit-refix-audit.md](rate-limit-refix-audit.md). Treat those figures as historical incident evidence, not current balances.

The workflow-runs API returned `total_count=40,000` in the unfiltered repository query. A latest run also carried a per-workflow `run_number=51,752`; those fields measure different things. Exact lifetime run count remains UNKNOWN. For filtered run queries, GitHub documents a 1,000-result retrieval ceiling for several filters; date-sliced collection is required for complete historical reconstruction.

## 3. GitHub Actions execution ceilings

**DOCUMENTED — current GitHub Actions limits page**

| Surface | Published limit | Scope / behavior |
|---|---:|---|
| Workflow run lifetime | 35 days | Includes execution, waiting, and approval time; run is cancelled at the ceiling |
| Environment approval wait | 30 days | Per approval gate |
| Matrix expansion | 256 jobs | Per workflow run |
| Re-runs | 50 | Full and selected-job re-runs combined |
| Workflow file size | 500 KB | Per workflow file |
| Check runs | 50,000 | Per check suite, including Actions and Checks API runs |
| Trigger events | 1,500 / 10 seconds | Per repository |
| Workflow runs queued | 500 / 10 seconds | Platform queue ceiling |
| Concurrency-group queue | 100 | Per group when `queue: max` is used |
| GitHub-hosted job duration | 6 hours | Per job |
| Self-hosted runner registrations | 1,500 / 5 minutes | Per repository, organization, or enterprise |
| Runners per self-hosted runner group | 10,000 | Concurrent registrations |
| Self-hosted job duration | 5 days | Per job |
| Self-hosted job queue time | 24 hours | Queued jobs expire at the ceiling |

### Hosted runner concurrency

| Account plan | Total standard hosted jobs | macOS maximum |
|---|---:|---:|
| Free | 20 | 5 |
| Pro | 40 | 5 |
| Team | 60 | 5 |
| Enterprise | 500 | 50 |

Larger-runner concurrency is configured by runner type. Published maximums are normally 1,000 Linux CPU jobs, 100 GPU jobs, and 5/50 macOS jobs for Team/Enterprise respectively. macOS concurrency is shared between standard and larger runners. Larger-runner static IP capacity is 10 IPs per organization and enterprise.

**Account plan is UNKNOWN.** Repository ownership is a personal user account; the GitHub connector exposes repository permissions and visibility, not the owner's billing tier. Therefore the applicable standard-runner concurrency ceiling is either 20 or 40 for a Free/Pro personal plan, subject to account-side confirmation.

## 4. Actions billing, artifacts, and cache

### Public-repository compute

- Standard GitHub-hosted runner usage in public repositories is free.
- Self-hosted runner usage in public repositories is free.
- Larger GitHub-hosted runners are billed even for public repositories.
- Private/internal standard-runner usage draws from the account's monthly included compute credit. Current published credits are $12 Free, $18 Pro, $18 Team, and $300 Enterprise Cloud. The credit is monetary, not a fixed minute allowance.

This repository is public, so standard hosted-runner minutes are a free-use surface. The 6-hour job ceiling, plan concurrency, trigger/queue ceilings, and dependent API quotas still apply.

### Included Actions storage

| Plan | Artifact storage | Cache storage / repo | Custom image storage | Included compute credit |
|---|---:|---:|---:|---:|
| Free | 500 MB | 10 GB | — | $12 |
| Pro | 1 GB | 10 GB | — | $18 |
| Free for organizations | 500 MB | 10 GB | — | $12 |
| Team | 2 GB | 10 GB | 75 GB | $18 |
| Enterprise Cloud | 50 GB | 10 GB | 150 GB | $300 |

Actions artifact storage and GitHub Packages storage share the same included storage allowance. Cache storage is a separate per-repository pool.

### Cache

| Limit | Published value |
|---|---:|
| Default cache size | 10 GB / repository |
| Default inactive-entry retention | 7 days |
| Cache uploads | 200 / minute / repository |
| Cache downloads | 1,500 / minute / repository |
| Cache deletes | 400 / minute / repository |
| Configurable maximum for user-owned repositories | Up to 10,000 GB / repository |
| Public-repository cache retention configuration | 1–90 days |

The 10 GB default can be increased through repository cache settings when the account and payment configuration qualify. At capacity, GitHub evicts least-recently-used entries; high churn can create cache thrashing.

### Artifacts, logs, checks, and workflow-run retention

- Default retention: 90 days.
- Public repository configuration: 1–90 days.
- Private/internal configuration: 1–400 days.
- From 2026-10-01, the retention policy also applies to checks, workflow runs, and commit statuses, alongside artifacts and logs.
- Per-artifact `retention-days` values can shorten the repository default.

The registry currently records a 90-day artifact-retention value from an older secondary source. Refresh it against the official repository retention documentation and record the actual repository setting.

## 5. REST API quota families

### Primary rate limits — DOCUMENTED

| Credential class | Primary allowance | Sharing boundary |
|---|---:|---|
| Unauthenticated public-data requests | 60 requests/hour | Originating IP |
| Personal access token / user-authenticated requests | 5,000 requests/hour | Authenticated user; multiple PATs do not create additional user capacity |
| GitHub App installation token | 5,000 requests/hour minimum | Per installation |
| GitHub App installation scaling | +50/hour per repository above 20; +50/hour per organization user above 20 | Maximum 12,500/hour for non-Enterprise Cloud installations |
| GitHub App installation on Enterprise Cloud organization | 15,000 requests/hour | Per installation |
| `GITHUB_TOKEN` | 1,000 requests/hour | Per repository; shared by workflows in that repository |
| `GITHUB_TOKEN` accessing Enterprise Cloud resources | 15,000 requests/hour | Per repository |
| OAuth app client credentials for public data | 5,000 requests/hour; 15,000 for Enterprise Cloud-owned apps | Per OAuth app |
| Git LFS API | 300 requests/minute unauthenticated; 3,000 authenticated | Separate LFS bucket |

A GitHub App user access token follows the authenticated user's limit and shares that user budget with PAT and OAuth user-authenticated requests. Installation tokens are the separate-capacity path. Each installation has its own bucket.

### Secondary rate limits — DOCUMENTED, dynamically enforced

| Constraint | Published value |
|---|---:|
| Concurrent REST + GraphQL requests | 100 |
| REST endpoint secondary points | 900 points/minute per endpoint |
| GraphQL secondary points | 2,000 points/minute |
| Total API CPU time | 90 seconds per 60 seconds |
| GraphQL CPU time within that total | 60 seconds per 60 seconds |
| Content-generating requests | Generally 80/minute and 500/hour |
| OAuth access-token requests | 2,000/hour |

Most REST GET/HEAD/OPTIONS requests cost 1 secondary point; most POST/PATCH/PUT/DELETE requests cost 5. Some endpoints have unpublished point costs. GitHub also applies adaptive secondary controls for resource-intensive bursts and publishes no endpoint for querying current secondary-limit headroom.

On a primary-limit 403/429, wait until the `x-ratelimit-reset` epoch. On a secondary-limit 403/429, honor `Retry-After`; otherwise wait at least one minute and use exponential backoff. Repeated attempts during a rate-limit event risk integration suspension.

### Search API

| Surface | Authenticated limit | Result ceiling |
|---|---:|---:|
| REST search endpoints | 30 requests/minute | 1,000 results/query |
| REST code search | 10 requests/minute | 1,000 results/query |
| Unauthenticated search | 10 requests/minute | 1,000 results/query |

Search has a separate primary bucket from REST core. Code search has its own bucket. Search queries can also return incomplete results after a timeout or repository-scope limit.

### GraphQL API

| Credential class | Primary allowance |
|---|---:|
| User | 5,000 points/hour |
| GitHub App installation outside Enterprise Cloud | 5,000 points/hour minimum; scales to 12,500 |
| GitHub App installation on Enterprise Cloud | 10,000 points/hour |
| `GITHUB_TOKEN` | 1,000 points/hour/repository; 15,000 for Enterprise Cloud resources |

Additional GraphQL constraints: 500,000 nodes per query; connection arguments `first` and `last` are required and each ranges from 1–100. Query point cost depends on nested connection fan-out. GraphQL primary points and secondary points are separate meters.

### Rate-limit resource families to capture

The REST `GET /rate_limit` response can expose separate resources including `core`, `search`, `code_search`, `graphql`, `integration_manifest`, `dependency_snapshots`, `dependency_sbom`, `code_scanning_upload`, and `actions_runner_registration`. Capture the full response per credential class. The endpoint itself consumes no primary REST quota, while it can consume secondary capacity. Per-request response headers remain the enforcement authority.

## 6. Adjacent GitHub product quotas

### GitHub Packages

| Plan | Storage | Data transfer / month |
|---|---:|---:|
| Free | 500 MB | 1 GB |
| Pro | 2 GB | 10 GB |
| Free for organizations | 500 MB | 1 GB |
| Team | 2 GB | 10 GB |
| Enterprise Cloud | 50 GB | 100 GB |

Public packages and inbound transfers are free. Actions artifact storage and Packages storage share the included storage allowance. Container Registry image storage and bandwidth are currently free under the published policy.

### Git LFS

| Plan | Storage | Download bandwidth / month |
|---|---:|---:|
| Free / Pro / Free for organizations | 10 GiB | 10 GiB |
| Team / Enterprise Cloud | 250 GiB | 250 GiB |

LFS uses a separate API bucket: 300 requests/minute unauthenticated and 3,000 authenticated. The batch API processes 100 objects per request by default.

### GitHub Pages

- One user or organization site per account.
- Published site maximum: 1 GB.
- Source repository recommended maximum: 1 GB.
- Deployment timeout: 10 minutes.
- Soft bandwidth allowance: 100 GB/month.
- Soft build allowance: 10 builds/hour for the native Pages build service.
- The 10-build/hour soft limit is exempt for custom GitHub Actions build-and-publish workflows.

The repository has a `pages build and deployment` workflow. Confirm the actual Pages source mode and published-site size before applying the native build-service ceiling.

### Codespaces

Personal-account included usage:

| Plan | Core hours/month | Storage/month |
|---|---:|---:|
| Free | 120 | 15 GB |
| Pro | 180 | 20 GB |

Organizations receive no included free Codespaces quota. Compute and storage are separate meters. The repository's earlier operations census recorded three Codespaces; current account usage and plan remain UNKNOWN.

### Copilot

The current quota registry records Copilot Free as a provider-side allowance with an unknown numeric cap and no live usage reader. Keep Copilot requests/premium requests separate from Actions minutes, REST API, and runner concurrency.

## 7. Live GitHub App installation inventory

The repository's `ops/github-apps/PROCESS.json` contains 11 fleet Apps. The current `bucket-headroom.json` feed was generated at **2026-11-22 10:18:41Z**, with a configured 10-minute poll interval.

| Bucket | Last observed limit | Used | Remaining | Feed state |
|---|---:|---:|---:|---|
| Swarm installation | 12,500/hour | 221 | 12,279 | OK |
| Collector installation | 5,000/hour | 778 | 4,222 | OK |
| CrossReference installation | 5,000/hour | 0 | 5,000 | OK |
| Workflow `GITHUB_TOKEN` read | 5,000 | 2,211 | 2,789 | DISPUTED |
| PAT core | — | — | — | UNREADABLE |

Eight fleet App installation buckets are marked `sec03_unprovisioned`: Publisher, Reviewer, Gate, Lifecycle, Repostory, Moneyball, DelphiOracle, and Understudy. The PAT bucket is marked `no_read_supplied`. The feed also carries an unreadable Gemini provider-arm observation. Overall: 4 readable/OK buckets and 10 unreadable buckets out of 14.

The Swarm 12,500/hour read is consistent with GitHub's documented non-Enterprise installation scaling ceiling. The exact repository/user-count contribution should be revalidated from installation metadata.

### Critical GITHUB_TOKEN discrepancy

Three sources disagree:

1. GitHub's current Actions and REST API documentation states **1,000 requests/hour/repository** for `GITHUB_TOKEN`.
2. `docs/ops/generated/quota-status.json`, generated 2026-11-18, records a 1,000/hour limit.
3. `ops/que/feeds/bucket-headroom.json`, generated 2026-11-22 10:18Z, records 5,000 for the `github.token` `/rate_limit` read.

Classify the 5,000 read as **DISPUTED**, rather than a confirmed increase. Resolve it by capturing `x-ratelimit-limit`, `x-ratelimit-resource`, `x-ratelimit-remaining`, and `x-ratelimit-reset` from a counted API request made with the workflow's actual `GITHUB_TOKEN`. GitHub explicitly identifies response headers as authoritative when they differ from `GET /rate_limit`.

### Freshness gaps

- Bucket headroom feed: 2026-11-22 10:18Z; nearly six hours old at the 16:18Z reconnaissance point, despite the 10-minute cadence.
- Canonical quota readings: generated 2026-11-18.
- Quota usage pack: generated 2026-11-19.
- PAT core series: latest point 2026-11-02.
- Rate-limit event register: latest recorded event 2026-11-12.

Current balances therefore remain UNKNOWN beyond the dated observations above.

## 8. Existing repository instrumentation

| Component | Current role |
|---|---|
| `.github/workflows/bucket-headroom-watch.yml` | 10-minute scheduled headroom watcher; PAT, workflow token, and selected App installation reads |
| `scripts/ops/bucket_headroom.py` | Reads `/rate_limit`, projects burn-to-reset, emits typed headroom and alert transitions |
| `ops/que/feeds/bucket-headroom.json` | Latest published bucket feed |
| `ops/quota/rate-limit-events.json` | Append-only primary/secondary/Search incident register |
| `docs/ops/rate-limit-refix-audit.md` | Trigger-churn and installation-limit root-cause audit |
| `.github/workflows/quota-analysis.yml` | Read-only quota registry, snapshot, allocation, and coverage validation |
| `.github/workflows/quota-allocation-planner.yml` | Weekly and event-driven allocation plan refresh |
| `.github/workflows/quota-usage-series-refresh.yml` | Input-driven quota usage series refresh |

The existing instrumentation is a strong foundation. The next work is freshness repair, bucket coverage, header-level enforcement evidence, and full registry representation.

## 9. Priority closure plan

1. **Restore freshness:** verify the 10-minute headroom workflow's latest run, failure state, and artifact; enforce a stale-feed state once age exceeds the polling SLA.
2. **Resolve the token discrepancy:** record actual `GITHUB_TOKEN` response headers beside the `/rate_limit` result.
3. **Close App coverage:** provision SEC-03 mint/read paths for the eight unreadable fleet Apps, or explicitly classify each as intentionally dormant with owner evidence.
4. **Restore PAT visibility:** establish the intended PAT secret binding and capture its core/search/GraphQL resource families.
5. **Expand the quota registry:** add Actions trigger/queue/concurrency/execution ceilings, cache operation rates, artifact/package shared storage, REST search, GraphQL, secondary limits, Pages, LFS, and Codespaces as distinct resource records.
6. **Measure burst shape:** add rolling 10-second and 60-second event/run counters, per-workflow event attribution, queue depth, and actual active job concurrency.
7. **Reconcile account settings:** capture plan tier, included compute balance, artifact/Packages usage, cache configuration and usage, retention settings, Codespaces usage, LFS usage, and runner-group configuration.
8. **Preserve source classes:** store published entitlement, observed limit, remaining balance, reset time, credential class, repository/install scope, and freshness as separate fields.

## 10. Source register

### GitHub documentation

- [Actions limits](https://docs.github.com/en/actions/reference/limits)
- [Actions billing and usage](https://docs.github.com/en/actions/concepts/billing-and-usage)
- [Product usage included with each plan](https://docs.github.com/en/billing/reference/product-usage-included)
- [REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- [REST API rate-limit resources](https://docs.github.com/en/rest/rate-limit/rate-limit)
- [REST API search limits](https://docs.github.com/en/rest/search)
- [GraphQL rate and query limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api)
- [Dependency cache limits and eviction](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
- [Repository Actions retention settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [GitHub Packages billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages)
- [Git LFS billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs)
- [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [Codespaces included usage](https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-included-usage)
- [Actions workflow-runs API](https://docs.github.com/en/rest/actions/workflow-runs)

### Repository evidence

- `ops/quota/registry.json`
- `docs/ops/generated/quota-status.json`
- `ops/que/feeds/bucket-headroom.json`
- `ops/quota/quota-usage.json`
- `ops/quota/rate-limit-events.json`
- `ops/github-apps/PROCESS.json`
- `docs/ops/rate-limit-refix-audit.md`
- `.github/workflows/bucket-headroom-watch.yml`
- `.github/workflows/quota-analysis.yml`
- `.github/workflows/quota-allocation-planner.yml`
- `.github/workflows/quota-usage-series-refresh.yml`

## 11. Access boundary

The GitHub connector verified repository metadata and read public repository contents, workflow-run records, and the committed quota feeds. Its supported API surface excludes account billing, secrets, and private settings endpoints. Therefore account plan, billing balances, live private token values, and repository Actions settings remain owner-side evidence requirements.


## 12. Follow-up live headroom and cadence evidence — 2026-11-23

A subsequent feed publication at **2026-11-23T03:55:42Z** confirms that the scheduled watcher resumed publishing after the earlier 2026-11-22 10:18Z snapshot. At the 2026-11-23T06:51Z review point, the feed was approximately **2 hours 56 minutes old**, still outside its configured 10-minute cadence.

The latest matching publication commits were recorded at 2026-11-23 03:55Z, 2026-11-22 23:26Z, 17:54Z, 10:18Z, and 02:33Z. The observed inter-publication gaps were approximately **4h29m, 5h32m, 7h36m, and 7h45m**. These observations show a persistent publication-cadence gap; they do not identify the precise scheduler, queue, or workflow failure cause.

GitHub documents scheduled events as best-effort: high Actions load can delay them, the start of each hour is a known high-load period, and queued schedule events can be dropped. This workflow's `*/10` schedule includes minute `00`; shifting the six polls to off-hour minutes (for example `7,17,27,37,47,57`) is a documented mitigation candidate, while an external dispatch fallback provides a stronger recovery path. See [GitHub schedule event behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Latest feed readings:

| Bucket | Limit | Used | Remaining | State |
|---|---:|---:|---:|---|
| Swarm installation | 12,500/hour | 8,452 | 4,048 | OK |
| Collector installation | 5,000/hour | 34 | 4,966 | OK |
| CrossReference installation | 5,000/hour | 0 | 5,000 | OK |
| Workflow `GITHUB_TOKEN` /rate_limit read | 5,000 | 87 | 4,913 | DISPUTED |
| PAT core | — | — | — | UNREADABLE |

Eight fleet App buckets remain unreadable with `sec03_unprovisioned`; the PAT core bucket remains `no_read_supplied`; the Gemini provider-arm remains unreadable. The feed therefore still reports 4 readable buckets and 10 unreadable buckets across its 14-bucket inventory.

The `GITHUB_TOKEN` reading remains a `/rate_limit` observation. The watcher currently stores the JSON resource values and omits response-header evidence. The 5,000 reading remains disputed against the documented 1,000/hour/repository allowance and the canonical 1,000/hour snapshot. Capture `x-ratelimit-limit`, `x-ratelimit-resource`, `x-ratelimit-remaining`, and `x-ratelimit-reset` in a follow-up implementation before changing the registry's entitlement value.
