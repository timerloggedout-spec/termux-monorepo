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

### CORRECTION 2026-11-02T13:35Z — the "2,500" figure is withdrawn

The §1 census table above records "Runs currently `action_required` = 2,500".
That number is the runs API's `total_count` **saturation cap**, not a count —
the fleet established this on 2026-10-31 (ruling of record, SWARM doc PR #2748)
and this register's v1 repeated the withdrawn figure in error. Superseded
statement, measured this census with fine `created=` partitions (coarse or
unbounded partitions saturate at 2,500 and are not evidence):

- disjoint measured partitions: pre-2026-10-24 = 123 · 2026-10-24→10-27 = 77 ·
  2026-11-01 in 8 h slices = 716 + 1,481 + 257 = 2,454 · 2026-11-02→census = 1,967
- **floor: the parked pile is ≥ 4,621 runs** (supersedes the 2026-10-31 floor of
  ≥2,666), plus the 2026-10-27→11-01 span whose partitions saturate — **exact
  total NOT_ESTABLISHED**
- census method corrected accordingly: backlog claims use fine partitions only;
  a reading of exactly 2,500 is recorded as SATURATED, never as a count

### Census 2026-11-02T13:29Z (census #2)

| Measure | Census #1 12:39Z | Census #2 13:29Z |
|---|---|---|
| Runs `queued` / `in_progress` / `pending` / `waiting` | 58 / 40 / 14 / 0 | **157 / 52 / 40 / 0** |
| Newest-100 window span | 46 s | 49 s |
| Window completed | 78 {skipped 65 · cancelled 10 · success 3} | 66 {skipped 55 · cancelled 11 · **success 0**} |
| Executed-success share of completed | 3/78 ≈ 3.8% | **0/66 = 0%** |
| Newest `action_required` run created | — | 2026-11-02T13:23:38Z (inflow live) |
| Pre-2026-10-24 parked stratum | 166 (2026-10-31 probe) | 123 (**−43: the only measured drainage**) |

**Flip rule: NOT MET on either leg.** (a) Draining cannot be established —
census #1's backlog figure is invalid (cap artifact) and census #2's measured
floor (≥4,621) exceeds it; the −43 oldest-stratum movement is a trickle against
~2.5k/day-class inflow. (b) Executed-success share 0% < 50%. State stays PARKED.

**Named blockers per component (evidenced):**
1. *Approval/admission pile* — ≥4,621 parked runs, inflow live at census minute,
   and **no drain mechanism exists in any lane's hands** for the parked pile;
   drainage observed only as −43 in the oldest stratum over two days.
2. *Execution share* — completed runs resolve `skipped` (dispatcher admission
   gating; cf. #3812's repo-wide busy≥6 pause) or `cancelled` (burst
   self-congestion); the remediation build is Stewardship #3812 step 4 — this
   seat's day-2 operations begin at its landing.
3. *Queue pressure* — queued+pending rose 72 → 197 between censuses while
   ~100-run bursts land in <50 s windows; GitHub schedule under-delivery
   (dispatch-tree sparse firing, §2) compounds the backlog.

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

### Cron extraction pass 2026-11-02T13:45Z — critical subset (20/99)

Nominal crons read from the workflow files at master; verdicts vs §2 census
firings. Watch rule v2 (refines §2's rule with observed platform behavior):
GitHub's delivered cadence on this repo ceilings at ~6 firings/day with lags up
to ~7.6 h, so — sub-daily crons: STARVED = 0 firings in 24 h; FIRING-SPARSE =
firing, chronically below nominal. Daily-or-slower: MISSED = no delivery by
nominal + 12 h; STARVED = 2 consecutive missed firings.

| Workflow | Cron (UTC) | Last schedule firing | Verdict |
|---|---|---|---|
| quota-dispatch-tree.yml | */10 * * * * | 11-02T09:56Z | FIRING-SPARSE (chronic under-delivery of record) |
| observer-poller-scheduled.yml | */20 * * * * | 11-02T08:28Z | FIRING-SPARSE |
| github-telemetry-snapshot.yml | 17 3 * * * | 11-02T10:56Z (+7.6 h late) | FIRING-DELAYED |
| ml-pr-lane-classify.yml | 37 5 * * * | 11-01T11:59Z (+6.4 h late) | FIRING-DELAYED; 11-02 firing pending at census |
| dispatch-tree-feed-collect.yml | 7 7 * * * | 11-01T14:13Z (failed) | FIRING-DELAYED; 11-02 firing pending |
| telemetry-ingest.yml | 23 7 * * 3 (Wed) | masked by push runs | NOT_ESTABLISHED (schedule leg) |
| repo-tracking-collect.yml | 23 7 * * * | masked by push runs | NOT_ESTABLISHED (schedule leg) |
| surface-feeds-collect.yml | 41 6 * * 3 (Wed) | masked by push runs | NOT_ESTABLISHED (schedule leg) |
| delphi-ledger-feed-collect.yml | 47 6 * * 2 (Tue) | masked by workflow_run runs | NOT_ESTABLISHED (schedule leg) |
| operator-matrix-generate.yml | 41 6 * * * | masked by PR-event runs | NOT_ESTABLISHED (schedule leg); event leg ACTIVE |
| issue-lifecycle-triage.yml | 17 7 * * 2 (Tue floor) | event leg 11-02T12:27Z | ACTIVE via events (latest failed = rate-wall class) |
| registration-monikers.yml | 41 6 * * 2 (Tue) | next due 11-03 | PENDING |
| challenge-countdowns-refresh.yml | 6 16 * * 1 (Mon) | due 11-02T16:06Z | PENDING-TODAY (last run = push, failed) |
| traffic-feed-collect.yml | 23 9 * * 2 (Tue) | none in last-5-run window | **STARVED-CANDIDATE** — confirm at 11-03 firing |
| context-relationship-reconcile.yml | 17 6 * * 1 (Mon) | 2026-10-26T13:04Z | **MISSED-FIRING CANDIDATE** — 11-02 firing undelivered at census (grace to ~14:17Z per lag precedent) |

**The five §2 stale candidates, resolved:**
- `ci-sweep.yml` — **CLEARED**: no `cron:` trigger exists in the file at master;
  its last schedule run (2026-10-23) predates the trigger's removal. Config
  state, not delivery failure.
- `actions-queue-reaper.yml` — **CLEARED as starvation, reclassified CONFIG
  GAP**: likewise no `cron:` at master — the reaping function is simply
  unscheduled while the parked pile stands at ≥4,621. Whether a reaper should
  be re-armed is a lane/owner decision, recorded here as an open gap.
- `actions-run-watcher.yml` — **REMOVED from the watch**: no cron trigger
  (enumeration false positive; the file's text mentions scheduling).
- `agent-runtime-stall-watch.yml`, `merge-promotion-queue-v3.yml` — same:
  no cron trigger, dispatch/workflow_run-driven, both active 11-02. Removed.
- `traffic-feed-collect.yml` + `context-relationship-reconcile.yml` — stand as
  candidates above; both resolve at their next nominal firings.

Remaining enumeration: 79 of 99 files unextracted; extraction continues next
pass. Event-masked schedule legs (NOT_ESTABLISHED rows) need schedule-event
history queries beyond the last-5 window — method noted for the next pass.

### Watch pass 2 — 2026-11-02T22:05Z: leg-level verdicts via schedule-event history

Method note (corrects pass 1's plan): code-search fragments are NOT available
through the PAT helper (its Accept header lacks the text-match media type, so
`text_matches` come back empty — extraction via search yields nothing and is
retired as a route). Verdicts instead come from per-workflow
`runs?event=schedule` history — exact and cheap. Cron-expression extraction for
the remaining files stays contents-read work.

**Rule v3:** observed delivery lag for daily crons is 6.4–9.9 h — that is the
norm, not the exception — so the +12 h grace stands. New leg-level class:
a schedule leg with **0 deliveries ever** and ≥1 nominal date passed is
**STARVED (leg)**, independent of the workflow staying alive on other triggers.

| Workflow | Schedule runs EVER | Last schedule delivery | Verdict (supersedes pass 1) |
|---|---|---|---|
| traffic-feed-collect.yml | **0** | never | **STARVED (leg) CONFIRMED** |
| telemetry-ingest.yml | **0** | never | **STARVED (leg)** — workflow alive on push; its Wed 07:23Z leg has never delivered |
| delphi-ledger-feed-collect.yml | **0** | never | **STARVED (leg)** — alive on workflow_run; next nominal Tue 11-03 06:47Z |
| challenge-countdowns-refresh.yml | **0** | never | CANDIDATE — today's 16:06Z firing undelivered at 22:05Z, inside grace (expires 11-03T04:06Z) |
| context-relationship-reconcile.yml | 11 | 2026-11-02T15:52Z ✓ success | **RESOLVED: FIRING-DELAYED-EXTREME** (+9.6 h lag; candidate cleared) |
| repo-tracking-collect.yml | 2 | 2026-11-02T17:13Z ✓ | FIRING-DELAYED-EXTREME (+9.8 h), thin history |
| operator-matrix-generate.yml | 5 | 2026-11-02T16:33Z ✓ | FIRING-DELAYED-EXTREME (+9.9 h) |
| surface-feeds-collect.yml | 1 | 2026-10-28T13:32Z ✓ | FIRING, thin (1 delivery ever); next due Wed 11-04 |
| quota-dispatch-tree.yml | 53 | 2026-11-02T20:12Z ✓ | FIRING-SPARSE (stands) |
| observer-poller-scheduled.yml | 42 | 2026-11-02T18:47Z ✓ | FIRING-SPARSE (stands) |

Repo-wide context: the newest 100 schedule-event runs span 2026-11-01T13:26Z →
11-02T21:56Z across **45 distinct workflows** — schedule delivery works as a
system; the starved legs above are per-workflow, not a platform outage. (The
repo-wide schedule `total_count` reads 2,500 = the §1 saturation cap; recorded
as SATURATED, not a count.)

Open after pass 2: countdowns candidate resolves 11-03T04:06Z · delphi/traffic
Tue firings 11-03 · cron extraction for the un-baselined remainder (contents
reads) · the 45-workflow firing set vs cron-file set difference = the full
silent-leg census, computable once extraction completes.

## §3 Next passes (this seat)

1. Nominal-cron extraction for all 99 enumerated files → per-workflow expected
   interval column; stale candidates resolved to STARVED or cleared.
2. Deploy-plane ops board (§ approval ③) as §4 of this register: Pages · Vercel ·
   Fly · Koyeb {last deploy · mechanism · failure class · blocking item}.
3. CI census repeated on state-change suspicion or weekly-class cadence,
   appended as new rows.

## §4 Deploy-plane ops board (census 2026-11-02T13:45Z, PAT firsthand)

| Plane | Mechanism (workflow) | State | Last deploy evidence | Failure class / blocking item |
|---|---|---|---|---|
| GitHub Pages (/tribute/) | `tribute-dashboard-deploy.yml` (38 runs; predecessor `help-wanted-dashboard-deploy.yml` deleted in the rename, 1,266 runs) | **OPERATIONAL, congested** | dispatch run PENDING 13:44Z; push runs 13:43Z ×2 both **cancelled** | Push-burst self-cancellation in hot queues (cancel/success/cancel tail on the predecessor's last runs, 10:52–10:55Z); standing remedy = manual dispatch — exercised as recently as this census |
| Vercel | `tribute-vercel-prod.yml` (17 runs) · `owner-records-vercel.yml` (5 runs) · `vercel-project-rename.yml` (2 runs) | **OPERATIONAL** | tribute prod dispatch **success 06:18Z** · owner-records final success 07:14Z (SSO-gated project live) · rename+domain-swap 2/2 success | Deploy rate-limit failures observed as non-gate PR-check failures (Stewardship merge census 2026-11-02); prior tribute-prod failures date to 2026-10-22 |
| Fly.io | `deploy-hindsight.yml` (1 run ever, 2026-09-28 success) · `fly-hindsight-config.yml` | **BLOCKED — card class** | config-apply run 41410355692 **FAILED 2026-11-02T08:04Z** ("trial has ended, please add a credit card") | ∅CC closed class: the on-file HindSight free-model config edit is UNAPPLIED; the Fly app serves its prior config. Unblock = Fly.io support-trial reset (owner request sent 2026-10-27, pending) ∨ card — neither in any lane's hands |
| Koyeb | `koyeb-hindsight-deploy.yml` (8 runs, all 2026-09) | **DORMANT-BLOCKED — credential** | last runs 2026-09-30: failure ×2 + cancelled; ∅ runs since | **KOYEB_API_TOKEN absent** (owner provisioning item, GATES-REGISTER DECISION-GATE class). This is the live HindSight retain target; its redeploy with the on-file :free config is the armed unblock for the ~10-day free fill (population still 0/388) |

Board discipline: state flips only on run evidence (a deploy run's conclusion),
not on lane report. Pages congestion and the §1 parked state are the same queue
phenomenon seen from two planes — a Pages deploy that matters rides dispatch,
never push.
