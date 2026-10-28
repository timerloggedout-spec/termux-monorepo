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

Plan (REVISED rev3, 2026-10-27, owner refinement — **CONSERVATIVE use,
MAXIMUM benefit**; supersedes rev2's spend allocations and PR #1987's
reserve plan; the rev2 rejection of a $0 target stands — credits are used,
but only where benefit is real and stated per credit):
- Metering reality: after 3 deployments and an always-on container, Usage is
  still $0.00 and the balance unmoved — Solo usage is not visibly metered
  against credits in-console. Measured credits consumed to date: **$0.00**.
  Every workload below states its benefit; while metering is $0 the
  benefit-per-credit is unbounded, and the conservative gate is what keeps
  that honest if priced metering starts: no benefit statement, no deploy.

Benefit per credit, per workload:
| Slot | Workload | Benefit (real, named) | Envelope |
| --- | --- | --- | --- |
| P1 | Fleet help-wanted dashboard (LIVE) | Independent second host for the fleet control surface + 18 data feeds; removes GitHub-Pages single-homing (fleet free-tier rule: no critical lane single-homed); saves Vercel deployment quota (100/day, cap already hit 2026-10-18/19) and Render free hours for workloads that need them | up to $12, always-on justified by daily fleet use |
| P2 | planning-queue backend (PR #1274) | `ops_queue` intake/claim/done backend that lanes, Actions and devices enqueue through (hark-bridge mirror target) — **deploy gated on a wired consumer**: no consumer, no deploy (an idle queue is waste) | within the $12 prod envelope, only after the gate |
| P3 | Experiments | **No standing allocation.** Each experiment pre-states benefit + kill date before deploy; deleted at kill date regardless of outcome | up to $2 per experiment, benefit-gated |
| — | Floor buffer | Prod continuity against priced-metering surprises | $3, untouched unless prod is at risk |
| — | Unallocated remainder | Default state is unspent — not hoarding: it converts the moment a benefit is named and gated | $3 |

Rules:
1. **Nothing wasteful:** no placeholder payloads (Vite lesson — the P1 swap
   itself is held to this: its benefit is the row above, re-checked monthly;
   if the dashboard host goes unused, it comes down), no idle always-on
   nodes, no filling caps for utilization's sake.
2. **Smallest sufficient shape first** (P1 runs 1 vCPU / 512 MB, instances
   0–1); scale-to-zero node types (functions, Neon) where traffic is bursty
   inside a real workload.
3. **Tripwires:** credits < $3 floor → experiments stop, prod runs on.
   Usage > $0.00 (priced metering starts) → report + re-plan within a week,
   benefit-per-credit recomputed from real rates. Check Billing + Usage
   1st monthly + after deploy bursts; the monthly check also re-validates
   each live workload's benefit row.
4. **No paid refill:** tiers grant node limits, not credits. Upgrade only
   when a node cap is the proven blocker for a named, benefited workload.


## Credits ledger semantics (amendment 2026-10-28, PR #1992 debate)

- The $20 is Platform201 platform CREDITS, not cash. Cash exposure = $0
  (no card on file). Cumulative and monthly credit consumption are tracked
  as separate ledgers.
- Unsubsidized usage (cost at published rates) = NOT ESTABLISHED: rates are
  unpublished and Usage reads $0.00. That ledger starts when rates publish
  or Usage exceeds $0.00.
- Credit thresholds (cumulative consumed): $1 reconcile · $3 review ·
  $5 pause expansion · $8 stop optional experiments · $10 stop discretionary
  spend. Rev3 envelopes remain the caps.
