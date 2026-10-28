# Platform201 — LIVE record (2026-10-27)

Platform201 (formerly **Shoal Stack**; domain shoalstack.com, public branding "Shoal")
is a visual graph cloud infrastructure platform: deploy backends, workers and web
apps in a live graph, into Google Cloud managed by Platform201.

## Live evidence (verified firsthand 2026-10-27)

- Account: signed in via **Google** at app.platform201.com (fleet rule: no GitHub
  sign-in route). No payment method entered; no card on file.
- Plan: **Solo — $0/mo, "Current"** in Billing. Credits observed: **$20.00 USD**;
  estimated monthly cost $0.00.
- Solo caps (Billing, console-observed): 3 projects; 1 environment per project;
  1 seat; 3 nodes each of container / function / gateway / scheduler /
  MongoDB-integration / Neon-DB-integration.
- Project: **n0nplatform201-live**, Production environment. Deployment 1
  (Hello World (Vite) blueprint) was the bring-up placeholder.
  **P1 payload swapped 2026-10-27 (owner correction — placeholder rejected):**
  container renamed `fleet-dashboard`, source replaced with the fleet's real
  **help-wanted dashboard** (`apps/help-wanted-dashboard`: pages + 18 data
  feeds, Node static host, port 8080, Node 22). Deployment 2 failed (buildpack
  rejected bare runtime "20"); Deployment 3 "(Deployed)", 3:10.
  Runs on Platform201-managed GCP (Cloud Run, europe-west2) — not fleet GCP.
- Live URL (opened and verified):
  https://ringerhollow-kangaroorose-killerpuddle.eu1.platform201.live/
  — serves "Help-Wanted · with Tribute · Control Surface"; `/quota.html`,
  `/data/referral-feed.json` and `/health` (`{"ok":true,...}`) verified.
- A starter project "My Project" pre-existed in the space (Gateway + Welcome App,
  not deployed by this lane).

## Registry wiring in this PR

- `ops/quota/registry.json`: new record `platform201.projects` (Solo, limit 3).
- `ops/delphi/surfaces.json`: `platform201.solo` → sourced=true, registry_id
  `platform201.projects`, horizon H0, auth note updated (live web account,
  console-only; still **no API token and no Actions credential** — that remains
  the integration gap vs Vercel/Render-class surfaces).

## History

Before this record the surface was REGISTERED-ONLY: a Delphi catalog entry
(sourced=false, limit null) plus the "Platform201 Planning Queue" name cited as
the source of five 2026-10-19 quota stubs. PR #1274 (planning-queue backend,
draft reference) remains open and is **not** part of this live deployment.
Platform201 is **not** n8n; n8n is a separate in-repo wiring
(`ops/n8n/`, docs/ops/N8N-FREE-COMMUNITY-WIRING.md).

## Credits plan — maximum benefit (2026-10-27, console-verified)

Facts (Billing + Usage pages, inspected in-console 2026-10-27):
- Credit balance **$20.00, unmoved** by the live deployment. Usage: **$0.00**
  recorded (daily + cumulative, last 30 days); estimated monthly cost **$0.00**.
- **No** credit expiry, refill/renewal terms, consumption rates, rollover, or
  top-up option is published anywhere in-console. No per-container hourly rate.
- **Referral/affiliate: NONE** — no programme, link, code, reward or cap in
  Billing/Usage/Settings/Members/Projects or on the public web. "Invites" =
  inbound space invites only; "Invite member" carries no reward. The only
  credit-intake surface is **Redeem coupon** (account menu) — code source
  not established; treat any future promo code as the sole refill path.
- Plans state node/seat limits only, no credit inclusions: Solo $0 (current);
  Indie $8/mo ($80/yr); Pro $20/mo per seat ($200/yr per seat); Enterprise custom.

Plan (REVISED 2026-10-27, owner correction — **$0 target REJECTED; the $20
exists to be USED**; supersedes the reserve plan in PR #1987):
- Metering reality: after 3 deployments and an always-on container, Usage is
  still $0.00 and the balance unmoved — Solo usage is not visibly metered
  against credits in-console. "Spend" therefore = **extract maximum hosted
  value inside the $20 envelope**: fill the node/project caps with real,
  always-on fleet workloads; if priced metering appears, allocations below
  govern priority and a re-plan lands within a week.
1. **Allocations (of $20):** $12 prod always-on (P1 + P2) · $5 experiment
   bursts (P3) · $3 floor buffer (overage surprise only — the sole hoard).
2. **Workloads, named:** P1 = **fleet help-wanted dashboard** (LIVE, above —
   second host for the fleet control surface). P2 = **planning-queue**
   backend (PR #1274 graph: intake + collector + sweeper containers, Neon
   `ops_queue`, queue node, `*/5` scheduler) — next deploy, fills P2's caps.
   P3 = rotating challenge/demo slot (entry demos, temporary backends);
   recycle on completion, never idle-hold.
3. **Utilization targets:** projects 3/3 with real payloads; every project
   always-on or scheduler-driven; zero placeholder payloads (Vite lesson).
   Efficiency = benefit per node, not idleness: scale-to-zero node types
   (functions, Neon) go where traffic is bursty *inside* a real workload.
4. **Tripwires:** credits < $3 floor → P3 experiments stop, prod runs on.
   Usage > $0.00 (priced metering starts) → report + re-plan allocations
   against real rates. Check Billing + Usage 1st monthly + after deploy bursts.
5. **No paid refill:** tiers grant node limits, not credits. Upgrade only
   when a node cap is the proven blocker for a named workload.
