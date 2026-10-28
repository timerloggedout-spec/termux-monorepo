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
