# Mesh-resiliency provider evidence matrix

**Tracking issue:** #1622  
**RFP:** [RFP.md](./RFP.md)  
**Status:** Seed list plus 2026-11-23 supplement; account eligibility and ranking remain pending.

This file is a research worksheet. The links identify official source entry points; current free capacity, account eligibility, price, and suitability require separate validation. Record an observation timestamp and exact terms before scoring any row.

| Candidate | Class | Official source | Terms/quota evidence | Account eligibility | Runtime/limits | Egress/storage | Overage/expiry | Evidence status | Next action |
|---|---|---|---|---|---|---|---|---|---|
| Oracle Cloud Always Free | VM/instance | https://www.oracle.com/cloud/free/ | unknown | unknown | unknown | unknown | unknown | unknown | verify current shape/region availability, account rules, limits, reclamation |
| Google Cloud | VM + managed runtimes | https://cloud.google.com/free | unknown | unknown | unknown | unknown | unknown | unknown | separate VM and Cloud Run terms; inspect billing/credit expiry |
| AWS | VM + managed runtimes | https://aws.amazon.com/free/ | unknown | unknown | unknown | unknown | unknown | unknown | verify current plan, account-specific terms, region and billing controls |
| Microsoft Azure | VM + managed runtimes | https://azure.microsoft.com/free/ | unknown | unknown | unknown | unknown | unknown | unknown | separate credits from recurring free quotas; verify post-credit behavior |
| Google Cloud Run | managed container | https://cloud.google.com/run/pricing | unknown | unknown | unknown | unknown | unknown | unknown | quantify request/CPU/memory quotas and cold-start/duration constraints |
| Azure Container Apps | managed container | https://azure.microsoft.com/pricing/details/container-apps/ | unknown | unknown | unknown | unknown | unknown | unknown | quantify free grants, scaling and billable components |
| Cloudflare Workers + D1 | edge/serverless + data | https://developers.cloudflare.com/workers/platform/limits/ | Workers Free: 100K requests/day, 10 ms CPU, 128 MB; D1: 5M rows read/day, 100K rows written/day, 5 GB account storage | 2 deployed Workers + 3 D1 databases; GraphQL Analytics confirms activity; 0 Queues; R2 activation pending; private usage counts retained in oversight | request/CPU-bound; D1 500 MB/database and 10 DB/account | R2 free allowance available after activation; current billing usage unknown | documented entitlements + live resources; billing read scope pending | capture Billing Read usage; decide Queues and R2 role |
| Deno Deploy | edge/serverless | https://deno.com/deploy/pricing | unknown | unknown | unknown | unknown | unknown | unknown | verify current plan, limits and runtime fit |
| Koyeb | managed app/container | https://www.koyeb.com/pricing | unknown | unknown | unknown | unknown | unknown | unknown | verify current free instance and region/runtime constraints |
| Render | image-backed web service | https://render.com/docs/deploying-an-image | free-service limits documented in https://render.com/docs/free | repo wiring: readme-extractor-image workflow → GHCR image → termux-readme-extractor service; live account state pending | image pull avoids Render build pipeline; 750 free instance hours/month per registry evidence | bandwidth and persistent-disk fit require service inspection | pipeline minutes estimated from deploy wall-clock; billing dashboard authoritative | repo-wired / provider health pending | confirm Render workspace; inspect service, events, URL, source digest, and usage |
| Fly.io | app/VM platform | https://fly.io/docs/about/pricing/ | unknown | unknown | unknown | unknown | unknown | unknown | verify current offer and establish the actual billable baseline |
| DigitalOcean App Platform | managed app | https://www.digitalocean.com/pricing/app-platform | unknown | unknown | unknown | unknown | unknown | unknown | verify static vs dynamic services and trial-credit conditions |
| GitHub Actions | hosted CI | https://docs.github.com/en/billing/managing-billing-for-your-products/about-billing-for-github-actions | public-repository standard hosted runner usage is free; job duration and concurrency limits apply | repository is public; account plan remains unknown | CI-shaped ephemeral jobs | artifacts/cache have separate quotas | larger runners and dependent APIs can incur charges | documented entitlement + live repo metadata | measure job duration, queue delay, and burst distribution |

| GitHub Codespaces | interactive development | https://docs.github.com/en/billing/concepts/product-billing/github-codespaces | GitHub Free personal accounts: 120 core-hours/month + 15 GB-month storage | owner order 2026-10-27 excludes BOINC compute use pending owner reopening; five role-specific devcontainer lanes exist; account usage unknown | per-machine core-hours; interactive workspace | storage billed in GB-month | organization billing differs from personal allowance | documented entitlement; owner HOLD; balance unknown | require explicit owner reopening and current billing actuals before utilization |
| SnapDeploy | managed container | https://snapdeploy.dev/docs/free-tier | up to 4 containers; 512 MB / 0.25 vCPU each; 100 shared container-hours/month; 10 deploys/day (5 per rolling 12h) | card requirement: none; account eligibility unknown | sleep after ~15 min idle; browser wake ~60 sec; scripts/cron/CI receive HTTP 503 and leave the container asleep | persistent disk: none | deploy cap includes failures | documented; workload fit conditional | run synthetic cold-start and caller tests |
| Leapcell Hobby | serverless + app runtime | https://www.leapcell.io/pricing | 20 projects/services; 100K invocations/month; 3 GB-hours/month; 2 GB egress; 10 GB ingress; 10K async invocations; 100K Redis commands; one free PostgreSQL database; 60 build minutes/month; 900 sec timeout | account eligibility and current balance unknown | serverless invocations; persistent servers listed on paid Plus | ingress/egress quotas apply separately | metered overage pricing published | documented; account state unknown | measure invocation, duration, and egress for a bounded task |
| Appwrite Free | backend platform + functions | https://appwrite.io/pricing | 750K executions/month; 100 GB-hours/month; 5 GB bandwidth; 2 GB storage; 75K MAU; 1 database + 1 bucket + 2 functions/project; 2 projects/organization; 0.5 CPU / 512 MB; 900 sec async timeout | account eligibility and current balance unknown | 15-minute builds; Free intervals start at 60 minutes; cron schedules require paid plan | resources shared across projects; projects pause after 7 inactive days and delete after 90 paused days | documented; recurring-job fit conditional | test function limits, hourly interval behavior, and pause/reactivation recovery |
| alwaysdata Free | shared hosting | https://www.alwaysdata.com/en/offers/ | 1 GB SSD; 256 MB RAM; 1/4 CPU; 3 backup days | personal-use restriction; account eligibility unknown | website hosting; running services excluded from free-plan fit | 1 GB SSD | lifetime free offer; use restrictions apply | documented; worker-pool fit excluded | retain for personal/static website use only |
| Back4app Containers Free | Docker preview | https://www.back4app.com/pricing/container-as-a-service | 0.25 CPU; 256 MB RAM; 100 GB transfer; card requirement: none | account eligibility unknown | vendor engineering article reports 60-minute temporary URL per deployment; free auto-deploy disabled; separate backend app supplies persistence | transfer quota published; persistence requires verification | URL lifetime is a documented preview constraint | conditional | resolve current dashboard behavior before persistent endpoint use |
| zrok Free | network sharing | https://zrok.io/pricing/ | 5 GB/day; 25 environments; 50 share backends; 50 private access frontends | card requirement: none; account state unknown | network sharing/tunneling; compute capacity: none | daily transfer budget | daily quota; self-hosted edition available | documented; networking adjunct | test access policy, transfer reporting, and revocation |

## Required evidence schema

For each observation add:
- `observed_at_utc`
- `source_updated_at` (or null if absent)
- `provider`, `product`, `plan`, `region`
- `quota_name`, `quota_amount`, `quota_unit`, `reset_period`, `shared_scope`
- `eligibility_conditions`, `payment_method_required`
- `expiry`, `post_expiry_behavior`, `overage_behavior`
- `runtime_limits`, `storage_limits`, `egress_limits`, `duration_and_sleep`
- `evidence_class`: verified / conditional / estimate / unknown / expired
- `source_url`, `source_title`, `captured_facts`, `next_recheck_at`

Keep unverified fields as `unknown`. Scores and provider selection follow completed evidence collection and an approved rubric.
