# P1 Spec — Device Pull-Queue on Cloudflare Workers + D1

**Status:** BUILD-READY SPEC, written 2026-10-21 (backend/mesh-resiliency
specialist); published to `docs/ops/` on 2026-10-22 — the canonical copy lives
here. **Phase 1 (Worker + D1 schema + queuectl + tests) is built and merged
(PR #1507); deploy remains an owner step; the device poller (Phase 2) and the
Actions producer (Phase 3) are not yet built.**
Implements resiliency proposal **P1** from
`RESILIENCY-MAP-AND-STACK-PROPOSAL-2026-10-21.md` in this folder.
It is written so a builder (a Jules session, a chat, or the owner) can
implement it without making further design decisions. Fleet rules apply throughout: names-only credentials,
no telemetry deletion anywhere in the design, lean origin, quota-first.

---

## 1. Problem and design in one paragraph

Today, every path that gives the origin device work **pushes** through a fragile
rendezvous: an ephemeral Pinggy endpoint published to a git manifest that has
been a placeholder since 2026-10-17, SSH credentials split across two families
(one of which is absent from the repo secret store), and an opaque on-device
scheduler (Runable) whose failures are visible only inside its app. P1 inverts
the direction: work is **enqueued to a small Cloudflare Worker backed by D1**,
and the device **polls outbound HTTPS every 15 minutes**, claims one task
atomically, runs it locally, and posts a receipt. Outbound polling needs no
tunnel, no published endpoint, no inbound port, and no GitHub round-trip — it
works on any network the phone can browse from. The tunnel stack (Pinggy /
Tailscale / ADB) remains for what it's good at — interactive operator access —
and leaves the critical path for scheduled work.

## 2. Architecture

```
 producers                        rendezvous (Cloudflare Free)              origin device
 ─────────                        ────────────────────────────              ─────────────
 Actions workflow ──POST /tasks──▶ Worker (thin, <10 ms CPU)                Termux job 43112
 Jules / chats ─────POST /tasks──▶   │  D1: tasks, receipts                  (queue-poll.sh)
 owner CLI ────────POST /tasks──▶   │  KV: status mirror (optional, §9)        │  HTTPS poll
                                    │                                        ▼
                                    └──────── GET /tasks/next ────── claim (atomic UPDATE)
                                             POST /tasks/:id/receipt ──────── run + receipt
 fallback (§10): device-queue git branch, same task/receipt JSON shapes
```

Design choices, decided here so the builder doesn't have to:

- **D1-first, no Cloudflare Queues in v1.** The device is a poller, not a
  push consumer; D1 alone gives atomic claims and a queryable receipt ledger.
  Queues (10k ops/day free) is a v2 fan-out option for cloud-side executors.
- **The Worker stays thin.** All logic is auth + 4 SQL statements. Free-plan
  CPU is 10 ms/invocation — no payload parsing beyond JSON, no crypto beyond
  comparing a bearer token (constant-time compare), no external fetches.
- **Payloads are references, not blobs.** A task carries a small JSON payload
  (kind + params ≤ 4 KB). Anything larger (a task file, a diff) lives in the
  repo or R2 and is referenced by path/URL. D1 is a ledger, not a file store.
- **Task kinds are an allowlist**, mirroring the repo's existing fixed-command
  posture (`termux-bridge-connect.yml` refuses arbitrary commands; so do we):
  `deepagent-run`, `git-commit-push`, `git-sync`, `shell-allowlisted`
  (params must match an on-device allowlist file), `heartbeat-only`.
  **No free-form remote shell in v1.** The Hark remote-exec lane keeps that
  job, with its owner-only dispatch guard.
- **Receipts reuse the existing format.** `scripts/termux/run-deepagent-task.sh`
  already emits a schema_version-1 receipt (task_id, role, transport,
  started/finished, exit_code, completion_status, stdout/stderr paths).
  The queue receipt wraps it unchanged (§5).

## 3. Components to build

| # | Component | Home (proposed repo paths) | Runtime |
|---|---|---|---|
| B1 | Queue Worker | `ops/device-queue/worker/` (`wrangler.toml`, `src/index.js`) | Cloudflare Workers Free |
| B2 | D1 schema | `ops/device-queue/worker/schema.sql` | D1 (SQLite) |
| B3 | Device poller | `scripts/termux/devices/queue-poll.sh` + job installer entry in `scripts/termux/devices/install-device-jobs.sh` (new job id **43112**, origin role) | Termux bash + `curl` + `python3` (both already on-device per provisioning package list) |
| B4 | Producer CLI | `ops/device-queue/queuectl.py` (stdlib-only Python, same discipline as `scripts/quota_poll.py`) | Any chat / workstation |
| B5 | Actions producer | New workflow `device-queue-enqueue.yml` (workflow_dispatch + optional schedule for the nightly pair) — replaces `deepagent-task.yml`'s SSH push; that workflow is retired by a follow-up PR, not edited silently | GitHub Actions |
| B6 | Runbook | `docs/ops/DEVICE-PULL-QUEUE.md` (operations, rotation, failure table §11) | — |

## 4. D1 schema (complete — build as written)

```sql
CREATE TABLE tasks (
  id            TEXT PRIMARY KEY,              -- producer-supplied, e.g. dq-20261022-0025-eng
  dedupe_key    TEXT UNIQUE,                   -- producer idempotency key; NULL allowed
  kind          TEXT NOT NULL,                 -- allowlist in §2
  role          TEXT NOT NULL DEFAULT 'engineer',
  payload       TEXT NOT NULL DEFAULT '{}',    -- JSON, <= 4 KB enforced by Worker
  state         TEXT NOT NULL DEFAULT 'queued'
                CHECK (state IN ('queued','claimed','done','failed','expired','dead')),
  producer      TEXT NOT NULL,                 -- token label, never the token
  created_at    TEXT NOT NULL,                 -- ISO-8601 UTC
  expires_at    TEXT NOT NULL,                 -- after this, poller must not claim
  claimed_by    TEXT,                          -- opaque device id (tmx-node-primary, ...)
  claimed_at    TEXT,
  lease_until   TEXT,                          -- claim lease; §6
  attempts      INTEGER NOT NULL DEFAULT 0,
  max_attempts  INTEGER NOT NULL DEFAULT 3,
  receipt       TEXT,                          -- receipt JSON (§5) on terminal state
  finished_at   TEXT
);
CREATE INDEX idx_tasks_claim ON tasks (state, expires_at, created_at);
-- one row per state transition for the watcher surface; receipts stay on tasks
CREATE TABLE events (
  task_id TEXT NOT NULL, at TEXT NOT NULL, actor TEXT NOT NULL,
  from_state TEXT, to_state TEXT NOT NULL, note TEXT
);
CREATE INDEX idx_events_task ON events (task_id, at);
```

**Write budget (the D1 constraint that shapes everything):** free D1 allows
100k row-writes/day; each indexed write costs roughly one row-write per index.
One full task lifecycle ≈ claim (task update + event) + receipt (task update +
event) ≈ **6–10 row-writes**. At a heavy 200 tasks/day ≈ 2,000 writes = **2% of
the daily cap**. Idle polling writes **zero** rows (reads only: 96 polls/day ×
1 indexed SELECT ≈ nothing against 5M reads/day). The design is two orders of
magnitude inside the free envelope; the landing note's registry records
(`cloudflare.d1_rows_written` safety 0.8) formalize the budget.

## 5. API contract (complete)

All routes require `Authorization: Bearer <token>` except `GET /health`.
Tokens are per-actor (§7); the Worker maps token → actor label and stamps it
on rows. Responses are JSON; errors are `{ "error": "<code>" }` with the HTTP
status shown. Timestamps ISO-8601 UTC.

| Route | Actor | Body / params | Result |
|---|---|---|---|
| `POST /tasks` | producer | `{ id?, dedupe_key?, kind, role?, payload, expires_at }` | `201 { id, state: "queued" }`; `409` if `dedupe_key` already exists (returns the existing id — enqueue is idempotent); `400` on kind not in allowlist or payload > 4 KB |
| `GET /tasks/next?role=<role>` | device | — | Atomically claims the oldest unexpired `queued` task for the role (§6 SQL): `200 { task }` or `204` when empty |
| `POST /tasks/:id/receipt` | device (the claimant) | Receipt JSON (below) | `200`; sets `done`/`failed` from `completion_status`; `403` if `claimed_by` ≠ caller |
| `POST /tasks/:id/release` | device | `{ note }` | Returns a claim to `queued` without consuming an attempt (clean shutdown path) |
| `GET /tasks/:id` | producer, device | — | Full row incl. receipt |
| `GET /health` | public | — | `{ ok: true, queued: n, claimed: n, dead: n, oldest_queued_age_s: n, at: iso }` — counts only, no payloads, no device ids beyond role counts. This is the surface the 6h census poll and the bridge-state watcher read |

Receipt body (wraps the existing on-device receipt unchanged):

```json
{
  "schema_version": 1,
  "task_id": "dq-20261022-0025-eng",
  "device_id": "tmx-node-primary",
  "receipt": { "...": "exact object emitted by run-deepagent-task.sh (schema_version 1)" },
  "storage_free_mb": 1234,
  "note": "optional operator/device note"
}
```

`storage_free_mb` is mandatory in the wrapper: every receipt doubles as a
storage telemetry point, closing the "93% with no later reading" gap from the
resiliency register (SPOF-9) without a new watcher.

## 6. Claim protocol (the part that must be exactly right)

```sql
-- one statement, executed by the Worker for GET /tasks/next
UPDATE tasks
SET state='claimed', claimed_by=:device, claimed_at=:now,
    lease_until=:lease, attempts=attempts+1
WHERE id = (SELECT id FROM tasks
            WHERE state='queued' AND expires_at > :now
              AND (role = :role OR role = 'any')
            ORDER BY created_at LIMIT 1)
RETURNING *;
```

- **Lease = 45 minutes** (3 poll cycles). A reaper step inside the same Worker
  invocation (before claiming) returns `claimed` rows with `lease_until < now`
  to `queued` — unless `attempts >= max_attempts`, in which case → `dead` +
  event. No cron needed; the reaper rides every poll.
- **Crash semantics:** device dies mid-task → lease expires → another claimant
  (or the same device after reboot) re-claims. Tasks must therefore be
  idempotent or self-guarding on-device: `git-commit-push` checks for a clean
  already-pushed state first; `deepagent-run` keys its session/checkpoint by
  task id (the device lineage already checkpoints per run — RESILIENCE.md
  layer 3).
- **Expiry:** `expires_at` is producer-set (nightly pair: ~6 h). Expired queued
  tasks are reaped to `expired` by the same in-poll reaper step; a task never
  runs stale the next night — tomorrow's enqueue is a new id.

## 7. Auth and secrets (names only — values never in repo, chat, or this spec)

| Name | Held by | Grants |
|---|---|---|
| `DEVICE_QUEUE_PRODUCER_TOKEN_ACTIONS` | GitHub Actions secret (B5) | `POST /tasks`, `GET /tasks/:id` |
| `DEVICE_QUEUE_PRODUCER_TOKEN_CLI` | Owner workstation / chat vault entry | same |
| `DEVICE_QUEUE_DEVICE_TOKEN_PRIMARY` | Origin device, `~/.config/tmx-device/queue.env` (mode 600, alongside the existing identity.env) | claim / receipt / release for `tmx-node-primary` |
| `DEVICE_QUEUE_DEVICE_TOKEN_SECONDARY` | Secondary device, same path | same, for `tmx-node-55619bd5` |

Worker side: the four token *values* live as Worker secrets
(`wrangler secret put`), compared against a label map in the Worker
environment. **Rotation:** issue new token → deploy Worker accepting both →
update the holder → revoke old. One paragraph in the runbook (B6), rehearsed
once at build time so the first real rotation isn't improvised.
**Compromise posture:** a leaked device token can claim and receipt tasks but
cannot enqueue, cannot widen the kind allowlist (enforced again on-device,
§8), and cannot read other tasks' payloads (`GET /tasks/:id` for a device is
restricted to rows it claimed). A leaked producer token can enqueue allowlisted
kinds only — the on-device allowlist is the real security boundary, same
posture as `termux-bridge-connect.yml`'s fixed health command.

## 8. Device poller (B3) — behavior contract

`queue-poll.sh` runs under job **43112** (15-min period, `--persisted true`,
`--battery-not-low false --storage-not-low false` — matching the existing job
family), and must:

1. Source `~/.config/tmx-device/identity.env` + `queue.env`; exit 0 silently if
   either is missing (sentinel discipline: no notification spam for an
   unprovisioned node).
2. Read the resource snapshot (`termux-resource-snapshot.sh`). If free storage
   < the adaptive floor (max(500 MB, 2× the task kind's expected footprint)
   from the resiliency proposal P2), post **no claim**; write a local log line
   and exit 0. Heavy kinds additionally require the wake-lock held.
3. `GET /tasks/next` (curl, 20 s timeout, one retry after 30 s). `204` → exit 0.
4. Validate the claimed task **on-device**: kind in the local allowlist file
   (`~/.config/tmx-device/queue-allowlist.txt`, owner-editable, shipped with
   the §2 five), payload parses, not expired. Failure → receipt with
   `completion_status: "failed"`, `note: "rejected:<reason>"`.
5. Execute by kind: `deepagent-run` → `scripts/termux/run-deepagent-task.sh`
   with `DEEPCLI_TASK_ID` = queue id (receipt format already matches);
   `git-commit-push` / `git-sync` → the repo's existing on-device scripts in
   `$HOME` (the real checkout — **no `~/termux-monorepo` assumption anywhere**;
   `TERMUX_MONOREPO_ROOT` honored, per the SPOF-2 lesson);
   `shell-allowlisted` → exact-match lookup in the allowlist file, no shell
   interpolation of payload strings.
6. Post the receipt (§5) with `storage_free_mb` from step 2's snapshot.
   Receipt post failure → keep the receipt file under
   `~/.local/state/tmx-device/receipts/` and retry posting next cycle before
   claiming new work (receipts are never lost to a network flap).
7. Log locally to `~/.local/state/tmx-device/queue-poll.log`, rotated at 1 MB
   (lean device; logs are not telemetry — rotation here does not touch any
   HindSight/training tree).

**Runable's new role:** none required. During migration (§10) the two Runable
tasks keep firing; if a Runable run and a poller claim race the same logical
job, the queue's dedupe is by task id and the git task's own clean-state check
makes the second run a no-op. After 7 consecutive nights of poller receipts
for both nightly kinds, the owner may retire the Runable triggers — recorded
decision, not a silent clearing.

## 9. Optional phase 2 (do not build in v1)

- **KV status mirror:** Worker writes the `/health` object to KV on every
  state change (≤ a few hundred writes/day vs the 1,000/day KV free cap) so
  dashboards read status without touching D1 or the GitHub API.
- **Queues fan-out:** cloud-side executors (Codespaces claimant, Oracle A1 if
  provisioned) subscribe as additional claimants with their own device tokens
  and roles — the claim protocol already supports N claimants; roles keep the
  phone's tasks off cloud executors and vice versa.
- **GitHub status bridge:** an Actions workflow on a schedule (existing
  cadence family, no new trigger class) reads `/health` and mirrors a
  three-state summary (up / degraded-known / down-new, per resiliency P6)
  into the existing bridge tracking issue.

## 10. Fallback and exit (free-tier mortality rule)

If Cloudflare's free tier changes or the account is lost, the **same task and
receipt JSON shapes** run over the pre-designed git fallback: a `device-queue`
side branch holding `queued/<id>.json` + `receipts/<id>.json`, `[skip ci]`
commits, device polls by `git fetch` — the pattern the heartbeat design
(`device-heartbeat` branch) already established. `queuectl.py` takes a
`--backend cloudflare|git` flag from day one so producers don't change.
Every free-tier dependency in this spec has its exit named *here, before it
becomes load-bearing*, per the recon's mortality rule.

## 11. Failure table (spec-level; runbook B6 expands)

| Failure | Behavior |
|---|---|
| Worker/D1 down or account lost | Poller exits 0, logs, retries next cycle; producers fall back per §10; `/health` absence is itself the down-new signal for the census poll |
| Device offline > lease | Claims reap automatically (§6); nightly tasks expire rather than pile up |
| Duplicate enqueue | `dedupe_key` unique → 409 with existing id; nightly producers use `dq-<yyyymmdd>-<kind>` keys |
| Payload > 4 KB / bad kind | 400 at enqueue; on-device revalidation is the second gate |
| D1 write budget pressure | Lifecycle ≈ 10 writes/task; at the safety-0.8 line (80k/day) the Worker refuses new enqueues with `503 { error: "write_budget" }` rather than dying mid-claim |
| Token leak | §7 rotation; blast radius bounded by allowlists on both sides |

## 12. Build order and acceptance tests

**Order:** B2 schema → B1 Worker (+ secrets) → `queuectl.py` round-trip from a
workstation → B3 poller on the **secondary first** (working screen) with
`heartbeat-only` tasks → origin install via the §P4/R2 device session →
B5 Actions producer → retire nothing; Runable demotion is §8's 7-night rule.

**Step 0 — RESOLVED (owner, 2026-10-22 00:38 PDT):** the Cloudflare account
already exists ("CloudFlare account already made" — owner's direct statement).
Remaining Step-0 work is only credential plumbing: a wrangler/API credential
for deploys reaches the build lane via the vault route, names-only, when the
build is dispatched. The `cloudflared` Tunnel consent block is a different
product and does not gate Workers deploys (wrangler authenticates separately).

**Acceptance tests (all must pass before the origin depends on it):**
1. Enqueue → claim → receipt round-trip ≤ 1 poll cycle, from `queuectl.py`,
   on the secondary.
2. Kill the device process mid-task; lease expiry re-queues; second claimant
   completes it; exactly one terminal receipt exists.
3. Duplicate `dedupe_key` enqueue returns the original id; no second claim.
4. Expired task is never claimed; reaper marks it `expired` with an event.
5. Storage floor: with free space forced below the floor, poller claims
   nothing and the receipt stream shows the floor value (test on secondary).
6. `/health` counts match D1 after a scripted 20-task burst; write-budget
   projection for the burst ≤ 300 row-writes.
7. Token matrix: device token cannot enqueue (403); producer token cannot
   claim (403); wrong-claimant receipt post is 403.
8. airplane-mode night: device offline for a full cycle, then online —
   queued tasks drain in order, none lost, none double-run.

## 13. What this spec deliberately does not do

- The spec document itself performs no account signups, deploys, or device
  changes; the Phase 1 code landed separately (PR #1507) and deploy is an
  owner step.
- No free-form remote shell (the Hark lane keeps that, owner-gated).
- No change to the Pinggy/Tailscale/ADB stack: it stays, demoted to
  interactive access, exactly as resiliency P3 orders it.
- No deletion or relocation of any on-device data, telemetry included —
  the poller writes only its own state directory.

*End of spec. Companion deliverables from the same order:
`registry-additions/` (drafted + validated) and
`FREE-TIER-BACKEND-RECON-2026-10-21.md` (§2–§4 are this spec's quota basis).*
