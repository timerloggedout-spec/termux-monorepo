# QUE — the fleet's queue system

**Name of record: QUE** (owner's spelling, 2026-11-03). QUE is a
first-class named system: the fleet's GitHub Actions queue —
admission, ordering, hygiene, observability, and spawn discipline
for every run the fleet creates — and the measurement plane the
fleet's efficiency systems read from (see *The measurement
plane* below). Lead: optimizations-assurance.
Custody: Cadence (governor) · DevOps (dispatch reliability) ·
Viz (boards).

Born of the 2026-11-03 flood, measured firsthand: spawn ≈ drain
at ≥1,000 runs/hr · last-100 completions **90 skipped + 10
cancelled, 0 real work** · gate and follower waits identical
(37m ≈ 36m, tier-blind) with live inversions · a run-list index
that serves phantom statuses at churn · 3 wedged runs listed as
queued since Oct 1–7. The queue was weather. QUE makes it a
system, by construction, not by escalation.

## The five components

### ① ADMISSION — project the queue before adding to it

Pattern of record: the PAT helper's flow governor (landed
2026-11-03) projects aggregate trailing burn and defers BEFORE
the wall. QUE generalizes it: dispatch admission reads the
queue-state feed + the tier table, projects depth and expected
wait, and **defers fail-soft** — a deferred dispatch is stamped
`deferred-by-tier` with its projection, never silently dropped.
Custody: Cadence.

### ② ORDERING — drains execute dependency order

Tiers (`docs/ops/QUEUE-DEPENDENCY-TIERS.md` · PR #4622):
1 infra/gates → 2 release machinery → 3 builds/proofs →
4 collectors. Per-entry chains are honored as DECLARED shapes —
exemplar, D1's: *gate/suite green → 3 surface cuts (parallel) →
release of record → v1.0.0 assembly → snapshot; the proof
independent; countdowns a leaf, last.* GitHub has no cross-
workflow DAG and no reorder API (stated, never asserted around);
ordering is expressed through admission stamps and chain heads:
a downstream dispatch does not admit before its upstream
completes.

### ③ HYGIENE — stale classes reaped automatically, with receipts

The reaped classes: superseded heads · duplicate fan-out spawns
· zombie in-progress (incl. phantom-index entries — direct GET
is the only truth at churn) · wedged ancients. **The standing
queue-reaper re-arming question is SETTLED BY THE OWNER'S
2026-11-03 MANDATE: the reaper is a QUE component, re-armed by
this document's authority, not by future escalation.** It runs
episodically (QAC-008 cadence, single-flight) and every sweep
posts receipts — counts by class — to the queue feed's record.
Manual cancel sessions (2026-11-03: 350, all tier-4) are the
bootstrap, not the steady state.

### ④ OBSERVABILITY — queue age + position on the visual web

Owner's contract: timers computed in-browser from `created_at`
instants, countdowns-style; a board that can't show queue age
is unfinished. Landed as PR #4621: `queue.html` + the
`queue-state-feed/v1` collector (queued count · in-progress ·
oldest wait ticking · feed age ticking · drain mix · pinned
critical-path runs · wedged ancients named). Position (a run's
rank in its repo queue) joins in feed v2. Custody: Viz.

### ⑤ SPAWN DISCIPLINE — storms are a defect class with a budget

Fan-out at the head is not weather. Every follower family
carries a **named spawn budget** (spawns/hr); exceeding it is a
defect with an issue, like any other. The mechanisms: gate
conditions move INTO triggers (paths/branches/actors) so
skipped runs never spawn · single-flight concurrency per
family (cancel-in-progress for superseded evidence runs) ·
sampled/aggregated follower triggers instead of per-completion
chains. Health metric, read off the board: the drain mix —
real work (success+failure) should be the majority of
completions; on 2026-11-03 it was **0%**.

## The measurement plane (owner amendment, 2026-11-03)

QUE is not only a control system; it is the fleet's
**measurement plane for queue behavior** — the substrate the
efficiency metrics, DoE, 3L0, and MoneyBall read from.

**Events.** Every queue transition emits a receipted event:

```
{transition: enqueued | admitted | deferred | started |
             cancelled | completed,
 workflow, dependency_tier, lane/seat attribution,
 created_at, started_at, cancel_class (when cancelled),
 run_id, repo}
```

**Store.** Append-only, on the lane-events pattern (Neon
lane-events or a QUE sibling table); **store of record = repo
snapshots** per the podium precedent — the database is the
working copy, the repo snapshot is the citable one.

**Consumers (named, with their contracts):**

- **Efficiency metrics — Quota + Cadence seats.** Wait-time
  distributions, idle-through, and storm attribution become
  continuous metrics read off the plane, not anecdotes
  reconstructed during an escalation.
- **DoE.** Admission and ordering policies are experiments:
  the plane is where their outcomes are measured (a policy
  change ships with its before/after read, or it didn't
  happen).
- **3L0.** Queue efficiency is a weighting signal — lanes and
  routes that respect the queue weigh differently from lanes
  that storm it.
- **MoneyBall.** Queue behavior is book material: drain
  outcomes (will this run start within N minutes? will this
  family's storm clear by the freeze?) are forecastable
  subjects with receipted resolutions.

**Why the layer is load-bearing:** QUE's own acceptance is
only testable off the plane. Drain-order compliance,
cancel-class rates, and queue-age percentiles are READ from
recorded events, never asserted from memory — the same
evidence discipline the queue flood violated (phantom list
statuses) and the plane exists to make impossible.

## Tranche plan

| Tranche | Scope | Acceptance |
|---|---|---|
| **0 — Live unblock** (2026-11-03, DONE) | stale-class cancels · dependency-ordered starts · timers question answered | 350 tier-4 cancels, 0 gates/machines · D1's five: cuts+proof+sync complete, leaf in the hold window · board PR #4621 + tiers PR #4622 open |
| **1 — Measurement plane** | transition-event emitter (collector-side, off the Actions API) · append-only store on the lane-events pattern · repo snapshots as store of record · consumer contracts live for Quota/Cadence + DoE | a full day of transitions recorded with ≤1% gaps vs the API census · wait-time percentiles + cancel-class rates published from the plane alone |
| **2 — Observability complete** | board merged + served · feed v2 (position + per-tier waits) · nav registration (canon pass) | board live on the served site, ages ticking · feed refresh ≤10m sustained a day |
| **3 — Hygiene automated** | reaper workflow live (single-flight, episodic, receipts to the feed record) · wedged-ancient playbook (disable/re-enable) executed once | 7 days of reap receipts · zero manual cancel sessions across one natural flood |
| **4 — Admission generalized** | guard projects queue at dispatch · tier-4 fail-soft deferral live · Cadence custody handoff | synthetic storm drill: burst admitted ≤ budget while tier 1–3 waits stay flat (plane-measured) |
| **5 — Spawn discipline** | top-5 follower families: trigger-level conditions + single-flight groups + stamped budgets | drain mix real-work share ≥50% sustained a week · family spawn/hr inside budget |
| **6 — Ordering encoded** | per-entry chain declarations consumed by admission (chain heads gate downstream) | a D1-class chain replayed in a drill with zero inversions among stamped runs |

**Guardrail:** D1's freeze work never waits on any tranche
beyond 0. QUE improves the road; it never parks the traffic.

## Platform truths QUE is built on

- No queue-reorder or priority API exists on GitHub.
- The run-LIST index serves phantom statuses at churn; direct
  GETs and job records are the truth (the PAT helper drops dict
  params on GET — embed query strings in the path).
- Both fleet repos are public; billing ceilings are not the
  constraint. The constraint is the shared account scheduler
  working a backlog — which is why QUE governs what ENTERS.

## Priority window — D1 (owner, 2026-11-03 15:55 PT)

Until the D1 freeze (2026-11-04 23:59 PT), the D1 chain
(slate iterations · releases · snapshot · deploys on its
path) holds **absolute priority on runner supply** — yields are automatic, without being asked twice ('Race to finish', owner 2026-11-03). Admission treats
chain runs as the highest claim; sweeps take non-chain
tier-3/4 work first; other lanes yield per the hold/sweep
doctrine. The window is encoded in
`ops/quota/dispatch-tiers.json` (`priority_window`) and
expires at the freeze — it is a window, not a standing
reorder. Cadence holds the guard-threshold copy.

## Governor deferrals — probe, never park (fleet rule, owner 2026-11-03 17:02 PT)

**"A deferral is a state to probe, not a timer to serve."**

The PAT flow governor's deferral is a PROJECTION (trailing-burn
extrapolation), and projections decay as burn drops: the stated
reset is a ceiling estimate, not a schedule. Proven 2026-11-03:
three seats parked on a projected 17:20 PT reset; a probe at the
owner's order at 17:01 PT found the deferral already cleared,
and the submission-critical verify completed in minutes. The
parking was the waste; the probe was the fix.

The rule, binding on every seat holding work behind a governor
deferral:

1. **Probe on a bounded cadence.** A probe = ONE governor-
   respecting call (the cheapest call that tests the state, e.g.
   the rate-limit read or the held call itself at low priority).
   Cadence: no tighter than the queue-census rhythm (minutes,
   not seconds); a probe never becomes a poll loop.
2. **Report clearance state, never a countdown.** The seat's
   status vocabulary is {deferred · probing · cleared} with the
   last probe's evidence — never "waiting until HH:MM" as a
   plan. A stated reset time may be quoted as the projection's
   ceiling, labelled as such.
3. **Pre-stage behind the deferral.** Work that can advance
   without the budget (local builds, verification prep,
   staged one-shots keyed on STATE, not on the clock) proceeds
   during the deferral; the held legs fire on clearance without
   latency. A parked seat with unstaged follow-on work is the
   defect this rule exists to prevent.
4. **Courtesy holds carry probe-and-release.** A seat that
   pauses its own consumers to clear budget for a priority
   verify releases them on a clearance PROBE, not a fixed
   sleep, wherever the paused work is state-keyed.

Governor-side improvements (projection labelling · clearance
estimates · priority honoring inside the governor) are Cadence's
delegated line; this section governs SEAT behavior only.
Escalation + findings of record: owner escalation via the D1
seat, 2026-11-03 17:02 PT; first application = the D1 v1.0.0
verify chain (PR #4748), same day.
