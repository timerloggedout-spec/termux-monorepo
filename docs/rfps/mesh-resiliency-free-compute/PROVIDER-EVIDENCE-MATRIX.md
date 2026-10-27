# Mesh-resiliency provider evidence matrix

**Tracking issue:** #1622  
**RFP:** [RFP.md](./RFP.md)  
**Status:** Seed list only; no candidate has been verified or ranked.

This file is a research worksheet. The links below identify official source entry points; they do not certify current free capacity, eligibility, price, or suitability. Record an observation timestamp and exact terms before scoring any row.

| Candidate | Class | Official source | Terms/quota evidence | Account eligibility | Runtime/limits | Egress/storage | Overage/expiry | Evidence status | Next action |
|---|---|---|---|---|---|---|---|---|---|
| Oracle Cloud Always Free | VM/instance | https://www.oracle.com/cloud/free/ | unknown | unknown | unknown | unknown | unknown | unknown | verify current shape/region availability, account rules, limits, reclamation |
| Google Cloud | VM + managed runtimes | https://cloud.google.com/free | unknown | unknown | unknown | unknown | unknown | unknown | separate VM and Cloud Run terms; inspect billing/credit expiry |
| AWS | VM + managed runtimes | https://aws.amazon.com/free/ | unknown | unknown | unknown | unknown | unknown | unknown | verify current plan, account-specific terms, region and billing controls |
| Microsoft Azure | VM + managed runtimes | https://azure.microsoft.com/free/ | unknown | unknown | unknown | unknown | unknown | unknown | separate credits from recurring free quotas; verify post-credit behavior |
| Google Cloud Run | managed container | https://cloud.google.com/run/pricing | unknown | unknown | unknown | unknown | unknown | unknown | quantify request/CPU/memory quotas and cold-start/duration constraints |
| Azure Container Apps | managed container | https://azure.microsoft.com/pricing/details/container-apps/ | unknown | unknown | unknown | unknown | unknown | unknown | quantify free grants, scaling and billable components |
| Cloudflare Workers | edge/serverless | https://developers.cloudflare.com/workers/platform/pricing/ | unknown | unknown | unknown | unknown | unknown | unknown | determine whether edge runtime fits workload; not a VM substitute |
| Deno Deploy | edge/serverless | https://deno.com/deploy/pricing | unknown | unknown | unknown | unknown | unknown | unknown | verify current plan, limits and runtime fit |
| Koyeb | managed app/container | https://www.koyeb.com/pricing | unknown | unknown | unknown | unknown | unknown | unknown | verify current free instance and region/runtime constraints |
| Render | managed app/container | https://render.com/pricing | unknown | unknown | unknown | unknown | unknown | unknown | verify sleep, persistence, free-service and overage rules |
| Fly.io | app/VM platform | https://fly.io/docs/about/pricing/ | unknown | unknown | unknown | unknown | unknown | unknown | do not assume a permanent free tier; establish actual billable baseline |
| DigitalOcean App Platform | managed app | https://www.digitalocean.com/pricing/app-platform | unknown | unknown | unknown | unknown | unknown | unknown | verify static vs dynamic services and trial-credit conditions |
| GitHub Actions | hosted CI | https://docs.github.com/en/billing/managing-billing-for-your-products/about-billing-for-github-actions | unknown | unknown | unknown | unknown | unknown | unknown | inspect repo/account plan and actual usage; compare only CI-shaped workloads |

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

Keep unverified fields as `unknown`. No scores or provider winner should be emitted from this seed worksheet alone.
