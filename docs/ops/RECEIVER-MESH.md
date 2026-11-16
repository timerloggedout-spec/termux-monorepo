# Receiver Mesh — design of record

Status: PROTOTYPE (2026-10-29). Generic external-event intake for
timerloggedout-spec/termux-monorepo. XAA subscription delivery folds into
this mesh as one source profile; the X-specific build remains PARKED
(owner order 2026-10-29) — nothing in this doc un-parks it.

## Why

GitHub Actions has no public listener. It natively receives repo events
(push, pull_request, issues, workflow_run, …) but cannot receive:

- pushes from external systems (X Activity API webhooks, SaaS, devices),
- anything needing a challenge/response handshake (X CRC, OAuth callbacks),
- pre-filtering/coalescing before a workflow run burns Actions minutes and
  PAT/API rate budget (feed-collect storm, 2026-10-29: ~143 gate runs in
  25 min contributed to PAT core exhaustion for user 233432881).

A receiver mesh is a set of thin, single-responsibility surfaces on
owner-account infrastructure (self-hosted = via GitHub | our accounts;
the Muse VM is a sandbox, not a service). Each surface does one job;
failsafe = hand-off to the next surface, never local state on the VM.

## Responsibilities (one job per surface)

| Surface | Job | Explicitly NOT its job |
|---|---|---|
| Cloudflare Worker (+ Queues, D1) | Edge intake: public HTTPS listener, HMAC verify, source-IP check (defense-in-depth), dedupe, coalesce, enqueue. Dead-letter in D1. | Business logic, commits, durable ledger |
| Vercel serverless | Handshake-shaped intake: CRC/challenge endpoints, OAuth callbacks, anything needing a framework runtime or preview-deploy testing. Second, independent intake path if Cloudflare is down. | Standing processing, storage |
| Neon (Postgres) | Durable event ledger: authoritative dedupe record, delivery log, replay source of truth (`receiver_events`). SQL-over-HTTP from workflows. | HTTP intake (no endpoint), compute |
| GitHub Actions | Processor: consumes dispatches/queue drains + scheduled reconciliation sweeps; all commit/PR/Neon-write logic; retry and replay driver. | Listening (no public URL) |
| Muse VM | Sandbox only: authoring, local test/replay harness, one-shot failover drills dispatched manually. See "VM scoped uses" — no standing listener, no daemon. | Hosting any mesh leg |

## Flow

```
source ──POST──▶ Cloudflare Worker ──verify──▶ Queue ──▶ repository_dispatch
                     │ dedupe (D1)                            │
                     └─ dead-letter (D1)                      ▼
                                          Actions processor workflow
                                             │            │
                                             ▼            ▼
                                       Neon ledger    repo commits / PRs
                     ▲
   Vercel function ──┘  (handshake sources; same dispatch contract)
                     ▲
   Scheduled Actions sweep ── reconciles Neon vs D1 dead-letters,
                               replays missed deliveries (failsafe leg 3)
```

Failsafe hand-offs:

1. Cloudflare down / source cannot reach it → Vercel function accepts the
   same signed envelope and dispatches identically (idempotent: Neon
   `delivery_id` unique constraint decides the winner).
2. Actions/PAT rate-limited → events wait in Cloudflare Queue + D1
   dead-letter; nothing is lost, the scheduled sweep drains when budget
   resets (pattern: feed-collect DEFER, 2026-10-29).
3. Dispatch lost → scheduled reconciliation sweep compares Neon ledger
   against source-side delivery logs and replays gaps.
4. Neon unavailable → processor writes the event payload to a repo
   artifact branch file (append-only JSONL) and the sweep re-ingests it
   into Neon later. Repo is the final fallback store.

## Verification stack (order matters)

1. HMAC signature — PRIMARY auth. GitHub: `X-Hub-Signature-256` over the
   raw body with the per-source webhook secret; timing-safe compare.
   X: CRC `GET ?crc_token=` answered with the consumer secret; POSTs
   carry `x-twitter-webhooks-signature`.
2. Source-IP allowlist — SECONDARY, defense-in-depth only, and only for
   GitHub sources. Ranges change (GitHub changelog 2026-10-29 added
   `9.234.98.160/28`, `9.234.98.176/28`, `9.234.106.48/28` to the Meta
   API `hooks` field). NEVER hardcode: fetch `https://api.github.com/meta`,
   cache ≤1 h, fail-open to signature-only if the fetch fails. A static
   list is exactly the failure this changelog warns about.
3. Dedupe — `delivery_id` (GitHub: `X-GitHub-Delivery`; X: event id)
   checked in D1 at the edge and enforced in Neon by unique constraint.

Payload discipline: forward an allowlisted, normalized envelope only
(`source, event, delivery_id, received_at, repo, action, actor,
object_id`) — never raw payloads wholesale, never credentials. Precedent:
the n8n SHE bridge in `deepagent/sweep/docs/ops/DEPLOYMENT-LANES.md`
(allowlisted receipt only).

## Secrets (names only — provisioning is an owner item, never invented)

- `RECEIVER_GH_WEBHOOK_SECRET` — GitHub webhook HMAC secret (Worker +
  Vercel env, same value both legs).
- `RECEIVER_DISPATCH_TOKEN` — dispatch-only credential for
  `repository_dispatch` on this repo alone (Worker/Vercel secret).
- Existing, already provisioned (do not re-create): `CLOUDFLARE_API_TOKEN`,
  `CLOUDFLARE_ACCOUNT_ID`, `NEON_API_KEY`, `LANE_EVENTS_DATABASE_URL`
  (lane-events project; a dedicated `receiver-events` database/branch is
  a provisioning decision, not assumed here).

## Actions integration

- `receiver-process.yml` — `repository_dispatch` type `receiver-event`:
  validates the envelope schema, writes the Neon ledger row, routes by
  `source`/`event` to the owning lane's existing workflow via
  `workflow_dispatch`. All heavy logic stays in the owning workflows.
- `receiver-reconcile.yml` — PHASE 2 (contract only, not in prototype):
  scheduled (hourly, jittered minute) + dispatch: drains D1 dead-letters
  via the Worker admin endpoint, replays, and reports a `receiver-health`
  issue comment only on change (no noise commits).
- Both workflows follow the fleet rate-limit discipline: preflight PAT
  check + DEFER exit (RATE-LIMIT-2026-10-29 pattern), retry with
  Retry-After on 403/429/5xx.

## VM scoped uses (proposals — each needs its own owner ruling)

The VM rule (2026-10-28) is sandbox-only; the sole named exception is
tmp-usage-tripwire (VM-self). The receiver work surfaced candidate
*novel* scoped uses; none is asserted here, all are proposals:

1. Local replay harness: feed captured envelopes from Neon/D1 into the
   processor logic locally to debug a failed delivery — authoring-class
   work, no listener. (Arguably already inside "sandbox".)
2. One-shot failover drill: a manually dispatched, minutes-long tunnel
   receiver to prove leg-2 hand-off, torn down in the same session —
   time-boxed, owner-present, not standing.
3. Break-glass manual intake: when both edge legs are down, an
   owner-triggered one-shot capture on the VM, imported to Neon after —
   manual, per-incident approval.

Any standing VM listener remains out of scope under the current rule.

## XAA fold-in (parked)

The XAA receiver design (2026-10-29, Observatory/XAA lanes) maps onto
this mesh unchanged: Vercel leg answers X CRC, Cloudflare leg is the
alternate, Neon holds the delivery ledger, Actions commits to
`x-index.json`. Differences from the GitHub profile: no IP allowlist
(X publishes none — signature/CRC only), `like.create` outbound is the
core event, no bookmark/unlike events exist (pull harvest remains).
Build of the X profile waits for owner un-park + X credits + the
`X_*` secret provisioning already recorded as blocked items.

## Existing repo state reconciled (anti-drift)

- `tmx-device-queue` Worker (live 2026-10-22) is the pattern precedent
  for the Cloudflare leg — a pull-queue rendezvous, not an event
  receiver; the mesh reuses its account, subdomain, D1 and secret
  provisioning route, not its code path.
- Repo webhook inventory already includes SaaS receivers (Buildkite
  joined 2026-10-23); those are vendor-side receivers and are out of
  scope — the mesh is only for events *we* must receive.
- Prior realignment attempts (VM-rule audits 2026-10-28) established
  that no lane runs a standing receiver today; this doc is the first
  receiver of record. Anything claiming to be a receiver elsewhere
  should be pointed here or retired.

## Prototype scope (this PR)

- `ops/receiver-mesh/worker/` — Cloudflare Worker: GitHub webhook
  profile (HMAC, dynamic Meta-IP check, D1 dedupe/dead-letter,
  repository_dispatch hand-off), `/health`.
- `.github/workflows/receiver-process.yml` — dispatch consumer +
  envelope validation + Neon ledger write (DEFER on rate limit).
- `tests/test_receiver_mesh.py` — envelope/HMAC/IP-range unit tests
  (offline, no network).
- NOT in prototype: Vercel leg code (contract defined above; build on
  first handshake source), Neon DDL applied live (DDL in
  `ops/receiver-mesh/processor/receiver_events.sql` for the DB lane),
  live Worker deploy (needs the two `RECEIVER_*` secrets provisioned).
