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

## Cadence-owner enactment (2026-10-29, `[MUSEai]@{role:{cadence-optimizer}}`, QAC-007)

- **P1 ENACTED.** `pat_publish.py` (the fleet's shared PAT publish path) now runs a derived-reserve preflight before any counted call: one `/rate_limit` read (uncounted), `planned_calls = files + 7`, defer when `remaining < planned_calls + limit/10` — fail-soft, exit 3, nothing created, reset time printed, resume next window. Formula exactly as mitigation 1; reserve is a proportion of the live limit, never a hardcoded count. Live verification 2026-10-29T06:03Z: `remaining=4743/5000 planned_calls=8 defer_threshold=508 reset=2026-10-29T07:00:44Z` → safe, `--preflight-only` created nothing. Trigger accounting: +1 uncounted read per publish; saves a full publish batch (~6–10 counted calls) whenever it defers.
- **P2 DEFERRED (cadence-owner decision, with rationale).** A scheduled headroom-posting workflow spends the scarce resource to report it: the PAT-bucket reading requires the user-class token (the installation token reads only its own bucket), so every scheduled run burns the budget it monitors, and at any ≥5-min-floor cadence that is ≥288 user-bucket reads/day for a signal P1 now surfaces at the exact moment of need (publish time). Revisit only on an event-driven trigger that does not itself consume PAT core (e.g. piggybacking the reading onto an existing scheduled collector's already-planned call), proposed with trigger accounting per boundary 5.

## Incident 2 (2026-10-29, 11:41–12:41Z window)

Second full exhaustion of 2026-10-29 (incident 1 at 05:50:14Z, above).

- **Window / shape.** Full-window burn: 5000 core calls in ~25 min. Firsthand anchors: remaining 3244 / used 1756 at 11:48Z; the forwarding lane's segment alone was remaining 1452 at 11:56Z → 0 at ~12:06Z; reset 12:41:45Z. The earlier "~1452 calls in ≤50 min" figure was only that segment, not the window total.
- **Attribution census (search bucket, separate).** Only 4 PRs were touched in the window: #2332 (X OAuth, 11:51Z), #2333 (cross-plane graph, 12:01Z), #2310 and #2263 (Delphi feed refreshes, ~12:10Z). Write activity was therefore tiny; the burn shape is read / verify / poll traffic across concurrently active lanes (X-Observatory finishing #2331/#2332, cross-plane #2333, Delphi feed lanes, Observatory extension recon lanes seeded that morning). Exact per-consumer attribution remains NOT ESTABLISHED — GitHub exposes no per-consumer breakdown to a PAT. Owner attribution on record: "Rate limit was from the burst of side chats."
- **Adjacent spends that morning.** The cross-plane lane's own spend was ~15 core calls total. In the prior window, the Following Graph lane burned core 244 → 0 in ~2 min (11:04–11:06Z, request `4CB5:1198E7`); distinct 403s in the same minutes were Observatory `8A71:1F1A72` at 11:06:05Z and X-delegate `812F:218A39` at 11:05:55Z.
- **FIX v1 LANDED (connector-local, live-proven 2026-10-29 ~12:11Z).** Circuit breaker in the shared PAT helper `github_pat.py`: before any counted core call it makes one uncounted `/rate_limit` read and defers fail-soft (exit 3, reset printed) when `remaining < limit/10` (derived reserve, never hardcoded); `/rate_limit` and `/search/*` paths are exempt (search buckets are separate); override `GHPAT_ALLOW_LOW=1` for owner-ordered critical work only. Every attempted counted call is logged to `spend.jsonl` beside the helper (timestamp, session id, path, `remaining_before`) — future windows are attributable by endpoint + time from the ledger. Proof: at remaining 0 a counted `user` call exited 3 and core stayed at full use (5000 used) — zero counted spend. Scope correction: the breaker covers callers of this helper copy on this VM only — Actions workflows on `OPERATOR_GITHUB_TOKEN` and non-helper surfaces are NOT covered. The breaker fails open if the uncounted read itself errors (by design).
- **FIX v2 LANDED (same helper, 2026-10-29 ~05:20 PT, owner order "fix the rate limit issue to prevent this stall").** (a) ETag conditional GETs — repeat reads of unchanged resources return 304, which does not count against the primary limit; cache beside the helper; first live exercise = the cross-plane lane's fresh-window reads. (b) Per-session hourly cap (default 400 counted calls/session/hour) + reserve fraction, both read from `budget.json` beside the helper on every invocation — cadence re-allocates by editing `budget.json`, no code change. (c) Token verdict recorded: more same-account PATs in rotation add ZERO quota (core limit is per-user id 233432881, not per-token); the only quota-adding token change is a different principal (GitHub App installation token, own bucket) — structural proposal to the cadence owner with trigger accounting: move scheduled collectors / orchestrator to an App installation token, reserve the PAT for interactive publishes; App creation / install is an owner provisioning item, NOT done.
- **P2 status update.** The deferred scheduled headroom workflow remains DEFERRED for the cadence owner's original reason (it burns the bucket it monitors); the breaker + ledger supersede its signal at the exact moment of need, and the ledger replaces its attribution purpose prospectively.
