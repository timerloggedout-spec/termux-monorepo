# SnapDeploy — Surface Map (Web · API · MCP · Limits)

> Mapped 2026-11-04 by the enumeration lane on the owner's ask.
> Trigger: tonight's `403 INTERACTIVE_SESSION_REQUIRED` surfaced
> LIVE during the D1 endpoint work, not from a map — the gap this
> document closes. Sources: vendor documentation (snapdeploy.dev
> /api reference, /docs/free-tier "last verified 28 September 2026
> against the pricing page and the platform code", /docs/deployment,
> /pricing, /docs/faq) + fleet firsthand observation 2026-11-04.
> Vendor-stated figures are quoted as the vendor's; fleet-observed
> figures are stamped as such. Part of the hosting census series
> (companion: FREE-TIER-BACKEND-RECON-2026-10-21.md).

## 1. Identity and account

- Sign-up: email address or GitHub account; no credit card, no
  trial clock, free tier never expires.
- Fleet route (owner fact 2026-11-04 05:53 PT): GitHub sign-in via
  the fleet's existing GitHub identity — no new credential class.
- Infrastructure: every container is its own AWS Fargate task
  (single-tenant), addressed at
  `<name>.containers.snapdeploy.app` with HTTPS from first deploy.

## 2. Web surface (dashboard + mobile app)

Interactive-session surfaces — the ONLY surfaces that can perform
destructive actions (section 5):

- Containers list (account hours usage shown on the dashboard).
- Container page: Deploy button · environment-variable editor
  (change applies with a rolling restart) · build/runtime logs ·
  deployment history (status, commit, duration, triggerer —
  person, GitHub pusher, or AI assistant) · delete.
- API Keys page: create scoped tokens (`sd_pat_…`, scope +
  expiry), revoke tokens, one-line MCP connector setup.
- Billing page: Always-On subscriptions, $1 Sprint Pack, add-on
  purchases (all card-gated — fleet closed class).
- GitHub connection: link repositories; auto-deploy on push to
  the linked branch via webhook.
- Mobile app (iOS): a deploy trigger AND an interactive session
  for destructive purposes. Fleet: unused, unmapped in practice.

Deploy sources from the web flow: GitHub repository, public
Docker image (Docker Hub, GHCR, Quay, ECR Public), ZIP upload,
`docker save` tarball upload.

Fleet-observed (2026-11-04): there is NO in-place redeploy — the
upload and GitHub flows create-new and reject a taken container
name; freeing a name requires deleting the old container first
(section 5 bound). The Delete control inside an agent-driven
browser session was unresponsive tonight; the working delete
route is a person in the dashboard (or the mobile app).

## 3. API surface

Base URL `https://snapdeploy.dev`; all routes under
`/api/mobile/**`.

### Auth

- Scoped personal access token `sd_pat_…` (API Keys page; scope +
  expiry) or legacy unscoped key `sk_…`.
- Credential carriage: `X-API-Key: <key>` header, or
  `Authorization: ApiKey <key>`, or `?api_key=<key>`.
- Scopes nest: `read` ⊂ `deploy` ⊂ `manage`. Below-scope calls
  get `403 INSUFFICIENT_SCOPE` with `requiredScope` in the body.
  - read: every GET (bootstrap, containers, logs, deployments,
    deploy-cap, GitHub status/repos, env-var scan).
  - deploy: + create/link/deploy, env vars, start, stop, wake,
    resize.
  - manage: + add-ons (`/api/mobile/services/addons`), custom
    domains (`/api/mobile/services/domains`).
- Values are never returned to a token: env values come back as
  `(set)`, credential-looking fields as `(redacted)` — a token
  can set a value but never read one back.
- Up to 20 active tokens; revocation is immediate (401 from that
  moment). Attribution: `X-SnapDeploy-Client: mcp/<name>` on
  deploy calls; responses carry `initiatedBy`/`initiatedByLabel`.

### Endpoints

| Route | Scope | Notes |
| --- | --- | --- |
| GET `/api/mobile/bootstrap` | read | Profile+plan, all containers, deploy cap, free-hours usage in one call |
| GET `/api/mobile/deploy-cap` | read | `capped`, `remaining`, `dailyLimit`, `timeUntilReset` |
| POST `/api/mobile/containers` | deploy | Create (GitHub-bound apps use image `"pending"`). AUP scan at create; compressed image cap 1 GB free / 8 GB paid via this route |
| GET `/api/mobile/containers/{id}` | read | Status, URL, port (+detection confidence), tech, resources, env names |
| POST `/api/mobile/containers/{id}/start` · `/stop` · `/restart` · `/wake` | deploy | Start/restart/wake pass the free-hours gate (402); restart consumes a deploy unit on free accounts |
| PUT `/api/mobile/containers/{id}/env` | deploy | Replace env vars; rolling restart, no rebuild; public-prefixed names apply at build time |
| GET `/api/mobile/containers/{id}/logs?lines=200` | read | Runtime logs (CloudWatch), max 1,000 lines/request |
| GET `/api/mobile/containers/{id}/deployments?limit=20` | read | History, newest first, max 50 |
| GET `/api/mobile/deploy/image-upload-url?filename=&size=` | deploy | Presigned PUT URL + `s3Key` for a `docker save` file (.tar/.tar.gz/.tgz); file never passes through the API |
| GET `/api/mobile/deploy/image-upload-limits` | read | Caller's image caps; a 402 carries the store link |
| POST `/api/mobile/deploy/image` | deploy | Create from uploaded image (`s3Key`, `containerName`, `port`); image must be `linux/arm64`; ≤2 GB free / ≤10 GB Always-On |
| GET `/api/mobile/github/status` · `/github/connect-url` | read | Connection state; connect-url returns the browser link |
| GET `/api/mobile/github/repos` · `/repos/search?q=` · `/repos/{owner}/{repo}/branches` · `/repos/{owner}/{repo}/detect-env-vars` | read | Browse + pre-deploy env scan |
| POST `/api/mobile/deploy` | deploy | One-call deploy: creates container + links repo + starts first build; on link failure the created container is rolled back (`linkError`, `rolledBack: true`) |
| POST `/api/mobile/github/link` | deploy | Link repo to container — **linking itself triggers the first build**; do not also call deploy (double unit) |
| POST `/api/mobile/github/link/{repoLinkId}/deploy` | deploy | Redeploy a linked repo (CI hook); one deploy unit at trigger |
| GET `/api/mobile/deployments/{deploymentId}` | read | Poll: `COMPLETED`/`FAILED`/`CANCELLED`/`ROLLED_BACK`; failure carries `errorCode`, `errorMessage`, `buildLogsTail`, `smartFixEligible` |
| GET `/api/mobile/deployments/{deploymentId}/stream` | read | Live build log as Server-Sent Events |
| GET · POST `/api/mobile/services/addons` | manage | PostgreSQL/MySQL/MariaDB/MongoDB/Redis/RabbitMQ; creation needs a purchased add-on subscription (else purchase link in response); credentials shown in dashboard only, never to API callers |
| GET · POST `/api/mobile/services/domains` | manage | Attach custom domain; `GET …/domains/{domainId}/dns-records`; `POST …/domains/{domainId}/verify` |
| GET `/api/mobile/services/always-on/unassigned` · POST `/api/mobile/services/always-on/assign` | manage | Assign an existing Always-On subscription to a container (also starts it). **Cancelling or detaching is interactive-only** |

### Idempotency and pipeline

- `Idempotency-Key` on deploy calls: an identical request inside
  10 minutes returns the original deployment and consumes no
  extra deploy unit.
- One pipeline for all triggers (dashboard, GitHub push, API,
  iOS app, AI assistant): fetch → detect → check → build (AWS
  CodeBuild, 60-minute timeout, ARM64 images) → run (Fargate) →
  route. Redeploys are zero-downtime (new task healthy before
  traffic moves); a failed redeploy leaves the old task serving.
- No one-click rollback: revert in Git and push, or deploy the
  earlier commit's branch; every deployment's image is kept.
- Common failure codes: `MISSING_ENTRY_POINT`,
  `DATABASE_DRIVER_MISMATCH`, missing env vars, health-check
  never passed, build timeout.

## 4. MCP connector surface (AI assistants)

- Official MCP connector for Claude Code, Cursor, Windsurf,
  Codex CLI, Gemini CLI; setup with a pre-filled token from the
  API Keys page.
- Tools include deploy/create (`deploy_image` performs the
  upload flow), set variables, read logs, `get_deployments`.
- **No token can delete anything** — the connector has no delete
  capability by design (vendor docs, docker-hosting + MCP blog
  2026-09-23: "An AI assistant that can deploy is only useful if
  it can't destroy anything").

## 5. Destructive-action class — the 403 (the map's reason to exist)

Vendor API reference, verbatim: "**Destructive actions are
refused for API keys, by design.** Deleting containers,
databases, domains or your account, changing the password, and
cancelling subscriptions all return `403
INTERACTIVE_SESSION_REQUIRED` — they can only be done by a
person signed in to the web dashboard or the mobile app. A
leaked key (or an over-eager AI agent) cannot destroy anything."
Error-table entry: "this is deliberate and has no API
workaround."

Full membership established from the vendor docs:

| Action | Route class |
| --- | --- |
| Delete a container | interactive only |
| Delete a database (add-on) | interactive only |
| Delete a domain | interactive only |
| Delete the account | interactive only |
| Change the password | interactive only |
| Cancel a subscription (incl. detaching Always-On) | interactive only |
| Apply a SmartFix fix (commits to your repo) | interactive only — deterministic fix proposals are free to view; applying requires a signed-in session |

Fleet live confirmation (2026-11-04, Oversight lane): an API
delete attempt returned `403 INTERACTIVE_SESSION_REQUIRED`;
every non-interactive route (upload, GitHub-link, API) also
dead-ends on the name-gate — create-new flows reject a taken
name, so replacing a container under the same name is impossible
without an interactive delete first.

Operational consequences (standing):

- Any plan that needs a container slot or name freed must route
  around the delete: use a fresh name (the route the D1 endpoint
  took 2026-11-04 21:17 PT — `hostb-live-5b9d7` deployed fresh,
  the fit-test container left untouched), or schedule a genuine
  person-in-dashboard delete.
- An "owner Delete click required" claim is a state stamp, not a
  default: capacity is verified firsthand before any owner
  escalation (owner ruling 2026-11-04 21:14 PT — tonight's
  escalation on exactly this point was FALSE; fleet capacity
  existed all along).

## 6. Limits (free tier, vendor-stated)

| Limit | Free tier | Notes |
| --- | --- | --- |
| Containers | Up to 4 per account | Each its own Fargate task + HTTPS address; a 5th needs a delete, or (Always-On holders) a dashboard increase request to 8 |
| Size | Small: 512 MB RAM, 0.25 vCPU | Medium 2 GB/1 vCPU and Large 4 GB/2 vCPU are Always-On only |
| Running time | 100 container-hours/month per account | Shared across containers; refreshes monthly; sleeping counts 0; hours exhausted ⇒ containers cannot start (402 class) until refresh, Always-On, or Sprint Pack |
| Deploys | 10/day, max 5 per rolling 12 h | **Failed attempts count**; a unit is consumed when the build starts; restart also consumes one; idempotent API retries inside 10 min consume none extra |
| Sleep | After ~15 min without traffic | Sleeping container answers 503 wake page |
| Wake | ~60 s, browser visit only | Scripts, cron, CI, webhooks, monitors do NOT wake; once awake, automated traffic is welcome |
| Builds | Up to 60 min each | Most 1–5 min; images build for ARM64 |
| Image upload | Tarballs up to 2 GB | Up to 10 GB on Always-On; API-create route states compressed caps 1 GB free / 8 GB paid (surface-specific figures, both vendor-stated) |
| Traffic | 100 requests/min per IP to one app | Above ⇒ HTTP 429 for 10 minutes (shared domain fair use) |
| Persistent disk | None | Filesystem resets on redeploy, restart and wake; state belongs in a database add-on or object storage |
| Custom domains, WebSockets | Not on free | Always-On only |
| Databases | Not included | PG/MySQL/MariaDB/MongoDB/Redis/RabbitMQ are paid add-ons, each with a $1 12-hour trial |
| Outbound | TCP 1–27017 except 3333 and 9000–9099; UDP DNS/NTP | Same on every plan; add-ons reached internally; high-random-port providers (e.g. Aiven) unreachable |
| API rate | 150 req/min + 2,500 req/hour per user; each PAT has its own 150/min bucket; invalid keys throttled 30/min per IP | `429` body `DEPLOY_CAP_REACHED` = the deploy limit, distinct from rate throttling |

Error taxonomy (API): 400 `fieldErrors` · 401 invalid/expired/
revoked token · 402 plan limit (body carries `message`,
`actionUrl`, `actionText`, sometimes `spareSubscriptionId`;
do not retry) · 403 `INTERACTIVE_SESSION_REQUIRED` · 403
`INSUFFICIENT_SCOPE` · 404 · 429 · 500. AUP scan at container
create and every deploy: a match returns `400 Security policy
violation`, counts as a strike, and is final.

Acceptable Use bans (all plans): proxies, VPN panels, tunnels
and remote shells of any kind; crypto mining / key-cracking /
distributed brute-force; bot farms, view manipulation,
anti-bot evasion; flooding. Violation ⇒ container stopped,
account may be suspended.

## 7. Paid surface (card-gated — fleet closed class, map-only)

- Always-On per container: Small $12/mo · Medium $25/mo ·
  Large $45/mo (quarterly/annual discounts exist). Runs 24/7,
  no hour limit, no deploy cap, custom domains, WebSockets,
  images to 10 GB; 99.9% monthly uptime target.
- Sprint Pack: $1 one-time — 24 h Always-On for one Small
  container + unlimited deploys for the account; two packs
  stack to 48 h; non-refundable; does not add free hours.
- Add-ons: Redis from $12; PostgreSQL/MySQL/MongoDB/MariaDB
  priced on the pricing page; $1 12-hour trials.
- Dedicated GPU subscriptions exist (pricing page).

## 8. Fleet state and firsthand observations (2026-11-04)

- HOST-B fit test verdict FIT (Desk receipt): free Small ran
  strands-agents + boto3 1.43.123 at RSS 60.2→100.5 MB (~20% of
  the 512 MB cap, no OOM); cold wake measured 34.2 s after a
  17-min clean idle (vendor figure ~60 s); HTTPS live; fail-
  closed in substance (no AWS creds ⇒ no model output, no
  provider substitution) with the caveat that the default boto3
  credential chain stalls (IMDS retries) so the platform proxy
  page, not the app's own 503 JSON, reaches the wire — endpoint
  builds must fail fast (explicit env creds, IMDS off or
  short-timeout botocore config, pre-flight creds check).
  Container: `hostb-fit-test-5b9d7`,
  https://hostb-fit-test-5b9d7.containers.snapdeploy.app/
- D1 0.5.2 endpoint default (decision 2026-11-04 21:17 PT):
  fresh container `hostb-live-5b9d7`
  (https://hostb-live-5b9d7.containers.snapdeploy.app) deployed
  with the merged build + env; the delete/name-gate path was
  abandoned for the fresh name; the fit-test container is
  untouched.
- Discrepancies flagged, unresolved: (i) a lane stamp tonight
  reported container budget "4/5 left" — the vendor cap is 4
  per account; the stamp's denominator does not match the
  vendor figure and is not relied on. (ii) Image-size caps are
  stated per-surface by the vendor (1 GB free via API create vs
  2 GB tarball upload); both are recorded as stated.

## 9. Remaining gaps

- Mobile app surface: documented as an interactive session, not
  exercised by the fleet.
- Dashboard page inventory is doc-sourced; only the deploy,
  container and delete paths were exercised live tonight.
- SmartFix AI: proposal mechanics documented; apply path is
  interactive-only (section 5); not exercised.
