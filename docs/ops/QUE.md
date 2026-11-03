# QUE — the fleet's queue system

**Name of record: QUE** (owner's spelling, 2026-11-03). QUE is a
first-class named system: the fleet's GitHub Actions queue —
admission, ordering, hygiene, observability, and spawn discipline
for every run the fleet creates. Lead: optimizations-assurance.
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

## Tranche plan

| Tranche | Scope | Acceptance |
|---|---|---|
| **0 — Live unblock** (2026-11-03, DONE) | stale-class cancels · dependency-ordered starts · timers question answered | 350 tier-4 cancels, 0 gates/machines · D1's five: cuts+proof+sync complete, leaf in the hold window · board PR #4621 + tiers PR #4622 open |
| **1 — Observability complete** | board merged + served · feed v2 (position + per-tier waits) · nav registration (canon pass) | board live on the served site, ages ticking · feed refresh ≤10m sustained a day |
| **2 — Hygiene automated** | reaper workflow live (single-flight, episodic, receipts to the feed record) · wedged-ancient playbook (disable/re-enable) executed once | 7 days of reap receipts · zero manual cancel sessions across one natural flood |
| **3 — Admission generalized** | guard projects queue at dispatch · tier-4 fail-soft deferral live · Cadence custody handoff | synthetic storm drill: burst admitted ≤ budget while tier 1–3 waits stay flat (feed-measured) |
| **4 — Spawn discipline** | top-5 follower families: trigger-level conditions + single-flight groups + stamped budgets | drain mix real-work share ≥50% sustained a week · family spawn/hr inside budget |
| **5 — Ordering encoded** | per-entry chain declarations consumed by admission (chain heads gate downstream) | a D1-class chain replayed in a drill with zero inversions among stamped runs |

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
