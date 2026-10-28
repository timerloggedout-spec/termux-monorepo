# Platform201 blueprint adaptation — PROPER PRIOR PLAN

Status: PLAN ONLY (owner order 2026-10-28: proper prior planning before execution).
No deployment, no payload change is authorized by this plan. The P2 consumer gate
and the credits rev3 rules still govern every later step.

## 0. Corrected facts this plan stands on

- The fleet help-wanted dashboard is the Tribute TELEMETRY / control surface,
  published through its own lanes (user-site Pages, Vercel) with a feed-refresh
  pipeline. It is NOT a portable hosting payload: a static snapshot copy on
  Platform201 is stale telemetry, not a second host. (Owner correction
  2026-10-28; the P1 swap is being reverted to the original webpages.)
- Platform201 IS Shoal: GitHub org `shoal-platform` carries display name
  "platform201"; its `blueprints` repo is "List of all blueprints platform201";
  blueprint pages previously served from shoalstack.com under the brand "Shoal"
  are the same pages now on platform201.com. Owner name form: Shoal Stack.
  "Shoal AI" names only unrelated entities — never this platform.

## 1. The template (from shoal-platform/blueprints, read firsthand)

- One top-level folder per blueprint (kebab-case), containing the code.
- Inside: one folder per service (container), each self-contained
  (package.json / server entry / Dockerfile as applicable). No graph manifest
  file — the graph is assembled in the console from these folders.
- A README table maps directory -> blueprint name -> short description.
- Reference shapes: `pastebin` (backend + frontend), `microservices`,
  `message-queue-demo` (order-service / order-collector / delivery-dashboard —
  the direct ancestor of our planning-queue).

## 2. Our schemas / assets to adapt (inventory before any work)

| Asset | Current form | Blueprint fit |
|---|---|---|
| planning-queue (PR #1274 branch, apps/planning-queue) | 4 service folders (intake-service, collector, sweeper, dashboard) + sql/001_ops_queue.sql; graph spec in its README (gateway paths, Pub/Sub topic/subscription, Neon schema, scheduler cron, env bindings) | Direct: same shape as message-queue-demo; needs template packaging only |
| quota registry / Delphi surfaces | JSON registries (ops/quota/registry.json, ops/delphi/surfaces.json) | Not payloads; they RECORD deployments. Blueprint work updates them after a verified live deploy, never before |
| help-wanted dashboard | Telemetry surface (see section 0) | EXCLUDED from blueprint adaptation |

## 3. Adaptation rules (schema -> template)

1. Service folder = container node; folder name = node name.
2. Gateway paths, queue topic/subscription, database schema, scheduler cron,
   and env bindings are declared in the blueprint README graph table —
   the same fields the console asks for, in the same order.
3. Secrets stay env-only names (INTAKE_TOKEN etc.), never values, never committed.
4. Each blueprint carries a benefit statement + kill criterion BEFORE any
   deploy (credits rev3: no benefit statement = no deploy).
5. Registration row added to a local blueprints index mirroring the upstream
   README table format (directory | blueprint | description | notes).

## 4. Sequence (each step gated by the previous one's verification)

1. Revert P1 to original webpages; verify live URL. [IN FLIGHT]
2. Package planning-queue into blueprint layout on a branch; diff against
   PR #1274 branch content — zero code drift allowed beyond layout + README.
3. Local validation: every service folder self-contained; graph table complete
   (gateway/queue/DB/scheduler/env all named); marker scan clean.
4. PR + review; land the TEMPLATE only. Deploy remains gated:
5. P2 deploy ONLY when a consumer is wired and named (rev3 gate stands).
6. After any verified deploy: update PLATFORM201-LIVE doc, quota registry,
   Delphi surface — in that order, from live evidence.

## 5. Explicit non-goals

- No dashboard/telemetry payloads on Platform201.
- No new projects beyond Solo caps without a named benefit.
- No credits spend assumption: metering is $0.00 observed; re-plan from real
  rates if Usage ever exceeds $0.00.

## 6. Amendment 2026-10-28 — debate vs Perplexity research (PR #1992 comment 6467129384)

Research evaluated firsthand by the eval lane + this lane. Verdicts:

### 6.1 ACCEPTED — pilot resequencing (supersedes section 2/4 candidate order)

- Pilot 1 = ONE bounded service: a read-only MCP service or a bounded Python
  API. 1 environment, 1 service. Pilot-1 selection requires its own benefit
  statement before packaging (rev3 gate).
- Planning-queue (4 services + gateway + Pub/Sub + Neon + scheduler) is
  DEFERRED to pilot 2: valid topology, too many independently failing or
  billable components for a first experiment. Its consumer gate also stands.

### 6.2 ACCEPTED — Phase-A verify gate (status firsthand, 2026-10-28)

| Item | Status |
|---|---|
| Shoal -> Platform201 identity | DONE (org shoal-platform, display name platform201) |
| Platform charges / trial restrictions | PARTIAL: Solo $0/mo, metering $0.00 observed; consumption rates UNPUBLISHED — open |
| GCP payment method required? | NO for Platform201-managed mode (live deploy, no card); bring-own-GCP NOT assessed |
| IAM / GitHub permissions requested | NONE observed: Google OAuth sign-in only; no GitHub permission, no repo connection, console-only |
| Resources per blueprint | Hello World observed: container + gateway (Cloud Run, europe-west2) |
| Environment deletion leaves-what | NOT ESTABLISHED — must verify before pilot-1 deploy |
| Export / rebuild without platform | Blueprint sources are public (shoal-platform/blueprints) — rebuild path exists for blueprint payloads; own packaged blueprint must keep the same property (repo is source of truth) |
| Platform-vs-GCP billing split | Platform201 credits/billing only observed; no owner-GCP billing exists in managed mode |

Pass condition (research, adopted): before any pilot deploy, we can state who
bills for every component and how to remove it. Deletion behavior is the one
blocking unknown.

### 6.3 RECONCILED — the $20 ledger (research cash model mapped, not adopted raw)

- The fleet $20 = Platform201 platform CREDITS on the account balance.
  It is NOT cash. Cash exposure = $0: no card is on file (verified at signup).
- Two ledgers, kept separately:
  1. Credits ledger (cumulative AND monthly, tracked independently):
     balance, consumed, thresholds below.
  2. Unsubsidized-usage ledger: what the same workload would cost at published
     rates. Currently NOT ESTABLISHED — rates are unpublished and Usage reads
     $0.00. This ledger starts the day rates publish or Usage exceeds $0.00;
     until then every benefit claim must say "at $0 observed metering".
- Credit thresholds (cumulative consumed) inside the rev3 envelopes:
  $1 reconcile resources vs intent · $3 review cost/task · $5 pause expansion ·
  $8 stop optional experiments · $10 stop discretionary spend, preserve rest.
  Rev3 envelopes unchanged as caps (prod <= $12, floor $3, experiments <= $2
  each with benefit + kill date). Thresholds govern pace; envelopes govern totals.

### 6.4 ACCEPTED — pilot runtime policy (declared in the blueprint README graph table)

environments 1 · services 1 · billing request-based · min instances 0 ·
max instances 1 · task timeout 60s · max attempts 2 · external model calls
per task <= 1 · writes disabled (pilot 1). The current live container already
runs min 0 / max 1 (observed). Region: managed mode placed the live project
in europe-west2 — platform-chosen; research's us-central1 is a deviation we
record, not a setting we control.

### 6.5 ACCEPTED — recovery + promotion gates

- Any task-bearing service carries an application-level task record:
  task_id, idempotency_key, status, attempt, max_attempts, lease_expires_at,
  checkpoint_ref, result_ref, estimated/recorded cost. The platform is never
  assumed to provide idempotency, leases, or checkpoints.
- Pre-promotion tests: duplicate submission · interrupt mid-task · redeploy
  with task pending · timeout · model provider unavailable · allowance
  exhaustion · restore from exported checkpoint.
- Phase-E: reconcile intended nodes vs actual resources, export config +
  evidence, tear down, inspect for residual billable resources, rebuild from
  repo instructions. Direct-Cloud-Run comparison on: cost per successful
  task, recovery behavior, time-to-deploy. No "production" claim before
  teardown + rebuild both pass.

### 6.6 REJECTED — with reasons

- Research file layout (deploy/platform201/, tests/deployment/,
  docs/experiments/): rejected on path only — repo convention stands
  (apps/platform201/blueprints/ + docs/ops/PLATFORM201-*). The file SET
  (resource-inventory, pilot-policy, recovery, teardown) is adopted and will
  live in the blueprint folder at packaging time.
- Phase-A "stop at the GCP signup gate" + $300-trial framing: not applicable
  to Platform201-managed mode — no owner GCP project or trial exists in this
  lane. Recorded as binding only on a future bring-own-GCP route.


## 7. OWNER $-RULE (2026-10-28) — spend freeze until intake is OBTAINED

Supersedes the rev3 use-posture on TIMING (envelopes, thresholds, gates
unchanged as caps/tripwires):

- Keep $ (credits) AS LOW AS POSSIBLE: NO new deploys and no spend beyond
  the $0-metered essential P1 already live, UNTIL an invite/referral-type
  benefit or other credit intake is FOUND and OBTAINED.
- "Found" is not enough — the freeze lifts only on obtained intake
  (redeemed coupon, granted credits, or an activated benefit recorded in
  the LIVE doc with date + evidence).
- No paid tier, no card, ever.

## 8. Benefit hunt (2026-10-28, widened pass — firsthand only)

| Channel | Result |
|---|---|
| Console (prior pass) | Referral/affiliate NONE; Invites = space invites only; sole intake = Redeem coupon, code source NOT ESTABLISHED |
| Docs, all 26 pages incl. MCP docs | referral/affiliate/coupon/promo/discount: ZERO hits |
| Pricing page (platform201.com/pricing) | FOUND: 14-day Pro trial, no card, auto-falls back to Solo. Plan-limits benefit, NOT credits. Claimable on our account: NOT ESTABLISHED. NOT OBTAINED |
| Web coupon/promo sources | NONE found for platform201/ShoalStack |
| Community / Discord | FOUND (2026-10-28, firsthand): Space Settings carries a "Join our Discord" link → https://discord.gg/ap2pDhrDph (space timerloggedout-space). Invite/credit benefits inside the server: NOT YET CHECKED — next hunt step (join + scan for coupon/referral/credit channels). |
| LinkedIn | No company page found: NOT ESTABLISHED |
| Product Hunt / launch offers | No listing found: NOT ESTABLISHED |
| Support inquiry | DRAFTED below; not sent |

### Support inquiry — DRAFT (send only on owner word; no-cost, no-commit)

> Subject: Credit intake options for existing Solo accounts?
> Hi — we run a small fleet-automation project on a Solo account (signed up
> with the $20 starting credits). Before we plan further usage: (1) Are
> there referral, invite, launch, or partner programmes that grant credits
> to existing accounts? (2) Where do Redeem-coupon codes come from — events,
> partners, community? (3) Is the 14-day Pro trial still claimable on an
> account that started directly on Solo? No purchase commitment implied;
> we're inventorying intake routes. Thanks.

## 9. Pilot 1 selection (2026-10-28, implementation start)

- **Selected: `catalog-api`** — a bounded, read-only Python API (stdlib
  only, Dockerfile-pinned) serving the fleet's Platform201 blueprint
  catalog as JSON. Packaged at `apps/platform201/blueprints/catalog-api/`
  (index: `apps/platform201/blueprints/README.md`); 5 local unit tests pass
  (health / catalog / single-entry / 404 / writes-disabled 405).
- Benefit statement + kill criterion: in the blueprint README (plan §3
  rule 4). Short form: end-to-end pipeline proof on a real artifact at $0
  observed metering + a machine-readable blueprint catalog for lanes;
  killed if unconsumed by Pilot 2 packaging or if it ever meters > $0.00.
- §6.5 task record: not applicable (not task-bearing); lands with Pilot 2.
- Status: PACKAGED ONLY. Deploy remains frozen under §7 until credit
  intake is obtained, and the §6.2 deletion-behavior unknown must be
  verified before that deploy.
