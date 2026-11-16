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

## §5 Default-token exposure register (finding via main, 2026-11-03; census this seat)

**The class:** the default `GITHUB_TOKEN` draws on ONE shared installation
bucket (1,000 requests/h for this repo) no matter which workflow spends it.
Exhaustion presents as `API rate limit exceeded for installation` — and jobs
can die on it **silently** (no failing surface anywhere). Precedents of record:
the 2026-10-22 fleet-wide exhaustion diagnosis (checks annotating the limit
from 07:55Z, every unrelated PR red) and the 2026-11-01 apk-xref belt deaths
(4× HTTP 403 on the shared bucket; fixed by PR #2992's SEC-03 Swarm mint).

**Worked example of the fix (verified at master by this seat):**
`dispatch-watchdog.yml` — its acceptance runs 403'd silently until its owner
built a self-diagnosis loop and moved the workflow onto the Termux Fleet Swarm
App's own bucket (PR #4167 chain, merged). At master the file mints via
`actions/create-github-app-token` with `TERMUX_FLEET_SWARM_APP_ID` /
`TERMUX_FLEET_SWARM_PRIVATE_KEY` (lines 38–41) and its API step consumes
`steps.swarm.outputs.token` (line 45). One residual default-token step remains
at line 57 — named here as found; whether it is deliberate (diagnosis leg) or
leftover is the owning lane's call. Fix pattern of record = SEC-03:
mint-before-checkout under `TERMUX_FLEET_<ROLE>_*`, steps consume the minted
token; each fleet App carries its own 5,000/h bucket.

**Census 2026-11-03T11:04Z (code search over `.github/workflows`, 311
workflows):** explicit default-token references (`secrets.GITHUB_TOKEN` ∨
`github.token`) in **140 files** · app-token minting (`create-github-app-token`)
in **23 files** · mixed (both) **10** · **default-only = 130 files**:

ace-watch · action-effectiveness-ledger · actions-queue-reaper · actions-run-watcher · agent-continuous-ops · agent-ecc-tools-ops · agent-feedback-linear-sync · agent-runtime-stall-watch · agent-throughput-evidence · agentic-repository-operations-report.lock · apk-release-finalize · apk-release · apk-xref-intake · audit-cycle · automation-docs-continuous-refresh · cadence-lead-lag · cadence-provider-onboarding · cellcog-engineering-health · cellcog-review · cert-coderoad-image · challenge-countdowns-feed-collect · challenge-countdowns-refresh · challenge-osint-watch · comment-quality-sweep · commit-diff-watcher · context-relationship-audit · context-relationship-backfill-watcher · context-relationship-backfill · context-relationship-publish · context-relationship-reconcile · continuous-evaluation · credential-family-probe · deepcli-agent-bridge · deepseek-ci · deepseek-secret-probe · deepseek-termux-agent · delphi-gate · delphi-generate · delphi-intake · delphi-participant-cycle · delphi-signal-bridge · delphi-signal · delphi-tribute-ingest · dependency-phase-dispatch · dependency-phase-evaluate · dependency-phase-project-sync · dispatch-tree-feed-collect · docs-branch-index · doe-cb1-acceptance · doe-live1-audit · doe-live3-autodispatch · doe-nc1-eval · doe-phrase-dispatch · fork-sync-audit · g07-profile-watch · gemini-after-peers · gemini-invoke · gemini-review · gemini-triage · github-telemetry-snapshot · gitlab-governed-reconciliation · hark-enqueue · historical-evaluation-correlation · integration-mesh-poll · issue-lifecycle-triage · issue-observatory · lane-events-recorder · linguist-panel-feed-collect · merge-promotion-queue-v2 · merge-promotion-queue-v3 · merge-promotion-queue · merge-promotion-steward · ml-pr-lane-classify · observer-poller-scheduled · operator-matrix-generate · operator-variable-provision · operator-wake · ops-gitlink-lego-fork · ops-lane-matrix-sweep · oracle-panel-feed-collect · ox-alpha-smoke · peer-review-orchestrator · phantom-secrets-audit · pin-cor-ae-submodules · platform201-support-response-check · pr-change-effectiveness-ledger · pr-evidence-evaluation · pr-scope-guard · project-task-dispatch · proposals-feed-collect · provider-batch · provider-recon-compound · publish-wiki · quota-allocation-planner · re-taxonomy-intake · readme-extractor-image · recon-intel-discovery · recon-intel-reconcile · reconcile-repository-surface · refTemplates-eval · referral-pool-watch · referral-rotation · registration-monikers · repository-observatory · research-intake · rindig-provenance-audit · rindig-source-inventory · shared-observer-poller · she-skill-clobber-heal · surface-feeds-collect · sweep-accountability · tailscale-bridge-probe · target-intake · team-mvt · telemetry-ingest · termux-bridge-connect · tribute-audit-staleness · tribute-dashboard-deploy · tribute-diff-gate · tribute-execute · tribute-followup · tribute-llm-assist · tribute-participation · tribute-rerequest · tribute-scout · tribute-status-refresh · tribute-system1 · v2-gitlab-probe · vercel-quota-probe (all `.yml`)

Method caveats, stated plainly: (a) this is a search-INDEX census and the index
lags — it classifies `dispatch-watchdog.yml` itself as default-only although
the file at master mints (verified above); counts are the exposure surface,
file-level truth is per-file reads. (b) The census covers EXPLICIT references;
workflows with no token reference still run checkout on the default token —
REST-bucket exposure concentrates in API-calling steps, and a step-level audit
is the next sweep refinement.

**Cross-reference to §2 (co-occurrence, causation NOT claimed):** eleven of the
watch's critical subset ride the default bucket exclusively — telemetry-ingest
∧ delphi-ledger-feed-collect (both STARVED-leg) · dispatch-tree-feed-collect ·
operator-matrix-generate · context-relationship-reconcile · observer-poller-
scheduled · github-telemetry-snapshot · ml-pr-lane-classify · registration-
monikers · surface-feeds-collect · issue-lifecycle-triage ·
challenge-countdowns-refresh. Schedule *delivery* is GitHub-side and is not
explained by this; what the bucket governs is whether their in-job API calls
succeed once a run starts — the watchdog's silent-403 mode is the failure to
watch for in these lanes' run logs.

### §5.1 Classification of the 130 — OPTIMIZE / MIGRATE / BOTH / NEITHER (2026-11-03)

Owner question via main, answered jointly with the AppID migration lane
(coordination of record, 2026-11-03): per consumer class, legitimacy-tested —
(1) volume maps to real work product? (2) self-triggering cascade share vs
external demand? (3) re-fetch where a feed/artifact already carries the data?
Migration never legitimizes waste: amplified classes optimize first.

**Volume evidence:** all-time run totals per workflow (PAT, 2026-11-03).
Thirteen files read exactly 40,000 = the per-workflow runs `total_count`
SATURATION cap (recorded as ≥40,000, not counts). Run volume ≠ API calls
(per-run intensity = MIG-11, open) — volume is the ranking evidence, the
legitimacy tests are the verdict evidence.

**Corrections folded in (per-file reads beat the §5 index census):**
`delphi-ledger-feed-collect` already Swarm-mints (it was in §5's MIXED set;
§5's cross-reference line implying it rides default-only was this seat's
error, corrected here — credit: migration lane's firsthand read).
`ml-pr-lane-classify` (OPERATOR PAT primary) and `registration-monikers`
(multi-bucket ARCHWIZ/OPERATOR/default) are NOT default-only consumers —
class K below. True default-only population = 128 + these 2 corrected out.

**TOP MOVERS (run volume):** the saturated-13 (≥40,000): action-effectiveness-
ledger · agent-ecc-tools-ops · agent-throughput-evidence · audit-cycle ·
cellcog-review · context-relationship-audit · deepseek-ci · deepseek-termux-
agent · lane-events-recorder · ox-alpha-smoke · peer-review-orchestrator ·
pr-evidence-evaluation · sweep-accountability — then actions-run-watcher
37,996 · delphi-gate 32,234 · operator-variable-provision 27,629 ·
operator-wake 27,586 · delphi-intake 27,549 · phantom-secrets-audit 26,057 ·
research-intake 20,659 · delphi-signal-bridge 16,918 · recon-intel-discovery
16,036 · pr-change-effectiveness-ledger 13,938 · pr-scope-guard 12,811 ·
merge-promotion-queue-v3 6,537. The head of the table is the fleet's own
meta-machinery — recorders, Delphi, operator machinery — not external-demand
surfaces.

| Class | n | Verdict | Basis (legitimacy tests) |
|---|---|---|---|
| A — per-run recorders / mesh-records-itself | 19 | **OPTIMIZE FIRST; migration refused until bounded** | Volume ≈ fleet run volume itself: they fire BECAUSE other workflows ran (cascade ~total). Products = ledgers/evidence; some have named consumers (lane-events → Neon), several are consumer-thin mills (migration lane: migrate only with a named consumer). Fix = event-payload consumption, sampling, single-writer batching (telemetry-ingest pattern). A bigger bucket here legitimizes amplification. |
| B — dispatch / promotion / operator machinery | 13 | **BOTH** | Real work product (fleet throughput). OPTIMIZE leg: THREE merge-promotion generations coexist (v1+v2+v3) — retire v1/v2 (archive rules) and consolidate; operator-wake/provision (27.6k runs each) get a per-run call audit before any move. MIGRATE leg: v3 + dispatch family = Swarm fit, READY (SEC-03 pair exists); operator-matrix-generate + quota-allocation-planner = Publisher fit, DESIGN-GATED. dispatch-watchdog = the §5 worked example, already migrated — its residual line-57 default step is its only default-bucket leg left. |
| C — Delphi family | 7 | **BOTH, split by leg** | Product = DoE experiment/ledger records (real). participant-cycle = self-triggering BY DESIGN (cycle bounds = the optimization); gate (32k) = external PR/check demand → Gate fit is identity-graduation only (MIG-09), PROVISIONING-GATED and narrow; collector legs split to Collector reads. |
| D — PR review / evidence machinery | 8 | **BOTH** | External demand (real PRs) ∧ starved in bursts. MIGRATE (provisioning-gated): review-shaped writes → Reviewer (orchestrator's EVIDENCE leg only per MIG-08; operator steps stay identity-bound); pr-scope-guard = pure check poster → Gate. OPTIMIZE leg: evidence re-fetch — reviewer-metrics feed already carries much of it. peer-review-orchestrator is a top mover (≥40k). |
| E — feed collectors / pollers / snapshots | 20 | **OPTIMIZE primary; BOTH for the priority wave** | Products = feeds consumed fleet-wide (real), but the class disease is (3): re-fetching what landed feeds already carry + cadence excess. Priority wave (§2-critical ∩ clean fit, agreed with migration lane): telemetry-ingest (Collector reads / Publisher write-leg split) · dispatch-tree-feed-collect · surface-feeds-collect · github-telemetry-snapshot · observer-poller-scheduled (cadence frozen in the same PR) · challenge-countdowns-refresh. repository-observatory's /user legs = NOT-MIGRATABLE (MIG-01) — stays. recon-intel-discovery (16k) = class top mover: cadence/dedup first. |
| F — provider invocation | 8 | **NEITHER (bucket)** | Providers key on requester identity (migration lane) — a bucket move does not apply; their GitHub-API draw is incidental to provider spend. Exception flagged: ox-alpha-smoke ≥40,000 runs for a SMOKE = cadence amplification suspect → OPTIMIZE its cadence. deepseek-ci / deepseek-termux-agent (≥40k each) = per-PR provider CI; legitimacy rides the provider lanes' own accounting. |
| G — intakes / issue-admin services | 14 | **Split: MIGRATE (provisioning-gated) for the 403-evidenced writer; OPTIMIZE for the firehoses; NEITHER for the tail** | issue-lifecycle-triage = 403-evidenced (installation-403 failures, lane-log-verified) → Lifecycle fit, priority wave. research-intake (20,659) + phantom-secrets-audit (26,057) = volumes no intake/audit semantics justify → trigger-breadth/cadence OPTIMIZE first. hark-enqueue + tribute-followup/rerequest → Lifecycle fit when provisioned. apk-xref-intake = RE lane's belt-swap call, not this classification's. Episodic probes/admin = NEITHER. |
| H — build / image / deploy incidental | 15 | **NEITHER** | REST draw ≈ 0 (checkout + build + artifact mechanics) or episodic by design. apk-release family: migration already QUEUED on its own track (ApkRelease App, owner GO of record) — not counted here. tribute-dashboard-deploy's problem is queue congestion (§4), not the bucket. |
| I — context-relationship / backfill family | 5 | **BOTH, Stewardship-gated** | OPTIMIZE primary = Stewardship #3812's fresh-output isolation (ends the re-fetch); write legs = Publisher fit (DESIGN-GATED) and land with step 4, where this seat's day-2 ops begin. (context-relationship-audit sits in A by behavior.) |
| J — dormant / refused | 2 | **NEITHER now** | agent-continuous-ops: 622 lifetime, 0 runs/24 h, dormant since 2026-10-23 — REFUSE migration until rate-bounded by design (coordinated ruling); reactivation is Stewardship's call (its dormancy starves ATES receipts). actions-queue-reaper: ∅ cron (config gap, §2) — Swarm fit IF re-armed. |
| K — corrected OUT of default-only | 2 | **NEITHER (not consumers of this bucket)** | ml-pr-lane-classify = OPERATOR PAT primary; registration-monikers = multi-bucket. Index-census artifacts; per-file truth governs. |
| L — DoE evaluation family | 9 | **BOTH-lite** | Products = experiment records (real, DoE-owned). Dispatch legs (live3-autodispatch, phrase-dispatch) = Swarm fit READY when DoE wants them; audit/eval legs = OPTIMIZE cadence (they are measurement of measurement — class-A discipline at class-L scale). |
| M — Tribute ops family | 8 | **Split: MIGRATE-gated for two; OPTIMIZE for the chain** | tribute-diff-gate → Gate fit (provisioning-gated, pure check class); tribute-status-refresh → Publisher fit (design-gated); execute/scout/followup-chain volume = self-triggering campaign chains → OPTIMIZE chain amplification first. |

**Readiness tiers (migration lane feasibility, verified names-only):**
SEC-03 Actions pairs exist ONLY for {Collector · Swarm · CrossReference}
⇒ Swarm/Collector fits = READY · Gate/Reviewer/Lifecycle fits =
PROVISIONING-GATED (owner sealed-box act; AppID lane prepares) · Publisher
fits = DESIGN-GATED (no Actions pair by design, MIG-07; in-Actions mint
changes the publish-identity model). Permission bounds applied per manifest:
Gate = checks-write only · Lifecycle = issues-write only · Reviewer =
review-shaped writes only · Collector = read-only (any write step = SPLIT
migration) · Swarm = dispatch/actor shapes only, not a catch-all writer ·
new App = ∅ (every starved class fits an existing specialist).

**Identity warning (migration lane, carried into every MIGRATE verdict):**
GITHUB_TOKEN-authored events never trigger downstream workflows; App-authored
events DO. Migration can switch ON inert workflow_run chains — every migration
PR must name the chains it activates.

Class membership (partition of the §5 130, verified complete by construction):
A: action-effectiveness-ledger · agent-ecc-tools-ops · agent-throughput-evidence · audit-cycle · context-relationship-audit · lane-events-recorder · pr-change-effectiveness-ledger · sweep-accountability · actions-run-watcher · cadence-lead-lag · cellcog-engineering-health · commit-diff-watcher · referral-pool-watch · ace-watch · agent-runtime-stall-watch · agentic-repository-operations-report.lock · cadence-provider-onboarding · challenge-osint-watch · g07-profile-watch
B: operator-variable-provision · operator-wake · merge-promotion-queue · merge-promotion-queue-v2 · merge-promotion-queue-v3 · merge-promotion-steward · project-task-dispatch · dependency-phase-dispatch · dependency-phase-evaluate · dependency-phase-project-sync · operator-matrix-generate · quota-allocation-planner · dispatch-watchdog
C: delphi-gate · delphi-generate · delphi-intake · delphi-participant-cycle · delphi-signal · delphi-signal-bridge · delphi-tribute-ingest
D: peer-review-orchestrator · pr-evidence-evaluation · cellcog-review · pr-scope-guard · gemini-review · gemini-triage · gemini-after-peers · comment-quality-sweep
E: telemetry-ingest · dispatch-tree-feed-collect · surface-feeds-collect · observer-poller-scheduled · shared-observer-poller · github-telemetry-snapshot · integration-mesh-poll · recon-intel-discovery · recon-intel-reconcile · repository-observatory · rindig-provenance-audit · rindig-source-inventory · oracle-panel-feed-collect · proposals-feed-collect · linguist-panel-feed-collect · challenge-countdowns-feed-collect · challenge-countdowns-refresh · fork-sync-audit · provider-recon-compound · ops-lane-matrix-sweep
F: deepseek-ci · deepseek-termux-agent · deepseek-secret-probe · gemini-invoke · provider-batch · ox-alpha-smoke · deepcli-agent-bridge · termux-bridge-connect
G: issue-lifecycle-triage · research-intake · target-intake · issue-observatory · phantom-secrets-audit · credential-family-probe · re-taxonomy-intake · hark-enqueue · tribute-followup · tribute-rerequest · agent-feedback-linear-sync · platform201-support-response-check · apk-xref-intake · referral-rotation
H: cert-coderoad-image · readme-extractor-image · apk-release · apk-release-finalize · tribute-dashboard-deploy · publish-wiki · vercel-quota-probe · tailscale-bridge-probe · v2-gitlab-probe · gitlab-governed-reconciliation · pin-cor-ae-submodules · ops-gitlink-lego-fork · she-skill-clobber-heal · docs-branch-index · automation-docs-continuous-refresh
I: context-relationship-backfill · context-relationship-backfill-watcher · context-relationship-publish · context-relationship-reconcile · reconcile-repository-surface
J: agent-continuous-ops · actions-queue-reaper
K: ml-pr-lane-classify · registration-monikers
L: doe-cb1-acceptance · doe-live1-audit · doe-live3-autodispatch · doe-nc1-eval · doe-phrase-dispatch · continuous-evaluation · historical-evaluation-correlation · team-mvt · refTemplates-eval
M: tribute-execute · tribute-scout · tribute-status-refresh · tribute-system1 · tribute-participation · tribute-llm-assist · tribute-diff-gate · tribute-audit-staleness
