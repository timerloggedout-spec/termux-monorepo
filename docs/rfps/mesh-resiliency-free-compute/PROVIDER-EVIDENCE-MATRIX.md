# Mesh-resiliency provider evidence matrix

**Tracking issue:** #1622  
**RFP:** [RFP.md](./RFP.md)  
**Status:** Initial official-source observations recorded; account-specific eligibility and end-to-end suitability remain unverified.  
**Observation batch:** 2026-10-24 UTC  
**Rule:** These observations describe public documentation, not this account's entitlements or guaranteed capacity. Do not treat an unknown field as zero, unlimited, or free.

## Candidate matrix

| Candidate / product | Class | Public quota / terms observed | Eligibility / availability | Runtime / limits | Egress / storage | Billing / expiry behavior | Evidence status | Next action |
|---|---|---|---|---|---|---|---|---|
| Oracle Cloud Infrastructure Always Free compute | VM/instance | Official page states Always Free Ampere A1 allowance of 1,500 OCPU-hours and 9,000 GB-hours per month, equivalent to 2 OCPUs and 12 GB memory; also advertises a US$300 credit for 30 days. | Account-specific eligibility and capacity unknown; Oracle docs say Always Free instances must be created in the home region and capacity errors can occur. | A1 is Arm; exact workload fit, architecture compatibility and instance availability require validation. | Official page advertises up to 10 TB/month outbound transfer; verify applicable limits and included service details before use. | Trial credit is time-limited; Always Free allowance is separate. Actual account status and billing guardrails unknown. | Public quota facts verified; account eligibility conditional; capacity unknown. | Capture current official terms, verify account eligibility only when deployment-ready, and model region/capacity failure. |
| Google Cloud Compute Engine Free Tier | VM/instance | One non-preemptible e2-micro instance-month in eligible US regions (us-west1, us-central1, us-east1), 30 GB-month standard persistent disk, and 1 GB outbound transfer/month. Eligible usage across supported regions is combined up to the hours in the month. | Billing-account eligibility, signup/trial state and current account-specific entitlements unknown. | e2-micro only; no GPU/TPU included. Region restriction applies. | 30 GB-month standard persistent disk; 1 GB outbound transfer/month as documented. | Public Free Tier is usage-limited; excess usage can be billable. Billing setup and budget/stop behavior must be verified for the target account. | Public quota facts verified; account eligibility conditional. | Record current billing and budget controls; compare only against low-memory, low-egress workloads. |
| Cloudflare Workers Free | Edge/serverless | Docs last updated 2026-10-12 state 100,000 requests/day, 10 ms CPU per HTTP request, 128 MB memory, and 50 subrequests/request. | Account-level entitlement and product fit not checked. | Edge JavaScript/Wasm execution surface; not a general-purpose VM. CPU-heavy or long-running batch jobs are not assumed suitable. | Product-specific storage/egress and any binding quotas need separate evidence. | At the daily request limit, requests fail with Error 1027 per docs; do not assume automatic paid overflow. | Public limits verified; account eligibility conditional; workload fit conditional. | Test only bounded control/API workloads; separately verify storage/binding limits and failure-mode behavior. |
| GitHub Actions hosted runners | Hosted CI | GitHub's plan allowance table lists 2,000 minutes/month and 500 MB Actions storage for GitHub Free (also 2,000 minutes / 500 MB for Free for organizations); plan-specific amounts differ. | Repository visibility, owner plan, runner type and actual billing configuration must be checked before projecting a quota. | Bounded CI jobs; runner image and job execution limits apply. Not an always-on production VM. | Actions artifact/cache storage allowance is plan-dependent; inspect retention and current usage. | Docs state standard hosted runners in public repos and self-hosted runners are free; private-repo usage above included allowances can be billed unless a stop-usage budget is configured. | Public plan terms verified; repo/account-specific allowance unknown. | Inspect repo visibility and account plan; capture actual usage and confirm stop-usage budget setting before any quota projection. |
| AWS Free Tier / compute | VM + managed runtimes | unknown — current account/plan-specific limits not yet captured in this evidence batch. | unknown | unknown | unknown | unknown | unknown | Verify current Free Tier plan, product-specific limits, region, expiry, billing alarms/budgets and stop controls from official docs. |
| Microsoft Azure free account / compute | VM + managed runtimes | unknown | unknown | unknown | unknown | unknown | unknown | Separate promotional credit from recurring free quotas; verify post-credit behavior and budget controls. |
| Google Cloud Run | Managed container | unknown in this batch; do not reuse Compute Engine VM allowances as Cloud Run quotas. | unknown | unknown | unknown | unknown | unknown | Capture Cloud Run's own current pricing, request/CPU/memory allowances, duration and egress terms. |
| Azure Container Apps | Managed container | unknown | unknown | unknown | unknown | unknown | unknown | Verify free grants, scaling and billable components. |
| Deno Deploy | Edge/serverless | unknown | unknown | unknown | unknown | unknown | unknown | Verify current plan, limits, runtime fit and overage behavior. |
| Koyeb | Managed app/container | unknown | unknown | unknown | unknown | unknown | unknown | Verify free instance availability, regions, sleep and runtime constraints. |
| Render | Managed app/container | unknown | unknown | unknown | unknown | unknown | unknown | Verify sleep, persistence, free-service and overage rules. |
| Fly.io | App/VM platform | unknown | unknown | unknown | unknown | unknown | unknown | Do not assume a permanent free tier; establish current billable baseline. |
| DigitalOcean App Platform | Managed app | unknown | unknown | unknown | unknown | unknown | unknown | Verify static vs dynamic services and trial-credit conditions. |

## Timestamped official-source evidence ledger

Observation timestamp for this batch: **2026-10-24** (UTC date; exact retrieval time not captured by the search interface). Source update/publication dates are recorded only when stated by the source. Re-check volatile limits immediately before an approved experiment.

| Evidence ID | Provider / product | Source | Captured public facts | Source date | Evidence classification / caveat |
|---|---|---|---|---|---|
| MESH-EV-001 | Oracle Cloud Free Tier | [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) | US$300 trial credit for 30 days; Always Free A1 allowance 1,500 OCPU-hours and 9,000 GB-hours/month; up to 10 TB/month outbound transfer shown on the page. | Page date not stated in retrieved result. | Verified public-page facts; does not prove account eligibility or regional capacity. |
| MESH-EV-002 | Oracle Cloud compute | [Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) | A1 monthly allowance is equivalent to 2 OCPUs and 12 GB memory; compute must be created in the home region; out-of-host-capacity errors may occur. | Page date not stated in retrieved result. | Verified public documentation; capacity is explicitly not guaranteed. |
| MESH-EV-003 | Google Cloud Compute Engine | [Google Cloud Free Tier features](https://docs.cloud.google.com/free/docs/free-cloud-features) | One non-preemptible e2-micro instance-month in three named US regions; 30 GB-month standard persistent disk; 1 GB outbound transfer/month; usage is combined across supported regions. | Page date not stated in retrieved result. | Verified public quota facts; billing-account and account-specific eligibility remain unknown. |
| MESH-EV-004 | Cloudflare Workers | [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) | Free plan: 100,000 requests/day, 10 ms CPU per HTTP request, 128 MB memory, 50 subrequests/request; daily request-limit breach returns Error 1027. | Last updated 2026-10-12. | Verified public plan limits at observation time; not a VM substitute and not account-specific verification. |
| MESH-EV-005 | GitHub Actions | [Product usage included with each plan](https://docs.github.com/en/billing/reference/product-usage-included) | GitHub Free: 2,000 Actions minutes/month and 500 MB storage; Free for organizations has the same stated allowance; other plans differ. | Page date not stated in retrieved result. | Verified public plan table; repository owner plan and actual usage still need checking. |
| MESH-EV-006 | GitHub Actions billing behavior | [Billing and usage](https://docs.github.com/en/actions/concepts/billing-and-usage) | Standard hosted runners in public repositories and self-hosted runners are free; private-repository hosted-runner usage can incur charges above included allowance. | Page date not stated in retrieved result. | Verified public policy summary; confirm repository visibility and budget stop-usage settings. |

## Required evidence schema for future observations

Each additional observation must preserve:
- `observed_at_utc` (exact timestamp where available; do not fabricate seconds)
- `source_updated_at` (or null if absent)
- `provider`, `product`, `plan`, `region`
- `quota_name`, `quota_amount`, `quota_unit`, `reset_period`, `shared_scope`
- `eligibility_conditions`, `payment_method_required`
- `expiry`, `post_expiry_behavior`, `overage_behavior`
- `runtime_limits`, `storage_limits`, `egress_limits`, `duration_and_sleep`
- `evidence_class`: verified / conditional / estimate / unknown / expired
- `source_url`, `source_title`, `captured_facts`, `next_recheck_at`

Keep unverified fields as `unknown`. No scores or provider winner should be emitted from this evidence batch alone.
