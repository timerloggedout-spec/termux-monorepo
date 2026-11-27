# Rhythmic Systems — Temporal Intelligence and Conductor RFP

**Status:** implementation specification and experiment proposal  
**Authority:** dependency-phase engine, Ballet Coordinator policy, QUE lifecycle, specialist adapters, ATES receipts, and operator promotion controls.

## Architecture

Temporal Intelligence contributes assignment-window semantics, collector cadence, wake policy, and evidence interpretation over the existing control plane.

| Owner | Contract | Authority |
|---|---|---|
| Dependency-phase engine | READY_AT, NOT_BEFORE, dependency barriers | canonical readiness and claims |
| Ballet Coordinator | WAVE, PHASE, WINDOW, EXPECTED_DURATION, CONCURRENCY | deterministic wave planning |
| QUE | OPEN, CLOSE, DEFER, EXPIRE, QUEUE_WAIT | admission, queue, claims |
| WAIT to WATCH | WAIT_UNTIL, WAKE_ON, RECHECK_AT | event/predicate/deadline observation |
| QUE collector | QUEUED, STARTED, COMPLETED, CANCELLED, VANISHED | lifecycle facts |
| ATES | actual start, finish, outcome, provenance, digest | evidence record |
| DoE / Observatory | timing treatments and measured effects | experiment evaluation |
| Conductor | cue sheets and dispatch intent | planning output through existing Manager and adapters |

The phase DAG remains canonical for readiness. Ballet plans waves. QUE owns admission and claims. WAIT to WATCH observes independent work and collector conditions. ATES records outcomes. Temporal Intelligence composes these contracts while preserving existing scheduling, queue, claim, and evidence authority.

## Temporal vocabulary

- BEAT: expected assignment, collection, or readiness boundary.
- OFFBEAT: valid work event displaced from its nominal boundary.
- ASYNC: start work asynchronously while retaining task identity and completion reference.
- WAIT: suspend observation until event, predicate, deadline, or cancellation.
- COLLECT: reconcile completed, pending, late, failed, cancelled, and missing assignments.
- OPEN_LENGTH: admissible execution/collection window duration.
- EXPECTED_DURATION: predicted execution duration or completion interval.
- ACTUAL: observed start, finish, duration, result, and evidence.
- DRIFT: ACTUAL minus EXPECTED.
- PHASE: temporal position relative to assignment or collector cycle.
- SYNC: satisfy dependency barrier, quorum, or readiness predicate.
- POLYRHYTHM: concurrent collectors with distinct periods.
- POLYMETER: distinct timing grids over shared work.

Early and late displacement inside an open window remain valid observations. Window expiry and expected-duration overrun are independent conditions. A task may be late and healthy, on-beat and over-duration, or expired with an overrun.

## Assignment and collector lifecycle

An assignment records nominal_at, opens_at, closes_at, and expected_duration. OPEN_LENGTH equals closes_at minus opens_at. The collector records observed start and finish timestamps and derives phase offset and duration drift.

| Condition | Classification | Meaning |
|---|---|---|
| start before nominal, inside window | OFF_BEAT_EARLY | valid phase displacement |
| start after nominal, inside window | OFF_BEAT_LATE | valid phase displacement |
| start outside window | WINDOW_EXPIRED | window breach |
| actual duration exceeds expected | DURATION_OVERRUN | independent performance variance |
| QUE COMPLETED | COMPLETED_OBSERVED | lifecycle fact; ATES validation remains separate |
| QUE VANISHED | RECONCILE_MISSING | missing observation requiring reconciliation |

Collector wake selection chooses the earliest applicable boundary among event readiness, expected completion, window close, and maximum wait. Each collector retains its own period and phase, enabling polyrhythmic cadence through independent tick origins.

## Jazz division taxonomy

Jazz is a division with orthogonal axes for style, meter, rhythmic treatment, polyrhythm, polymeter, polyphonic roles, performance context, and capability state. Style remains independent of meter and rhythmic treatment. Polyphonic roles may carry distinct phase, accent, and cycle definitions.

The machine-readable taxonomy is JAZZ-DIVISION-TAXONOMY.json. Profiles cover swing, shuffle, syncopation, off-beat accents, anticipation, displaced downbeats, rubato, metric modulation, Euclidean patterns, 2:3 and 3:2 polyrhythm, independent meters, and simultaneous instrumental roles. Capability values distinguish available, experimental, unsupported, and runtime-validation-required features.

## Ballet semantic crosswalk

Ballet is polysemous. Typed concepts preserve domain boundaries:

| Concept | Domain | Meaning |
|---|---|---|
| performing-arts.ballet | performing arts | dance art form and performance tradition |
| performing-arts.choreography | performing arts | composition and arrangement of movement |
| software-orchestration.ballet-coordinator | software orchestration | dependency-wave planner and orchestration policy |
| pit-crew-doe.PC-SEED-019 | architecture tournament | Ballet architecture treatment |
| pit-crew-doe.PC-SEED-009 | architecture tournament | Orchestra/Conductor architecture treatment |

Typed relations include uses_compositional_method, analogy, architecture_treatment_reference, part_of, broader_than, narrower_than, and evidence-backed equivalent_to. Ballet Coordinator uses choreography as analogy and planning vocabulary; the software-orchestration concept remains distinct from the performing-arts concept. Orchestra and Ballet remain separate architecture treatments.

## Conductor placement experiment

Evaluate all three placements independently:
1. Manager policy: Conductor produces policy-level cue sheets for Manager approval.
2. Temporal Intelligence: Conductor produces phase-aware cue sheets and temporal annotations.
3. Agent-team orchestration: Conductor composes team-level intent through the existing orchestration contract.

Keep architecture seed, software placement, wave strategy, and temporal treatment as independent design axes. Compare PC-SEED-009 and PC-SEED-019 as architecture treatments. Compare sequential, parallel, and adaptive wave strategies separately. Compare event-driven, periodic, and hybrid wait policies separately. Record timing, integration correctness, cost, coordination overhead, and censoring in canonical experiment records.

Conductor emits cue sheets and dispatch intent. Manager, phase engine, QUE, specialist adapters, write leases, digest checks, and ATES retain authority. Cue sheets carry phase, expected duration, open length, wake conditions, dependency barriers, and evidence references.

## Music as Code

Music as Code operates both as an independent creative/experimental subsystem and as a mixed-mode stimulus source. Independent mode evaluates composition, rhythmic structure, exact ratios, and render/export adapters. Mixed mode supplies controlled rhythmic stimuli to temporal-policy experiments. Production dispatch authority stays with the existing control plane.

The shared notation registry carries canonical notation and typed domain mappings. Music-specific encodings remain domain projections. Exact rational ratios remain distinct from musical meter, performance feel, and scheduler cadence.

## DoE registration

The DoE questions matrix v2 adds:
- Dimension 41, collector timing policy: event-driven, periodic, hybrid; evidence includes wake reason, period, phase, and observed wake.
- Dimension 42, assignment phase treatment: on-beat, early-within-window, late-within-window, window-expiry control; evidence includes nominal/open/close/start/finish timestamps and expected duration.

Use the existing experiment record schema and DoE family. Record baseline and candidate SHAs, treatment identity, status, timestamps, metrics, provenance, confidence, and evidence references. Preserve failed, censored, skipped, and inconclusive arms. Register a distinct temporal campaign while keeping the existing Ballet 3x3 strategy/capacity campaign intact.

## What I would investigate beyond the obvious

- Phase aliasing: identify collectors whose periods create systematic blind spots or repeated synchronization collisions.
- Window fairness: measure whether open-length policies favor short tasks, particular providers, or selected cohorts.
- Queue interference: separate queue wait, execution duration, collector latency, and evidence-ingestion latency.
- Wake amplification: quantify event fan-out, duplicate wakeups, polling load, and stale predicate checks.
- Temporal observability: preserve clock source, timezone, monotonic-clock correlation, timestamp precision, and clock-skew uncertainty.
- Partial completion: model quorum, stragglers, cancellation propagation, late evidence, and recovery windows.
- Adaptive stability: test timing-policy oscillation under changing queue depth or quota replenishment.
- Rhythmic aliasing in Music as Code: measure whether generated stimulus patterns synchronize with collector periods and bias results.
- Polyphonic workload mapping: compare independent role cadences and write-set overlap under concurrent work.
- Human oversight cost: measure review-window fit, intervention timing, and operator context-switch cost.

## Qualification

1. Validate deterministic timing primitives and timezone-aware timestamp contracts.
2. Run offline unit and schema tests.
3. Replay QUE lifecycle fixtures and canonical ATES receipts.
4. Run preregistered temporal DoE arms against fixed cohorts.
5. Validate cue-sheet intent through Manager and existing adapters in shadow mode.
6. Promote a treatment after correctness, integration, safety, cost, and operator approval gates pass.

Implementation: deepcli/deepcli/observatory/temporal.py. The module classifies timing and calculates collector wake boundaries while existing control planes retain dispatch and scheduling authority.
