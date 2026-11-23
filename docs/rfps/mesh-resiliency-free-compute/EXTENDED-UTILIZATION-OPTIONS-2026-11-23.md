# Extended Mesh Utilization Options — 2026-11-23

**Tracking lane:** [Mesh-resiliency RFP #1622](https://github.com/timerloggedout-spec/termux-monorepo/issues/1622)  
**Evidence date:** 2026-11-23  
**Method:** official vendor documentation + read-only repository inspection + read-only connected Cloudflare account inventory  
**Decision state:** research expanded; all six candidates remain unranked; provider selection and provisioning require separate approval.

## Executive result

The mesh has more useful surfaces than the VM/container shortlist suggests. The six extended options below cover short-lived compute, serverless execution, lightweight application hosting, temporary preview execution, and network sharing. Their capabilities differ materially, so the scheduler should classify each by workload shape rather than treat every row as interchangeable compute.

Two existing assets deserve immediate utilization work before additional signup activity:

1. **GitHub Codespaces** — personal-account allowance of 120 core-hours and 15 GB-month storage on GitHub Free. The repository already has Codespaces workflows and a Codespaces resource history; actual usage remains an account-billing measurement.
2. **Cloudflare Workers + D1** — live account inventory shows deployed Workers and D1 databases. This is an existing execution/data surface with an empty Queues inventory and R2 activation still pending.

Render also has repository-side wiring through a GitHub Actions → GHCR → image-backed Render path. The Render account inventory remains pending workspace confirmation.

## 1. Six extended utilization options

All values below are published plan entitlements. Account eligibility, current remaining capacity, actual billing posture, and region-specific availability remain separate observations.

| Candidate | Class | Published free shape | Operational constraints | Mesh fit | Evidence state |
|---|---|---|---|---|---|
| **SnapDeploy** | Managed container | Up to 4 containers; 512 MB RAM / 0.25 vCPU each; 100 shared container-hours/month; 10 deploys/day; card requirement: none | Sleeps after ~15 min idle; browser visit wakes in ~60 sec; scripts/cron/CI calls receive the wake response; persistent disk: none; deploy failures count toward cap | Interactive demos, low-traffic previews, manual-triggered tasks; weak fit for unattended workers and scheduled jobs | Official docs retrieved 2026-11-23; source page says last verified 2026-09-28 |
| **Leapcell Hobby** | Serverless + app runtime | 20 projects/services; up to 3 vCPU / 4 GB per project; one free PostgreSQL database; 100,000 invocations/month; 3 GB-hours/month; 2 GB egress/month; 10 GB ingress/month; 10,000 async invocations/month; 100,000 Redis commands/month; 1 GB Redis bandwidth/month; 60 build minutes/month; 100 MB log ingestion/month; 900 sec invocation timeout | Metered overage pricing is published; persistent servers are listed on paid Plus rather than Hobby; free Postgres is listed | Strong candidate for bounded webhook handlers, short API jobs, and serverless batch slices; preserve external durable state | Official pricing page retrieved 2026-11-23 |
| **Appwrite Free** | Backend platform + functions | 750,000 executions/month; 100 GB-hours/month; 5 GB bandwidth/month; 2 GB storage; 75,000 MAU; 1 database + 1 bucket + 2 functions/project; 2 projects/organization; 0.5 CPU / 512 MB; 15-minute builds; 900-second max async function timeout | Projects pause after 7 inactive days and delete after 90 paused days; Free intervals start at 60 minutes; cron schedules require a paid plan from 2026-10-19 | Candidate for event-triggered functions and auth/data services; recurring jobs need hourly cadence and a reactivation owner | Official pricing + changelog retrieved 2026-11-23 |
| **alwaysdata Free** | Shared PaaS / website hosting | 1 GB SSD; 256 MB RAM; 1/4 CPU; 3 days of backups; lifetime free offer | Free plan is limited to personal use; websites use the alwaysdata.net address; free plan excludes running services | Documentation/static site and small personal web workloads only; exclude from general-purpose worker pool | Official pricing + plan restrictions retrieved 2026-11-23 |
| **Back4app Containers Free** | Docker container preview | 0.25 CPU; 256 MB RAM; 100 GB transfer; GitHub deployment; payment method: unknown | Back4app engineering update records a 60-minute temporary URL lifetime per free deployment (change dated 2026-09-15); current pricing page omits this URL lifetime, so public documentation is internally inconsistent | Ephemeral demos, smoke tests, and deployment previews; persistent service placement requires current dashboard confirmation or paid plan evidence | Official pricing and vendor engineering article conflict; conditional |
| **zrok Free** | Zero-trust network sharing | 5 GB/day; 25 environments; 50 share backends; 50 private access frontends; card requirement: none | Provides secure resource sharing/tunneling, compute capacity: none; self-hosted edition is Apache-2.0 | Network ingress and private resource sharing adjunct; pair with a separate worker and explicit access policy | Official pricing page retrieved 2026-11-23 |

### Candidate-specific evidence

**SnapDeploy**
- Free-tier documentation: https://snapdeploy.dev/docs/free-tier
- Pricing: https://snapdeploy.dev/pricing
- FAQ and automation wake behavior: https://snapdeploy.dev/docs/faq
- The key scheduling constraint is the wake path: a browser visit wakes a sleeping free container in about 60 seconds, while automated server-to-server requests receive HTTP 503 and leave the container asleep. Keep scheduled workers on an always-on or alternative execution surface.

**Leapcell**
- Official pricing: https://www.leapcell.io/pricing
- Hobby includes 20 projects, 100K monthly serverless invocations, 3 GB-hours, 2 GB egress, 10 GB ingress, and a 900-second invocation timeout.
- Plus adds persistent servers and higher included quotas. Treat Hobby as a serverless/scale-to-zero lane; meter invocations, duration, and egress independently.

**Appwrite**
- Official pricing: https://appwrite.io/pricing
- Free-plan inactivity pause: https://appwrite.io/changelog/entry/2026-02-20-1
- Paused-project deletion after 90 days: https://appwrite.io/changelog/entry/2026-06-29
- Free cron schedules move to paid plans: https://appwrite.io/changelog/entry/2026-10-15-1
- Function interval and timeout contract: https://appwrite.io/docs/products/functions/execute
- Seven consecutive days without Console development activity pauses the project. Paused projects suspend scheduled functions and background processes; projects paused for 90 days are deleted. From 2026-10-19, Appwrite Cloud Free uses intervals of 60 minutes or longer; cron schedules require a paid plan. Function timeout tops out at 900 seconds. Add a maintenance owner, reactivation receipt, and schedule-compatibility check before relying on Appwrite for recurring tasks.

**alwaysdata**
- Official offers: https://www.alwaysdata.com/en/offers/
- Official free-plan restrictions: https://help.alwaysdata.com/en/docs/admin-billing/billing/public-cloud-prices/
- Free offer has 1 GB disk, 256 MB RAM, quarter CPU, and three backup days. The vendor restricts the free plan to personal use and website hosting on the alwaysdata.net address; running services belongs outside the free-plan fit.

**Back4app Containers**
- Official pricing: https://www.back4app.com/pricing/container-as-a-service
- Official deployment guide: https://www.back4app.com/docs-containers
- Vendor engineering article with September 15, 2026 change: https://www.back4app.com/blog/deploy-node-app-dockerfile-back4app
- The pricing page presents the Free container as a $0 plan with 0.25 CPU, 256 MB RAM, and 100 GB transfer; its FAQ confirms card requirement: none. The engineering article records temporary URLs expiring after 60 minutes, with free auto-deploy disabled and a separate backend required for persistence. Preserve the URL-lifetime and deployment constraints as disqualifiers for persistent public endpoints.

**zrok**
- Official pricing: https://zrok.io/pricing/
- The free allowance is a daily transfer and sharing quota. zrok adds network reachability and access mediation; it contributes zero compute capacity by itself.

## 2. Existing mesh surfaces — utilization first

### GitHub Codespaces

- Official personal-account allowance: 120 core-hours/month and 15 GB-month storage on GitHub Free; GitHub Pro lists 180 core-hours and 20 GB-month.
- Sources: https://docs.github.com/en/billing/concepts/product-billing/github-codespaces and https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-included-usage
- Personal-account allowance applies to personal accounts; organization-owned Codespaces use organization billing.
- The repository already contains Codespaces workflows and a Codespaces resource history. Treat the free quota as a personal-account budget and capture current usage before placing routine heavy builds there.
- Priority: **HOLD — owner decision required**. Capture billing actuals and resume utilization planning only after the owner reopens the lane.

### Cloudflare Workers, D1, Queues, and R2

**Live connected-account observation — 2026-11-23 (read-only API inventory):**
- 2 deployed Worker scripts were returned.
- 3 D1 databases were returned; their reported database file sizes total approximately 86 KB and table counts total 4.
- The deployed `tmx-device-queue` Worker has a D1 binding and five deployment records; its latest deployment was 2026-10-22.
- The `admin-graph-live` Worker has a D1 binding and a 2026-11-17 deployment.
- Cloudflare Queues inventory returned 0 queues. The existing `tmx-device-queue` Worker is a D1-backed pull-queue rendezvous, distinct from the Cloudflare Queues product.
- R2 bucket inventory returned an activation-required response. The account's R2 activation status is pending.
- Worker observability returned 0 events for 2026-10-24 through 2026-11-24; both scripts reported `logpush=false` and unset observability configuration. GraphQL Workers Analytics independently returned 80 requests, 0 errors, and 0 subrequests across the two scripts for that 30-day window: 70 requests on `tmx-device-queue` and 10 on `admin-graph-live`. Observed CPU quantiles ranged from about 0.5 ms to 3.25 ms. D1 GraphQL Analytics returned 57 reads and 3 writes across the three databases for the same 30-day window; `termux-surface-matrix` had no usage row. Billing usage reads still require Billing Read.
- Account billing usage reads returned an authorization response requiring Billing Read. Current request/billing usage therefore remains unknown.
- The connected account identity and account/database IDs are excluded from this public evidence record.

**Published free limits:**
- Workers Free: 100,000 requests/day; 10 ms CPU/invocation; 128 MB memory; 50 subrequests/request. https://developers.cloudflare.com/workers/platform/limits/
- D1 Free: 10 databases/account; 500 MB/database; 5 GB total account storage; 5 million rows read/day; 100,000 rows written/day; 7-day Time Travel. https://developers.cloudflare.com/d1/platform/limits/ and https://developers.cloudflare.com/workers/platform/pricing/
- Queues Free: 10,000 operations/day, 10,000 queues/account, 24-hour message retention. https://developers.cloudflare.com/queues/platform/pricing/ and https://developers.cloudflare.com/changelog/post/2026-02-04-queues-free-plan/
- R2 Free: 10 GB-month Standard storage, 1 million Class A operations/month, 10 million Class B operations/month, free egress. https://developers.cloudflare.com/r2/pricing/

**Priority:** **P0 — finish existing lane**. Preserve the measured 80 Worker requests and 57 D1 reads / 3 writes as the initial baseline; obtain Billing Read for financial usage, document the deployed Worker/D1 bindings, evaluate Cloudflare Queues for receiver-mesh buffering, and route R2 activation through the account owner. Keep D1 write budgets explicit; the existing Neon exhaustion incident demonstrates why a quota read is observational; runtime admission requires a separate enforcement gate.

## 3. Render reconciliation — repository wiring exists

The repository already carries an image-backed Render service path:

1. `.github/workflows/readme-extractor-image.yml` builds a small BusyBox image from a sparse checkout and pushes `ghcr.io/timerloggedout-spec/termux-readme-extractor` with `latest` and SHA-tagged references.
2. `ops/render-image/Dockerfile` serves the repository README.
3. `ops/render-image/README.md` records a separate image-backed Render web service pulling the GHCR image.
4. `scripts/quota_poll.py` contains `render_reader`, gated on `RENDER_API_KEY`, with a service identifier default and deploy/bandwidth reads.
5. `docs/ops/QUOTA-REGISTRY.md` records Render's quota reader and distinguishes deploy-wall-clock estimates from authoritative billing-dashboard usage.

Official Render sources:
- Free service limits: https://render.com/docs/free
- Prebuilt image deployment: https://render.com/docs/deploying-an-image
- Pipeline billing: https://render.com/docs/build-pipeline

**Reconciliation:** the root deployment-lane SSOT currently labels Render as an unproven candidate. The repo image-build workflow and image-backed service README establish repository wiring. Account service health, public URL, source digest, and latest successful deploy remain unverified. The lane status should therefore read **REPO-WIRED / PROVIDER-HEALTH PENDING** until the Render workspace is confirmed and its service/event inventory is inspected.

## 4. GitLab and the 10-minute watcher

GitLab remains two separate lanes:
- GitLab CI: opt-in secondary validation, registered with compute/storage quota entitlements in PR #5767; namespace plan and live usage remain account-side measurements.
- GitLab mirror/webhook: separate repository-redundancy lane, with the last recorded webhook failure 429 in the integration-mesh history.

The 10-minute watcher is `.github/workflows/bucket-headroom-watch.yml`:
- `*/10 * * * *` schedule, inside the repository's 5-minute cadence floor;
- reads `/rate_limit` for PAT core, repository `GITHUB_TOKEN`, Swarm App, Collector App, CrossReference App, and every fleet GitHub App installation that the workflow can enumerate;
- derives alerts from each bucket's observed burn and reset time, projecting exhaustion before the bucket's own reset;
- writes `que-governor-event/v1` transition receipts to `ops/que/events/` and updates one standing issue;
- supports `workflow_dispatch` with dry-run and synthetic-drill inputs.

This is distinct from the 10-minute `timeout-minutes` on the GitLab validation job and the 10-minute timeout on the GHCR image-build job. Those are per-run execution ceilings, separate from watcher schedules.

Related schedules:
- `que-feed-collect.yml` also uses a 10-minute schedule.
- `que-cadence-kick.yml` runs every 5 minutes, also waking on qualifying master pushes and dispatching stale producers.
- GitHub schedule delivery is best-effort. The GitHub quota capacity map records multi-hour publication gaps, so observed firing must be measured separately from the cron expression.

## 5. Priority investigation order

| Priority | Surface | Investigation | Exit evidence |
|---|---|---|---|
| HOLD | Codespaces | Preserve the 2026-10-27 owner exclusion; prepare a billing-usage read and per-codespace inventory for the reopening decision | explicit owner reopening + timestamped billing reading + safe monthly budget |
| P0 | Cloudflare Workers/D1 | Capture Billing Read usage; verify Worker routes/deployments and D1 metrics; record the empty Queues and R2 activation gaps | account-scoped usage evidence, deployment receipts, D1 usage, and decision on Queues/R2 |
| P1 | Leapcell | Validate Hobby invocation, GB-hour, ingress/egress, and timeout behavior with a synthetic workload | test receipt and usage delta |
| P1 | Appwrite | Validate function runtime limits, inactivity pause behavior, and scheduled-work recovery | function test receipt, pause/reactivation test, and recovery checklist |
| P1 | SnapDeploy | Test cold-start behavior and automated caller response; measure shared container-hour draw | synthetic request traces, wake classification, and hour consumption |
| P2 | Back4app | Resolve temporary URL lifetime discrepancy in the current account and verify deployment persistence | dashboard-observed URL lifetime and teardown receipt |
| P2 | zrok | Validate environment lifecycle, daily transfer reporting, and access controls for one synthetic private resource | access-policy test, transfer reading, and revocation receipt |
| P2 | alwaysdata | Confirm free-plan eligibility and website-only restrictions for intended personal/static use | explicit use-case fit decision; keep out of worker pool |

## 6. Mesh placement rules

- Use Codespaces for interactive and heavy-build workloads with idle-stop and monthly core-hour budgets.
- Use Workers for short, stateless request handling and dispatch; use D1 for small durable control records with explicit write budgets.
- Use Cloudflare Queues when message delivery/buffering is required; record the 10K daily operation budget and 24-hour retention.
- Use R2 for artifact/object storage only after account activation and owner approval; include storage and operation budgets.
- Use Leapcell/Appwrite for bounded serverless functions after measured workload fit and quota receipts.
- Use SnapDeploy/Back4app for previews and experiments whose cold-start/URL lifetime matches the use case.
- Use zrok for secure network sharing with separate compute; treat network access as a security-sensitive capability.
- Keep alwaysdata's free plan outside the general worker pool.
- Preserve GitHub as canonical source/control plane and keep provider adapters replaceable.

## 7. Quota ledger boundary

The active quota registry remains the ledger for services currently adopted by the repository. Candidate-only entitlements stay in this RFP evidence matrix until an account is approved and a service is adopted. At adoption, add the exact account scope, published entitlement, reset contract, live usage reader, and allocation rule. The existing registry already tracks Codespaces, Cloudflare, and Render; Codespaces remains owner-held, while Cloudflare and Render require account-side usage evidence.

## 8. Bounded Loopy-derived investigation receipt

The repository's Continuous Improvement Policy adapts Loopy into the native WAIT loop. This investigation follows the bounded six-step cycle:

| Step | Action | Receipt |
|---|---|---|
| Observe | Re-read current master, existing RFP, deployment records, and connected Cloudflare inventory | current SHA + timestamped source/API observations |
| Choose | Separate six new options from existing account-backed surfaces | candidate class and priority |
| Act | Update the RFP, evidence matrix, and deployment-lane status | focused documentation diff |
| Verify | Recheck official source claims, repo paths, account inventory, and Markdown structure | deterministic checks and source links |
| Record | Preserve known, conditional, disputed, and unknown states | this dossier + PR evidence |
| Repeat | Re-enter only when fresh account readings or owner-approved experiments produce a measurable delta | WAIT / approval-required terminal |

**Current cycle terminal:** `approval-required` for Render workspace selection and Cloudflare Billing Read; `research-recorded` for the six public provider candidates. Provider provisioning and paid resource creation remain outside this cycle.
