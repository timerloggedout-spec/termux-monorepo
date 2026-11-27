# Brain/CNS-Inspired Composer — Design

**Status:** implementation design for a follow-on layer to PR #5939  
**Parent:** `feat/rhythmic-temporal-intelligence` at `8ad6b73f8a3b695b3986bdfccb9cd341e5c1ca95`  
**Scope:** a deterministic intent-to-cue composition layer plus typed cognitive-system contracts.

## 1. Intent

Build a Composer that turns an explicit goal, task graph, context references, constraints, and timing assignments into a versioned, replayable score. The score compiles through the existing Ballet planner and Orchestra Conductor. It gives the system a coherent composition surface while preserving the existing control-plane owners.

The brain/CNS model is an architectural analogy: biological systems motivate separation of sensing, context, executive planning, action selection, prediction, feedback, and actuation. The implementation models software coordination; it makes no claim to reproduce biological cognition, consciousness, or clinical neuroscience.

## 2. Goals

- Provide a single deterministic entry point from typed intent to a cue sheet.
- Represent specialist cognitive roles as explicit, replaceable modules with narrow contracts.
- Preserve task identity, dependency barriers, timing windows, provenance, and success criteria end-to-end.
- Make every score inspectable, serializable, replayable, and attributable to a policy version.
- Accept feedback as evidence for future policy evaluation while keeping policy promotion explicit.
- Add a compact demonstration and regression tests for determinism, validation, and authority boundaries.

## 3. Non-goals and anti-goals

- Implement biological neural networks, medical models, brain simulation, or claims about consciousness.
- Replace Manager approval, dependency-phase readiness, Ballet wave planning, QUE admission/claims, specialist adapters, or ATES evidence validation.
- Dispatch work directly from Composer.
- Treat confidence, salience, predicted duration, or a musical metaphor as authorization.
- Silently mutate production policy from unverified feedback.
- Add an autonomous learning loop, model training, external service, database, or new runtime dependency.

## 4. Approaches

1. **Composer as a new scheduler.** Rejected: it duplicates readiness, claims, execution, and evidence authority already assigned to canonical systems.
2. **Composer as a thin document-only metaphor.** Rejected: it would provide vocabulary without a testable software contract.
3. **Composer as a deterministic score compiler over existing owners.** Selected: it accepts typed intent and context, delegates wave planning to Ballet, delegates cue formatting to Conductor, and emits a versioned score with decision trace and provenance. This adds a usable layer without creating a competing control plane.

## 5. Cognitive/CNS-inspired module map

| Module | Biological inspiration | Software responsibility | Authority boundary |
|---|---|---|---|
| Sensory Gateway | sensory receptors and afferent pathways | normalize external events into typed, source-attributed signals | observes; does not authorize |
| Thalamic Relay | thalamic routing | route signals to relevant specialist domains by declared type | routes only; Manager retains routing policy |
| Context Memory | hippocampal episodic/context functions | carry context references, prior observations, and provenance into a score | references canonical records; does not invent facts |
| Executive Planner | prefrontal executive functions | hold goal, constraints, success criteria, and planning policy | proposes; Manager approves |
| Salience Filter | salience/action-selection networks | annotate urgency and relevance for downstream admission | QUE retains priority/admission/claim authority |
| Temporal Predictor | cerebellar prediction and timing | attach expected duration, phase, and timing windows | Temporal Intelligence owns timing semantics |
| Coordinator | distributed cortical/subcortical coordination | compile dependency graph and specialist roles into a score | Ballet owns wave planning |
| Motor Interface | descending motor pathways | translate approved cues into adapter-facing dispatch intent | adapters execute; Composer never dispatches |
| Homeostasis Monitor | autonomic and homeostatic regulation | observe queue/cadence health, stale signals, and recovery conditions | WAIT→WATCH/collectors observe; QUE owns lifecycle |
| Error-Correction Loop | cerebellar error correction and feedback | compare expected/actual evidence and produce policy-evaluation inputs | ATES validates evidence; policy changes require explicit promotion |

The module names are typed software concepts. Biological names remain analogies and must be marked as such in docs, telemetry, and UI.

## 6. Runtime contract

### Inputs

- `ComposerIntent`: stable intent ID, objective, task records, success criteria, context references.
- `ComposerPolicy`: policy version, Conductor placement, Ballet strategy, optional parallel capacity.
- `assignments`: task-keyed temporal metadata already accepted by Conductor.

### Output

A JSON-compatible `composer.score.v1` object containing:
- stable intent and objective;
- policy version and selected placement;
- Ballet dependency plan;
- Conductor cue sheet;
- context references and success criteria;
- deterministic decision trace;
- explicit `dispatch_intent_only` authority marker.

### Determinism

For equivalent normalized inputs and the same policy version, score output is byte-stable under canonical JSON serialization. Task ordering is normalized by the Ballet planner; mappings are serialized with sorted keys. Timestamps and evidence references are caller-supplied inputs, never generated by Composer.

### Validation

Reject missing intent IDs/objectives, duplicate task IDs, unknown dependencies, invalid strategy/placement, missing assignments, missing cue metadata, invalid capacity, and empty success criteria. Reject non-JSON-compatible payloads rather than silently stringifying them.

### Feedback

Feedback is an observation envelope referencing a validated ATES receipt. Composer may package it for analysis, but it cannot validate a receipt, score an outcome independently of the canonical evidence plane, or promote a policy. A future policy update requires an experiment record, review, and explicit promotion.

## 7. Invariants

1. Dependency-phase engine owns readiness and dependency barriers.
2. Ballet owns deterministic dependency-wave planning.
3. QUE owns admission, queue priority, claims, and lifecycle.
4. Specialist adapters own execution.
5. ATES owns canonical evidence validation and provenance.
6. Temporal Intelligence owns assignment windows, phase, cadence, wake, and drift semantics.
7. Conductor emits cue sheets and dispatch intent through existing control planes.
8. Composer owns only intent normalization, score composition, and decision trace.
9. Signals and context remain source-attributed; unknown data remains unknown.
10. Feedback changes future policy only through an explicit, versioned, evidence-backed promotion.

## 8. Deliverables

- `deepcli/deepcli/observatory/composer.py`: typed intent/policy contracts and deterministic score compiler.
- `deepcli/tests/test_composer.py`: TDD coverage for success, determinism, validation, and authority.
- `docs/architecture/BRAIN-CNS-COMPOSER.md`: module map, data flow, ownership, failure behavior, and extension contracts.
- `docs/architecture/BRAIN-CNS-COMPOSER.mmd`: canonical Mermaid architecture source.
- `docs/schemas/composer.score.v1.schema.json`: machine-readable output contract.
- A plan and a runnable example using the existing Ballet and Conductor interfaces.

## 9. Acceptance criteria

- Same normalized input + same policy version ⇒ identical score.
- Every cue maps to exactly one input task and supplied assignment.
- All task dependencies remain represented in the Ballet plan.
- Every cue retains required phase, timing-window, dependency-barrier, and evidence-reference metadata.
- Output carries `dispatch_intent_only`; no dispatch or claim mutation occurs.
- Invalid inputs fail with actionable validation errors.
- Unit tests cover the acceptance criteria and run with the existing Observatory test suite.
- Repository gates run on the exact candidate SHA before promotion.
