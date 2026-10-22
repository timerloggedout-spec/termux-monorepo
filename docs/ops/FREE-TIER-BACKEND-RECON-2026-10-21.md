# Free-Tier Backend Recon — Extended Provider Map for the Mesh

**Compiled:** 2026-10-21 ~22:00 PDT (backend/mesh-resiliency specialist, pass 2)
**Mode:** RECON ONLY — written as a staged `~/workspace/` doc and published to
`docs/ops/` on 2026-10-22; the recon itself created no accounts, made no repo
changes, and signed up for nothing. Extends: `ops/quota/registry.json` (28 records on master),
`docs/ops/FREE-QUOTA-WINDOWS.md`, `docs/AGENTIC-CICD-FREE-TIER.md`,
`~/workspace/termux-monorepo/quota-panel/QUOTA-EXPANSION-GAPS.md` (2026-10-20),
PR #1490 mesh matrix §7–§9, and the staged resiliency proposal in this folder.
**Rules (inherited, non-negotiable):** documented entitlements are NOT balances —
never invent a remaining value; revalidate on the vendor page before any spend
or signup; credential names only; free tiers are a *cadence/capacity* surface,
never a reason to clear or mute a participant.

**Vintage warning:** free tiers now change several times a year (see §5,
mortality). Every figure below carries its check date — 2026-10-21, from vendor
pages where reachable, otherwise the dated secondary source named in §7. A
figure older than ~90 days in this file should be treated as a lead, not a fact.

---

## 0. The one-paragraph answer

The fleet already implements more of this list than the list implies: Vercel,
Render, Cloudflare, GitHub (Actions + Codespaces + Pages), Fly, Koyeb, Neon,
Supabase, Turso, Upstash and Grafana all have registry records, workflows, or
apps in the mesh today. The genuinely *unclaimed* always-free capacity is
concentrated in three places: **GitHub Codespaces' 120 core-hours/mo** (fleet
has 3 codespaces but no registry record and no standing use as the heavy-build
lane), **Cloudflare Workers/D1/Queues/R2** (fleet has the quota family and a
blocked *Tunnel* lane, but not the Workers-as-rendezvous lane), and the
hyperscalers the fleet has **no account presence on at all** — **GCP**
(Cloud Run: 2M free requests/mo, always-free), **AWS** (Lambda: 1M req +
400k GB-s/mo, always-free), **Azure** (Functions: 1M executions/mo,
always-free), and **Oracle** (the largest free VM, halved in June 2026 but
still unmatched). **DigitalOcean does not have a permanent free tier** — only
a $200/60-day trial and 3 free static sites; same correction for Railway
(free tier died 2023) and Fly.io for new accounts (allowances ended Oct 2024).

## 1. Already implemented in the fleet (existing research + code)

| Provider | Fleet surface today | Registry record | State |
|---|---|---|---|
| Vercel | Deploys (primary), Muse connector, Jules-adjacent; `vercel-batch-deploy.yml` adaptive budget + learned offset, 6h cooldown | `vercel.deployments` 100/day rolling 24h (API undercounts enforcement ≥13); `vercel.build_time` 45 min | **Live, cap-bound** — tripped 2026-10-20. Hobby = personal/non-commercial terms; 1M function invocations + 100 GB transfer in the Hobby entitlement set (vendor pricing page; registry records only deployments + build time — gap) |
| Render | App installed; Jules MCP connected; previews | 500 pipeline min/mo; 750 instance hrs/mo; 5 GB bandwidth/mo (cut from 100 GB in Apr 2026 per §7 survey); free Postgres 1 GB/30 days then expires; Key Value 1 instance, in-memory only | **Live** — free web services sleep after 15 min idle (~1 min wake) |
| Cloudflare | Quota family in `provider-managers.json`; `cloudflared` logs on device; registry record exists but content-free | `cloudflare.d1_queues` — limit `null`, "mixed/daily", **no live reading** | **Partial** — Tunnel lane blocked on cfapi.net consent (device-side); Workers/Pages/D1/R2 lane never built (see §2) |
| GitHub Actions | Execution substrate, 167 workflow files on master tree (census: 192) | Minutes free for public repos; cache 10 GB; API 1,000/hr/repo (`GITHUB_TOKEN`) vs 5,000/hr (user token) | **Live** |
| GitHub Codespaces | **3 codespaces exist**; 7 Codespaces secret names (HindSight ×5, OpenRouter, vault age key); `codespace-create.yml` / `codespace-start.yml` workflows | **NO registry record for Codespaces compute/storage** — the single biggest registry gap this recon found | **Present, unmeasured** — mesh matrix C2 already names it the heavy-build lane to offload the B160V; nobody metered it |
| GitHub Pages | 38/300 sampled deployments; legacy `gh-pages` build | — (rides Actions) | **Live** — the deploy lane that keeps working when Vercel's cap trips |
| Fly.io | `FLY_IO_ORG_TOKEN` secret name; `deploy-hindsight.yml` (manual dispatch), fly-diag family | **No registry record** | **Live but unpriced in our books** — and see §5: Fly's free allowances ended Oct 2024 *for new accounts*; the fleet org's actual billing state is NOT ESTABLISHED |
| Koyeb | App authorized (dormant in mesh matrix §4); `koyeb-hindsight-deploy.yml` exists | **No registry record** | **Dormant** — free shape changed Feb 2024 ($5.50 credit → single free web service instance, sleeps after 1h idle) and a $29 verification hold was added Feb 2026 (§7 survey) — revalidate before any revival |
| Neon | Jules MCP connected (fleet memory: verified 2026-10-20, flagged contested); registry records | 100 CU-h/project/mo; 1 GB storage/project (20 GB total); 5 GB egress/mo | **Live-ish** — batch writes hourly (~15 CU-h/mo) vs per-event (~180) per registry note |
| Supabase | Registry record only; Jules lane open; Muse custom connector pending vault keys | `supabase.free` — limit `null`, "mixed", no live reading, **no numbers at all** | **Gap** — vendor free plan (widely documented: 500 MB Postgres, 1 GB storage, 5 GB egress, projects pause after ~1 week inactivity) is NOT in our registry; revalidate on vendor page before recording |
| Turso / Upstash / Grafana Cloud | Registry records | `turso.free`, `upstash.free` — limits `null` "mixed"; `grafana.cloud_free` 10,000 samples/s | **Recorded, un-detailed** — same treatment as Supabase: numbers or an explicit "unpublished" note, not blanks |
| Replit | Muse connector connected; apps lane | No registry record | **Live (Muse side)** — free plan exists; not a backend the mesh depends on |
| GitLab | Mirror webhook (repo redundancy lane) | — | **Degraded** — last response 400; repair is mesh item I2 and §4 of the resiliency proposal |

## 2. The unclaimed always-free core (extension — new recon)

### 2.1 Serverless compute — the "Lambda" row, done properly

"Lambda" is one product in a class. Every major vendor's function tier is
always-free at roughly the same scale, and all of them fit the same mesh jobs
(queue receiver, webhook sink, receipt writer, canary brain):

| Product | Always-free entitlement (checked 2026-10-21) | Card to open account | Fleet presence |
|---|---|---|---|
| **AWS Lambda** | 1M requests/mo + 400,000 GB-s/mo, never expires, all account types. Traps: no free tier with Provisioned Concurrency; VPC/NAT ≈ $32/mo; CloudWatch Logs share a 5 GB/mo free quota | Yes | **None** (the `DEEPSEEK_AWS_WAF_TOKEN` name in repo secrets is a DeepSeek-lane WAF token, not a fleet AWS account) |
| **Azure Functions** (Consumption) | 1M executions/mo + 400,000 GB-s/mo, always-free (55+ always-free services on the free account) | Yes (+ phone) | **None** |
| **GCP Cloud Run functions** | 2M invocations/mo + 400,000 GB-s + 200,000 GHz-s + 5 GB egress/mo — the largest function grant | Yes (billing account required even for free tier) | **None as GCP** — the fleet's Google presence is Gemini/Workspace/Jules, not a GCP project |
| **GCP Cloud Run** (containers) | 2M requests/mo + 180,000 vCPU-s + 360,000 GiB-s + 1 GB NA egress/mo; scales to zero, request-based billing = $0 at idle | Yes | None |
| **Cloudflare Workers** | 100k requests/**day** (~3M/mo — the largest request grant in this table) + 10 ms CPU/invocation; static assets free & unmetered | **No** | Quota family only — **the cheapest lane to claim: no card, fleet-adjacent already** |
| **Deno Deploy** | 1M requests/mo, 20 GiB egress, 10 CPU-hours, 5 custom domains | No | None |
| **Vercel Functions** | Inside Hobby (1M invocations in the entitlement set) | No | **Live** (rides Vercel) |

### 2.2 Always-free VMs / workspaces — the off-device compute lane

| Offer | Entitlement | Catch | Fleet fit |
|---|---|---|---|
| **GitHub Codespaces** (personal) | **120 core-hours/mo + 15 GB-mo storage** (Free plan; Pro 180/20). 2-core = 60 h/mo. Orgs get **no** free quota. Beyond quota: $0.18/h (2-core), $0.07/GB-mo; no payment method on file = hard block at quota, not a bill | Hibernates ~30 min idle; per-repo devcontainer setup is ours to own | **Claim first.** Zero signup (account exists), 3 codespaces + secrets already in place, directly serves mesh C2 (offload the 93%-full B160V) and resiliency P1/P2 (a claimant that isn't the phone) |
| **GCP Compute Engine** | 1× e2-micro/mo always-free (US regions) + 30 GB disk; $300/90-day trial for new billing accounts | Trial needs a card; e2-micro is small and throttled | A free always-on micro relay/queue-poller is possible here — but Cloud Run (scale-to-zero) fits the same jobs with less babysitting |
| **Oracle Cloud Always Free** | Ampere A1 ARM: **halved June 2026** — now 1,500 OCPU-hours + 9,000 GB-hours/mo (≈ 2 OCPU / 12 GB running 24/7, or 4 OCPU / 24 GB for ~half the month) + 200 GB storage + ~10 TB egress; plus 2× E2.1.Micro AMD | Card for identity; home region chosen at signup is **permanent**; "out of host capacity" is routine; idle instances (<20% util over ~7 days) can be reclaimed on pure free accounts | Still the only free *real VM* big enough to be a second executor / self-hosted runner / queue claimant. High value, high friction — an owner signup decision, not a chat action |
| **Azure VMs** | B1S 750 h/mo — but only in the **12-month** free-services window, not always-free | Converts to billed after month 12 unless deprovisioned | Trial-shaped, not infrastructure-shaped. Skip for standing lanes |
| **AWS EC2** | Post-2025-07-15 accounts: **no more 750h t2/t3.micro 12-month offer** — replaced by the credit plan (§2.3) | — | Do not plan around the old EC2 free year; it no longer exists for new accounts |
| **Gitpod** | ~50 h/mo small workspaces (free tier) | — | Codespaces covers this job with the account we already have |
| **AWS WorkSpaces** | No ongoing free tier (trial offers only) | — | Noted because the request named "WorkSpaces": if that meant Amazon WorkSpaces (virtual desktops), there is nothing standing to claim; if it meant Codespaces-style workspaces, the row above is the answer |

### 2.3 Hyperscaler account shapes (why "just sign up" is three different decisions)

| | New-account offer | Always-free core | Endgame if you do nothing |
|---|---|---|---|
| **AWS** (since 2025-07-15) | $100 credits + up to $100 more for onboarding actions = **$200, 6 months**. Choose **Free plan** (can never bill; restricted services) or **Paid plan** (credits first, then billed) | 30+ services incl. Lambda (§2.1), DynamoDB 25 GB + 25 RCU/WCU, SQS/SNS 1M, CloudWatch 10 metrics/10 alarms/5 GB logs, CloudFront 1 TB out + 10M req | **Free plan account auto-closes** at 6 months or credit exhaustion (data kept 90 days); Paid plan just starts billing |
| **Azure** | $200 credit, **30 days**; 12 months of popular services (B1S, Blob 5 GB, SQL); 55+ always-free | Functions 1M (§2.1), Cosmos DB 1,000 RU/s + 25 GB, 10 App Service apps, AKS, DevOps 5 users | Without upgrading to pay-as-you-go the account is **disabled** at day 30; with upgrade, 12-month items silently start billing in month 13 |
| **GCP** | $300 credit, **90 days** | Cloud Run + functions (§2.1), e2-micro, Firestore 1 GB, Pub/Sub 10 GB/mo, Cloud Build 120 min/day, BigQuery 1 TB queries/mo, GKE one cluster | Trial end without upgrade = resources paused; billing account required even to use always-free |
| **DigitalOcean** | $200 credit, **60 days** | **None for compute.** App Platform: 3 free static-site apps, 1 GiB transfer each; container registry + firewalls/VPC/monitoring free as features | Credit evaporates day 61; Droplets start $4–6/mo |

All four need a payment card for identity (Azure also a phone number). Account
creation for any of them is an **owner action** — no chat signs the user up for
a hyperscaler, and the fleet credential rule's posture (vault-only, names-only)
applies to whatever keys come out of it.

### 2.4 Data / edge freebies that complete the P1 rendezvous design

| Piece | Free entitlement | Mesh job |
|---|---|---|
| Cloudflare **D1** | 5 GB total (10 DBs, 500 MB each), 5M row reads/day, **100k row writes/day** — writes bite first; a queue that writes receipts per claim must budget ~10 row-writes per task event | Queue + receipts store for resiliency P1, without a git branch |
| Cloudflare **Queues** | Free monthly message-operation allowance (registry already carries a `cloudflare.d1_queues` stub) | The queue itself |
| Cloudflare **R2** | 10 GB-mo, 1M Class A + 10M Class B ops/mo, **zero egress** | Artifact/receipt blobs; GitHub-artifact-retention (90 days) alternative |
| Cloudflare **KV** | 1 GB, 100k reads/day, **1k writes/day** | Manifest mirror (`current.json` equivalent) readable without the GitHub API |
| Cloudflare **Pages** | Static free/unmetered requests; 3,000 build min/mo (survey figure) | Dashboard/docs mirror that survives a Vercel cap trip |
| **Turso** (libSQL) / **Upstash** (Redis/queue) | In registry with `null` limits — vendor numbers to be recorded or marked unpublished, same gap class as Supabase | Alternate queue/ledger stores |
| **Grafana Cloud** free | In registry (10,000 samples/s) + free logs/traces allotments | The watcher-of-watchers surface (resiliency P6) without another signup |

## 3. Ranking for the fleet's actual jobs (not generic "best free tier")

1. **Heavy builds / off-device compute (mesh C2, origin at 93%): Codespaces,
   now.** 120 core-hours/mo is already ours, unmeasured and unregistered.
   First move is bookkeeping, not building: add `github.codespaces.core_hours`
   (120 core-hours, monthly) + `github.codespaces.storage` (15 GB-mo) records
   to the registry set, and count the 3 existing codespaces in the census poll.
2. **P1 queue rendezvous: Cloudflare Workers + D1/Queues, no card, no signup
   friction, fleet-adjacent.** It removes GitHub-as-sole-rendezvous (SPOF-11)
   for the tasking path specifically, and the device only needs outbound HTTPS
   polling — no tunnel, no `cloudflared` (the consent-blocked product is
   *Tunnel*, a different lane; Workers needs nothing on the device). Fallback
   stays the git side-branch design already in the resiliency proposal.
3. **Second executor / self-hosted runner: Oracle A1, as an owner decision.**
   The only free VM that can actually hold a queue claimant + runner 24/7.
   Friction is real (card, permanent home region, capacity lottery, idle
   reclamation) — propose, don't presume.
4. **HindSight hosting redundancy:** Fly's free era is over for new orgs and
   Koyeb's free shape shrank + gained a card hold; the honest free alternates
   are Cloud Run (container, scale-to-zero, 2M req) or a Render free web
   service (sleeps 15 min — bad for a telemetry endpoint that must accept
   writes, fine for read-mostly). GCP account creation is the gate for Cloud Run.
5. **Static/docs survival:** Cloudflare Pages or GitHub Pages as the mirror
   that keeps the dashboard/quota panel reachable through a Vercel cap trip
   (Pages already proved this role on 2026-10-20).
6. **Deliberately NOT now:** AWS and Azure accounts. Their function tiers are
   excellent and always-free, but each is a new card-backed account for
   capacity that Workers/Cloud Run already cover for our job shapes. Revisit
   only if a job needs a hyperscaler-specific service (e.g. DynamoDB's
   25 GB always-free as a ledger, SES, Azure DevOps). DigitalOcean: trial
   credit only — useful for a 60-day experiment (e.g. benchmarking the Docker
   image cache lane from the parked research cards), never for a standing lane.

## 4. Registry additions this recon proposes (landed 2026-10-22 via PR #1504 — registry now 64 records)

Following the registry's own format (documented entitlement, source URL,
live-reading method or `none`), in priority order:

1. `github.codespaces.core_hours` — 120 core-hours/mo (Free personal); live: GitHub billing API. `github.codespaces.storage` — 15 GB-mo.
2. `cloudflare.workers_requests` — 100,000/day; `cloudflare.d1` — 5 GB / 5M reads / 100k writes per day; `cloudflare.r2_storage` — 10 GB-mo, egress free; `cloudflare.pages_builds` — revalidate figure on vendor page first.
3. Split `supabase.free`, `turso.free`, `upstash.free`, `cloudflare.d1_queues` from `null/"mixed"` stubs into per-metric records with vendor numbers or an explicit `unpublished` note (the QUOTA-EXPANSION-GAPS standard).
4. `fly.*` — first ESTABLISH the fleet org's billing state; record "no free allowance for new orgs (Oct 2024)" as the entitlement fact either way.
5. `koyeb.free_instance` — single free web service, 1h idle sleep; revalidate + note the Feb 2026 card hold before recording.
6. New-provider stubs marked `no_account` (entitlement documented, fleet presence none): `gcp.cloud_run_requests` 2M/mo, `gcp.cloud_functions_invocations` 2M/mo, `aws.lambda_requests` 1M/mo + `aws.lambda_compute` 400k GB-s/mo, `azure.functions_executions` 1M/mo, `oracle.ampere_ocpu_hours` 1,500/mo + `oracle.ampere_gb_hours` 9,000/mo, `digitalocean.trial_credit` ($200/60d, one-time) + `digitalocean.app_platform_static` (3 apps). A `no_account` stub is how the registry says "known, unclaimed" without inventing a balance.

## 5. Free-tier mortality — the standing caution (why §3 ranks redundancy first)

Verified deaths/shrinkages, each against the provider's own announcement or a
dated survey (§7): Heroku free dynos/Postgres/Redis (Nov 2022) · Railway
recurring free tier → $5 one-time trial (Aug 2023) · PlanetScale Hobby killed
(Mar–Apr 2024) · Koyeb $5.50 credit → one free instance (Feb 2024), card hold
added (Feb 2026) · Fly.io free allowances removed for new accounts (Oct 2024) ·
Glitch hosting shut down (Jul 2025) · Netlify legacy free → 300 credits/mo
(Sep 2025) · AWS 12-month EC2 free year replaced by 6-month credit plan
(Jul 2025) · Render free bandwidth 100 GB → 5 GB (Apr 2026) · Oracle Always
Free Arm halved (Jun 2026).

**Rule that follows (extends resiliency P5/P6):** no critical lane is ever
single-homed on a free tier, however generous. Free capacity is spent in
parallel, per-provider, each thread reconciling its own cap before its own
dispatch — the owner's standing provider-neutral rule — and every free-tier
dependency carries a named exit (the same workload on the next provider in §3)
recorded *before* it becomes load-bearing.

## 6. Relationship to the staged resiliency proposal

- P1 (pull queue) gains a concrete no-card implementation option: §2.4.
- P2 (what runs where) gains two claimant hosts that aren't the phone:
  Codespaces (ephemeral builds) and, if the owner chooses, Oracle A1 (standing).
- P3 (failover order) is unchanged for *reaching the device* — none of these
  providers fix a dead tunnel; they fix *not needing* one for scheduled work.
- P5 (hosted guardrails) gains §5's mortality rule and §4's bookkeeping.
- SPOF-11 (GitHub as sole rendezvous) is the register item this recon most
  directly de-risks.

## 7. Sources (checked 2026-10-21)

Vendor/first-party where the search surfaced them: Google Cloud Free Program
page + Free Tier docs table (Cloud Run / functions / e2-micro / Firestore /
Pub/Sub / Cloud Build figures); GitHub Codespaces billing docs (120 core-hours
+ 15 GB Free, 180/20 Pro, org = no free quota, rates past quota); DigitalOcean
App Platform pricing page (3 free static apps, 1 GiB each, no free web-service
tier); Azure free-account pages ($200/30 days, 12-month set, 55+ always-free,
Functions 1M executions + 400k GB-s via AZ-900/vendor material); Cloudflare
Workers pricing via vendor perspectives page (100k req/day, 10 ms CPU).
Dated surveys used for cross-checks and the mortality timeline: SnapDeploy
"State of Free Hosting 2026" (verified 26–28 Sep 2026, per-provider dates);
Flavio Copes hosting free-tier table (Oct 2026); CostGoat/ComputingForgeeks AWS
free-tier breakdowns (July 2025 plan change, always-free table); 301.sh
Cloudflare free-plan job mapping (29 Jul 2026 doc read); Oracle A1 guides +
the June 2026 halving report (1,500 OCPU-h / 9,000 GB-h). Where a survey and a
vendor page disagreed, the vendor figure is the one recorded above; survey-only
figures are marked "(survey)" in-line.

*End of recon. Signups, registry edits, and builds are separate, scoped orders —
this file only updates the fleet's knowledge.*
