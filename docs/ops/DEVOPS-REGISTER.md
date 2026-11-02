# DevOps Register — CI Health + Schedule-Delivery Watch

Standing record of the fleet DevOps seat (`Infra · DevOps — CI · Dispatch · Deploy
Reliability`, stood up 2026-11-02). Owner approval 2026-11-02: five holds —
① CI/Actions health register ② schedule-delivery watch ③ deploy-plane ops board
④ dispatcher day-2 operations (effective when Continuous Stewardship's #3812
step-4 build lands) ⑤ workflow-reliability first response. The federated set
(Cadence pacing · Stewardship builds · Vercel Specialist execution · Web Dev/Viz +
Repo Org Pages · Mesh Resiliency failover/backup/latency · Provisioning credentials ·
AppID lifecycle · Releases APK · Repo Org gate definitions) stays with its named
owners; this register records state, it does not absorb functions.

Update discipline: event-driven, by this seat. Census rows are appended with
timestamps and never rewritten; a correction is a new row that names the row it
supersedes.

## §1 CI / Actions health register

**State of record: PARKED.** Since 2026-10-29 (first observed by the Observatory
lane: runs completing `action_required` without executing), check runs do not
reliably execute on this repo. Merge discipline of record until a state change is
registered here: hand-verification (branch blob read-back + local suites) per fleet
pattern; no merge cites CI as evidence while this state stands.

Census method: (a) run-status totals via `GET /actions/runs?status=<s>&per_page=1`
(`total_count` = runs currently in that status); (b) newest-100 window sample —
conclusion distribution of completed runs + statuses of the rest. The window
sample is burst-dominated by construction (a fan-out burst creates ~100 runs in
under a minute); it measures execution share, not throughput.

### Census 2026-11-02T12:39Z (PAT, firsthand)

| Measure | Value |
|---|---|
| Workflows registered (`/actions/workflows`) | 309 |
| Runs currently `action_required` | **2,500** |
| Runs currently `queued` / `in_progress` / `pending` / `waiting` | 58 / 40 / 14 / 0 |
| Newest-100 window span | 46 s (12:38:53Z → 12:39:39Z) |
| Window: completed 78 | skipped 65 · cancelled 10 · **success 3** |
| Window: in flight | in_progress 4 · queued 13 · pending 5 |
| Executed-success share of completed | 3/78 ≈ 3.8% |
| Distinct workflows in window | 32 |

Reading: the queue is not idle — runs are created at burst rates and overwhelmingly
resolve as `skipped` (dispatch-tree gating) while a 2,500-run `action_required`
backlog stands unexecuted. Both numbers are the parked state's shape: admission
and approval, not runner capacity, are the binding constraints.

State-change rule: this section's state flips only on a census showing (a) the
`action_required` backlog draining across two consecutive censuses AND (b)
executed-success share of completed runs in the newest-100 window ≥ 50%.
Anything less is a new census row under PARKED.

## §2 Schedule-delivery watch

Rule: for every workflow carrying a `schedule:` trigger, silence beyond
2× its nominal interval + 1 h (GitHub jitter allowance) is a **visible finding**
(filed as an issue capture), never a silent gap. Precedent: the 2026-10-23 cadence
takeover starved tree consumers for days with no failing signal anywhere
(docs/ops record; quota-dispatch-tree delivers ~6×/day at jittered minutes against
far denser nominal crons across the fleet).

Enumeration 2026-11-02: code search over `.github/workflows` for `schedule`
returns **99 files**, including false positives (an `.md`, a `.lock.yml`,
dispatch-only files whose text mentions scheduling) and ∅-cron-by-design files
(`latency-probe.yml` dispatch-only · `quota-usage-series-refresh.yml` push-driven —
both excluded from the watch by design). Nominal-cron extraction for the full set
is the next pass; the critical subset below is baselined now.

### Critical subset — last firing at census (2026-11-02T12:40Z)

| Workflow | Last run | Event | State |
|---|---|---|---|
| quota-dispatch-tree.yml | 2026-11-02T09:56Z | schedule | FIRING-SPARSE (≈2.7 h gap vs */10 nominal; known GitHub under-delivery) |
| observer-poller-scheduled.yml | 2026-11-02T08:28Z | schedule | FIRING |
| github-telemetry-snapshot.yml | 2026-11-02T10:56Z | schedule | FIRING |
| ml-pr-lane-classify.yml | 2026-11-01T11:59Z | schedule | FIRING (daily-class gap) |
| dispatch-tree-feed-collect.yml | 2026-11-01T14:13Z | schedule | LAST SCHEDULE FAILED; dispatch runs since ✓ |
| telemetry-ingest.yml | 2026-11-02T12:33Z | push | ACTIVE (event-driven in practice) |
| repo-tracking-collect.yml | 2026-11-02T12:29Z | push | ACTIVE |
| surface-feeds-collect.yml | 2026-11-02T10:57Z | push | ACTIVE |
| delphi-ledger-feed-collect.yml | 2026-11-02T12:40Z | workflow_run | ACTIVE (pending at census) |
| operator-matrix-generate.yml | 2026-11-02T12:38Z | pull_request | ACTIVE |
| issue-lifecycle-triage.yml | 2026-11-02T12:27Z | issues | ACTIVE, latest FAILED (intermittent rate-wall class of record) |
| merge-promotion-queue-v3.yml | 2026-11-02T12:40Z | workflow_run | ACTIVE (skipped by design) |
| agent-runtime-stall-watch.yml | 2026-11-02T10:05Z | workflow_dispatch | ACTIVE (dispatch) |
| challenge-countdowns-refresh.yml | 2026-11-02T09:42Z | push | ACTIVE, latest FAILED |
| registration-monikers.yml | 2026-11-01T09:49Z | push | ACTIVE (event-driven) |
| traffic-feed-collect.yml | 2026-10-28T06:49Z | workflow_dispatch | **STALE-CANDIDATE** (5 d) |
| actions-run-watcher.yml | 2026-10-25T00:43Z | push | **STALE-CANDIDATE** (8 d; latest FAILED) |
| context-relationship-reconcile.yml | 2026-10-26T13:04Z | schedule | **STALE-CANDIDATE** (7 d since last schedule firing) |
| ci-sweep.yml | 2026-10-23T16:08Z | schedule | **STALE-CANDIDATE** (10 d) |
| actions-queue-reaper.yml | 2026-10-23T17:15Z | schedule | **STALE-CANDIDATE** (10 d — the queue's own reaper is silent while 2,500 runs sit action_required) |

STALE-CANDIDATE = last firing far beyond fleet-typical cadence; the starvation
verdict waits on nominal-interval extraction (next pass). Candidates are named,
not smoothed: if a candidate's cron is monthly-class, the next pass clears it in
a correction row.

## §3 Next passes (this seat)

1. Nominal-cron extraction for all 99 enumerated files → per-workflow expected
   interval column; stale candidates resolved to STARVED or cleared.
2. Deploy-plane ops board (§ approval ③) as §4 of this register: Pages · Vercel ·
   Fly · Koyeb {last deploy · mechanism · failure class · blocking item}.
3. CI census repeated on state-change suspicion or weekly-class cadence,
   appended as new rows.
