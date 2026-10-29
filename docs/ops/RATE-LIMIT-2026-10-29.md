# GitHub Rate Limit — Incident Recon + Mitigation Record (2026-10-29)

`[MUSEai]@{role:{rate-limit}}` — owner order via Pinecone lane (2026-10-28). PAT helper only; names-only credentials.

## Buckets — never conflated

| Bucket | Limit | Owner/token class | Evidence |
|---|---|---|---|
| PAT core | 5000/h | user `timerloggedout-spec` (id 233432881), MUSE_ADMIN_GH route | incident below; 2026-10-28 check: 683/5000 remaining (~4317 used that hour) while installation bucket was already exhausted — buckets are distinct |
| Actions `GITHUB_TOKEN` installation | 1000/h | repo installation, shared by all repo workflows | run 40706072646 surfaced `API rate limit exceeded for installation`; Delphi `gate.py` `defer_api`: early-return when remaining − reserve 100 < 26 (remaining ≲126/1000), "defer, never fail" |
| Search | 30/min | PAT | 2026-10-29T06:01Z reading: 2 used, reset per-minute |
| Code search | 10/min | PAT | 2026-10-29T06:01Z reading: 1 used |
| GraphQL | 5000/h | PAT | 2026-10-29T06:01Z reading: 67 used / 4934 remaining |

## Trigger incident

- 2026-10-29T05:50:14Z — PAT-helper `GET git/ref/heads/master` (first step of a `pat_publish`) → 403 `API rate limit exceeded for user ID 233432881`, request `33AF:1CEEDD`. Blocked the Pinecone live-proof append (PR source kept locally).
- Contributing cause (owned by the Pinecone lane): tight check-runs / workflow-run polling loops that hour.
- Resolution: that append landed post-reset as PR #2319, merged `dcad684819727fdcea14574de5a4495cea3f4cd2` (master-history scan + landed content verified by rate-limit lane).

## Current headroom (measured, not polled)

- 2026-10-29T06:00:16Z: core 0 used / 5000, reset 07:00:16Z; search 30/30; graphql 66 used.
- 2026-10-29T06:01:33Z: core 42 used — 42 calls fleet-wide in ~77s of the fresh window (this lane ≈10 of them). Baseline fleet burn is hot; sustained, that pace is ~1900/h before any polling spike, so a single lane's tight loop can close the remaining gap inside one hour. Exact per-consumer attribution is NOT ESTABLISHED (GitHub exposes no per-token-consumer breakdown to a PAT).

## Consumers of the PAT core budget (ranked by shape)

1. **Lane polling loops (dominant spike risk).** Polling check-runs + run status + PR read every ~10s = ~1080 calls/h per lane; 3 endpoints × 10s across 4–5 concurrent lanes exceeds the whole 5000/h bucket alone. This is the incident shape.
2. **`list-prs --all` sweeps.** Helper paginates `per_page=100` over all states; each sweep is pages × repeated sweeps per hour across lanes. Cheap once, expensive as a heartbeat.
3. **`pat_publish` / merge verification.** ~4 + N-files calls per publish, plus compare + master-history scan per merge — bounded, per-outcome, not a driver.
4. **Workflows using a user token.** Repository Observatory (daily cron `17 4 * * *`) feeds its collector `OPERATOR_GITHUB_TOKEN` (user token, same account) as `REPOSITORY_OBSERVATORY_TOKEN` — low frequency, not a hot-hour driver, but it draws on a user-class budget, not the installation bucket. All other workflows observed use the installation `GITHUB_TOKEN` (separate bucket, above).
5. **Ad-hoc recon `get` calls.** Bounded if single-read; becomes a driver only when scripted into loops.

## Existing guards

- Delphi gate `defer_api` reserve pattern (installation bucket): reserve 100, defer below ≲126 remaining.
- Dispatch-tree / Vercel batch guards: quota + cooldown gating on their own surfaces (cadence-owned).
- No equivalent reserve/preflight existed on the PAT-helper publish path — the incident step was the publish's first call, already at 0.

## Mitigations

Enacted as lane discipline by this record (no schedule/cadence change):

1. **Preflight before publish:** run `github_pat.py rate-limit` once before a `pat_publish` batch. Defer threshold is DERIVED from that live reading (cadence boundary 2, adopted 2026-10-29): defer when `remaining < planned_calls + limit/10` (reserve proportion taken from the response's own `limit`, never a hardcoded count); deferral is fail-soft + logged (Delphi `defer_api` pattern) — report the `reset` time, resume next window, never retry-loop against a 403. (This supersedes the fixed-count threshold in this record's first version.)
2. **No tight polling:** never poll check-runs/run status in a loop. Use completion handoffs / a single check after a bounded wait. One verification read per outcome (compare API = 1 call replaces per-file reads; master-history scan = 1 call).
3. **Sweeps are snapshots:** `list-prs --all` at most once per task, timestamped and reused across lanes via the repo record — never as a heartbeat.
4. **403 = stop:** a rate-limit 403 ends the attempt for that window; report reset time. No endpoint/tool switching to evade it.

## Cadence-owner boundaries (received 2026-10-29, `ac333a25` — adopted, this record conforms)

1. Poll floor: no new fixed-interval polling under the schema minimum (5 min); prefer event-driven (push / `workflow_run` / `issue_comment`) wherever a trigger exists.
2. Defer/reserve thresholds DERIVED from the live `/rate_limit` reading (remaining + reset), never hardcoded counts; defer = fail-soft + logged, work resumes next cycle.
3. Batching: one `commits/{sha}/check-runs` call per SHA, `per_page=100` on lists, stop-on-condition; full `--all` sweeps only in scheduled collectors, never per-PR/per-event lanes.
4. Orchestrator poll budget (cadence-owned exception, unchanged): `POLL_SEC ≥ 20s`, per-event polls bounded by `MAX_WAIT`; no cross-PR tight loops.
5. Any cadence/schedule change = proposal to the cadence owner WITH trigger accounting (executions + API calls per run); they land it as a QAC PR. No unilateral schedule edits in this record.
6. Consumer census ranked by calls/hour (below) is the evidence base for any interval proposal.

## Consumer census — ranked by calls/hour (evidence for cadence owner)

| Consumer | Interval / shape | Calls/hour |
|---|---|---|
| Lane tight polling loops (incident shape, Pinecone lane that hour) | ~3 endpoints (check-runs + run + PR), interval NOT ESTABLISHED; at 10s illustrative | ~1080/lane at 10s; multiple lanes ⇒ >5000 (whole bucket) |
| Peer-review orchestrator (cadence-owned) | `POLL_SEC` 20s, bounded by `MAX_WAIT` per PR event | ≤180 per active PR event |
| `list-prs --all` sweeps (per-PR/per-event lane use) | paginated `per_page=100`, all states | pages × sweeps/h — unbounded if repeated; boundary 3 confines to scheduled collectors |
| `pat_publish` + merge verification | per outcome, stop-on-condition | bounded, ~6–10 per PR |
| Repository Observatory collector | daily cron `17 4 * * *`, user token | negligible averaged; burst within its run only |

Proposals to the cadence owner (NOT enacted here; each needs trigger accounting before a QAC PR):

- P1: mirror the Delphi derived-reserve defer pattern on the PAT publish path fleet-wide (formula in mitigation 1).
- P2: a dispatch-only GitHub Workflow (VM hosts nothing) posting core/search/graphql headroom to a standing issue, at an event-driven or ≥5-min-floor cadence the cadence owner sets.

## Reset cadence

Core + GraphQL: hourly windows (reset timestamps in readings above). Search / code-search: per-minute. A blocked lane needs the reset timestamp from one `rate-limit` read, not repeated retries.
