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
- Project: **n0nplatform201-live** (Hello World (Vite) blueprint: Gateway → Vite
  container, Node.js 20, port 5173), Production environment.
- Deployment 1: completed, console status "(Deployed)", "Your deployment is live".
  Runs on Platform201-managed GCP (Cloud Run, europe-west2) — not fleet GCP.
- Live URL (opened and verified): 
  https://ringerhollow-kangaroorose-killerpuddle.eu1.platform201.live/
  — serves "Welcome to Platform201 / Your Vite Example is running."
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

Plan (B efficient):
1. **$20 = reserve, never budget.** Runway is unpriced — plan all spend at $0
   target; credits absorb surprises only.
2. **Scale-to-zero first:** functions (on-demand, scale to zero) > schedulers
   (no 24/7 server) > containers (always-on, last resort). DB: Neon integration
   (scales to zero) before MongoDB/VM nodes.
3. **Project slots (Solo cap 3):** P1 = n0nplatform201-live (prod). P2 = one
   real workload. P3 = held reserve/experiment — never fill casually.
   1 environment per project: no staging envs; test = redeploy.
4. **Node discipline:** current live use = 1 container (1 vCPU / 512 MB,
   instances 0–1) + 1 gateway of 3+3. Keep each project ≤3 nodes/type;
   smallest container size that serves.
5. **Tripwires:** Usage > $0.00, estimated monthly cost > $0.00, or credits
   < $20.00 → stop new deploys, inspect Usage breakdown, report.
   Check Billing + Usage on the 1st of each month and after every deploy burst.
6. **No paid refill:** do not buy Indie/Pro for credits — tiers grant node
   limits, not credits. Upgrade only when a node cap (3 projects / 10 nodes)
   is the proven blocker.
