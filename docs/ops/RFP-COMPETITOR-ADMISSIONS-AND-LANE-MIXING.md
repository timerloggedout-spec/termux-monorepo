# RFP Pipeline — Extensible Competitor Admission and Lane Mixing

**Status:** governance specification / implementation plan  
**Authority:** RFP pipeline is an internal operating mandate. DoE governs comparative pipeline versions, competitor admission, lane composition, measurement, and evolution. The established 13-phase process remains a valid asynchronous execution option.  
**Scope:** extensible admission of new competitor versions and controlled mixing of internal/external lanes under the existing RFP and DoE authorities.

## 1. Governing model

The RFP pipeline is the internal mandate: it defines how opportunities and proposals are discovered, normalized, evaluated, routed, prepared, reviewed, and closed. DoE supplies a family of versioned methods for carrying out and improving that mandate.

External due dates are authoritative temporal constraints when an opportunity carries them. They influence the affected workstream's urgency, sequencing, readiness, and escalation. They do not replace the internal pipeline, establish its phases, or become the general planning model.

Keep these dimensions distinct:

| Dimension | Authority | Meaning |
|---|---|---|
| RFP mandate | RFP operating contract | Required internal process and governance |
| Pipeline version | DoE version registry | A separately identifiable method for executing the mandate |
| Competitor | Candidate registry / source evidence | An internal or external alternative method, implementation, capability, or configured lane |
| Lane | Owning lane contract | A bounded capability, provider, workflow, evaluator, or execution surface |
| Lane composition | DoE campaign design | A tested combination or hand-off among compatible lanes |
| Phase | Canonical 13-phase process or selected alternative | Governance and outcome progression |
| External due date | Authoritative external source | A time constraint attached to the affected opportunity/workstream |

The RFP mandate remains stable while its candidate methods evolve. A new competitor may enter the candidate population without changing the mandate or displacing the incumbent.

## 2. Version family and extensible admission

Treat each materially distinct pipeline method as a versioned DoE treatment. The registry is open-ended: new candidates can be proposed and admitted through the same contract as the initial versions.

Initial comparison set:

| ID | Candidate | Classification | Admission posture |
|---|---|---|---|
| RFP-V1 | Current mandated RFP pipeline | Incumbent / baseline | Baseline; preserve its current authority |
| RFP-V13 | Canonical 13-phase process | Established governance option | Comparative candidate; async overlap is permitted |
| RFP-VD | Dependency-driven pipeline | Candidate design | Register and pre-register before designed execution |
| RFP-VH | Hybrid 13-phase + dependency-driven execution | Candidate composition | Register as a distinct version and test interactions |

This list is extensible, not closed. Each new competitor receives a stable candidate ID and immutable source identity. A new release, materially changed configuration, changed prompt/tool set, revised phase topology, or changed lane composition creates a new version or configured-instance identity as appropriate.

### Admission lifecycle

1. **Discover** — identify a candidate from an external source, internal lane, research result, generated proposal, benchmark, or production observation.
2. **Capture** — retain source URL/repository, revision or release, observed timestamp, license/terms, maintainer evidence, provenance, and immutable artifact hashes.
3. **Normalize** — describe the capability contract, inputs, outputs, phase behavior, lane requirements, dependencies, and intended RFP consumer.
4. **Classify** — mark implementation, method, specification, research result, benchmark, template, complement, competitor, duplicate/alias, historical, blocked, or unknown.
5. **Relate** — connect it to existing candidates and lanes using explicit relations: competes-with, complements, composes-with, measures, consumes, supersedes, or derived-from.
6. **Triage** — evaluate license, security, privacy, supply chain, maintenance, compatibility, cost/quota, operational access, and external obligations.
7. **Pre-register** — define hypothesis, factors/levels, baseline, cohort, assignment, blocking, sample/replication plan, outcomes, thresholds, stopping rule, and automation before designed execution.
8. **Admit** — assign an explicit state and owner disposition. Admission to comparison grants experiment participation only; it does not grant production routing, credentials, permissions, external submission authority, or promotion.
9. **Execute** — dispatch through the campaign's declared automation and existing lane contracts; emit one canonical experiment record per executed run.
10. **Evaluate** — compare against the same task/evidence basis, preserve source-class distinctions, measure main and interaction effects, and calibrate predictions against outcomes.
11. **Promote / retain / cull / defer** — record an evidence-backed disposition and lineage. Cherry-picked improvements become a new registered version/cohort, never a silent mutation of an existing treatment.

### Admission states

Use explicit lifecycle states and preserve state transitions append-only:

- `discovered`
- `classified`
- `triage_pending`
- `eligible_for_design`
- `pre_registered`
- `admitted_design_only`
- `executing`
- `executed`
- `validated`
- `promoted`
- `retained`
- `culled`
- `deferred`
- `blocked`
- `superseded`
- `historical`

Proposal status, admission status, execution status, outcome validity, and promotion status remain separate fields. A proposal or Delphi award alone does not establish experiment admission or production readiness.

## 3. Machine-readable contracts\n\nThe governance records use dedicated JSON Schema 2020-12 contracts:\n\n- `docs/ops/rfp/COMPETITOR-ADMISSION.schema.json` — candidate source, immutable version/configuration identity, capability contract, lifecycle, admission decision, and production-authority boundary.\n- `docs/ops/rfp/LANE-COMPOSITION.schema.json` — composition pattern, participating lanes, topology, compatibility gates, experimental design, and production-routing boundary.\n- `docs/ops/rfp/examples/` — illustrative records for RFP-V13 admission and a parallel baseline/candidate comparison.\n- `tests/test_rfp_admission_schemas.py` — schema and authority-boundary proof obligations.\n\nThese records govern candidate and composition admission. Executed work continues to emit the family-adopted `docs/ops/corpus/EXPERIMENT.schema.json` record, one per executed run.\n\n## 4. Competitor identity and evidence

Candidate identity must distinguish a named product/method from the configured instance that actually ran.

For every configured lane instance, reuse the DoE family identity contract:

`{provider, model@version, system_prompt{ref,sha256}, tools{ref,sha256}, role, moniker, context, instance_key}`

Also stamp the candidate/version ID, lane ID, source revision, pipeline version, phase topology, and campaign ID. Hash the exact dispatched configuration. Comparisons and attribution group by configured instance, not a provider or model label alone.

Each run emits exactly one record conforming to `docs/ops/corpus/EXPERIMENT.schema.json`. Designed runs carry the pre-registered design provenance. Undesigned production activity remains observational. Existing historical records remain immutable.

## 5. Lane mixing and composition experiments

Lane mixing is a first-class DoE operation. A lane may contribute a capability, phase, evaluator, provider, execution arm, or hand-off. The design declares the composition and tests the combined treatment.

### Composition patterns

| Pattern | Description | Example |
|---|---|---|
| Parallel arms | Independent lanes receive equivalent work and produce comparable outputs | Two proposal-generation lanes |
| Sequential hand-off | One lane's validated output becomes the next lane's input | Discovery → normalization → evaluator |
| Phase-specialized composition | Different lanes own different phases or phase segments | Research lane + implementation lane + review lane |
| Ensemble / consensus | Multiple lanes independently evaluate a shared evidence bundle | Blind ballots with source classes preserved |
| Conditional routing | A declared gate routes work to a lane based on readiness or capability | Specialist lane on a qualifying task class |
| Complementary composition | Distinct capabilities combine into one treatment | Generator + validator + calibrated reviewer |
| Mixed factorial treatment | Lane choices and pipeline methods vary as explicit factors | Pipeline version × generator lane × reviewer lane |

A composition is a distinct treatment when the combination, routing policy, hand-off policy, or configuration materially changes. Record all participating lanes and transitions. Stamp both source and destination configured instances at every hand-off.

### Compatibility and composition gates

Before a mixed treatment executes, declare:

- Shared task and capability contract.
- Input/output schema compatibility and transformation rules.
- Data provenance and evidence preservation across hand-offs.
- Lane ownership, accountability, and failure semantics.
- Security, privacy, license, and credential boundaries.
- Quota, capacity, rate limits, latency, and retry policy.
- Determinism or acceptable variance assumptions.
- Conflict resolution and evaluator independence.
- Human approval points and consequential-action boundaries.
- Rollback, isolation, and containment behavior.

A lane's admission does not imply that every combination containing it is eligible. Composition compatibility is assessed per combination. Preserve incompatible and untested combinations as explicit states rather than silently omitting them.

### Mixing design

Use the design class that matches the question:

- Full factorial when estimating all declared factor combinations is feasible.
- Fractional factorial or orthogonal arrays when a justified screening design reduces the run burden.
- Mixture designs when proportions of lane contributions are the treatment variables.
- Split-plot designs when some lane factors are expensive or difficult to randomize at the individual-run level.
- Sequential designs when evidence justifies adaptive follow-up and the stopping rule is pre-registered.
- Pairwise or staged screening as a discovery filter, followed by a confirmatory design for promotion claims.

The existing DoE taxonomy remains authoritative for generator availability. A design class named in a skill or proposal is not treated as an implemented generator until its runner and validation exist.

Measure individual lane effects, interaction effects, hand-off loss, composition overhead, and the combined outcome. A combined treatment earns promotion through its own evidence; component scores do not prove composition quality.

## 5. Pipeline versions and the canonical 13 phases

RFP-V13 uses the established 13 phases in `docs/ops/ACTIONS-MATRIX-UPGRADE-PLAN.md` and Issue #631:

1. Initiation / Purpose
2. Challenge / Obstacle
3. Activation / Movement
4. Form / Architecture
5. Empowerment / Core
6. Balance / Rhythm
7. Alignment / Attunement
8. Integrity / Modeling
9. Realization / Intent
10. Manifestation / Production
11. Release / Dissolution
12. Cooperation / Review
13. Transcendence / Evolution

The phases remain the governance sequence. Multiple asynchronous workstreams may overlap across phases when their dependencies, readiness, capacity, and authorization conditions permit. Workstream slots are dependency relationships, not new phases or fixed calendar promises.

Other pipeline versions may use different internal topologies, but each must map its work and evidence to the shared RFP capability contract and comparable outcome dimensions. Preserve the mapping so comparisons remain interpretable.

## 7. External due dates as direct constraints

An external due date enters the plan only when supported by authoritative evidence. Store the source, exact instant, timezone, observed time, and date type (registration close, eligibility cutoff, submission close, event start, award date, or external recheck).

Link the date to the affected opportunity, candidate, lane, workstream, phase, and internal decision owner. Derive countdowns from the authoritative instant. Recalculate readiness and escalation when the source changes.

External dates directly constrain the affected submission or event. The internal RFP pipeline continues to govern intake, preparation, evaluation, and oversight. When the deadline cannot be met, record a decision and disposition; preserve the internal cadence and next review trigger.

## 7. Shared outcome and decision contract

Use the existing DoE outcome ordering:

1. Execution status
2. Task outcome
3. Correctness
4. Integration
5. Regression
6. Resource cost

Add RFP-relevant outcomes where the campaign requires them: eligibility correctness, source/evidence completeness, response coverage, compliance, submission readiness, deadline compliance, and post-submission result. Pre-register thresholds and weights; preserve raw measures alongside composite scores.

Every decision receipt records:

- Candidate, pipeline version, lane(s), composition, and configured-instance keys.
- Campaign/design ID and pre-registration revision.
- Task/cohort and assignment/block.
- Source evidence and hashes.
- Dispatch/run IDs and phase/workstream transitions.
- Outcomes, validity checks, and resource measurements.
- Comparison basis, uncertainty, interaction effects, and calibration.
- Disposition, rationale, owner, and next review trigger.
- External deadline evidence when applicable.

Human decisions and automated recommendations remain distinguishable. Promotion follows existing owner authorization and repository dual-gate policy.

## 8. Continuous discovery and evolution

New competitors can enter through CEEL discovery, Delphi-generated proposals, external release/repository events, internal lane discoveries, benchmark changes, or production outcome signals.

Reuse the existing CEEL capability graph, proposal registry, Delphi/EGM lifecycle, DoE experiment schema, integration mesh, and owning lane registries. This specification adds their RFP-specific admission and composition rules; it does not create another scheduler, ledger, registry, or control plane.

Discovery is event-driven with existing bounded recovery/reconciliation paths. Candidate revisions and relationships remain traceable. Reconsider deferred candidates when evidence, internal demand, compatibility, or external maturity changes.

## 10. Implementation sequence

| Step | Deliverable | Acceptance evidence |
|---|---|---|
| A0 | Link this contract from DoE family and CEEL | Canonical docs cross-reference each other |
| A1 | RFP pipeline version registry mapping | Stable IDs, versions, owners, source pins, states |
| A2 | Candidate admission schema and validator | Lifecycle, provenance, relations, identity, and state-transition tests |
| A3 | Lane-composition schema and validator | Compatibility declarations, hand-off stamps, explicit combination states |
| A4 | Campaign designs for baseline, 13-phase, and selected alternatives | Pre-registration and canonical design records |
| A5 | Mixed-lane pilot | Automated runs, canonical records, main/interaction analysis |
| A6 | External due-date linkage | Verified source/timezone, affected work mapping, computed escalation |
| A7 | Comparative evaluation and promotion | Same-basis evidence, calibrated decision receipt, owner disposition |
| A8 | Continuous admission | Event-driven intake, dedupe, immutable lineage, bounded recovery |

Build validators and record emission alongside the schemas. Reuse existing automation and owning registries. Each admitted campaign names its runner/workflow in `DESIGN.json`; manual chat dispatch is not the experiment execution mechanism.

## 11. Acceptance criteria

- The RFP pipeline remains the internal mandate across all candidate versions.
- New competitor versions can be proposed and admitted through a repeatable, extensible lifecycle.
- Every candidate has source provenance, immutable version identity, owner, state, and disposition.
- Candidate admission, experiment admission, execution, validation, and production promotion are separate decisions.
- Lane compositions are registered as explicit treatments with compatibility and hand-off evidence.
- Both component and interaction effects are measured for mixed treatments.
- The canonical 13-phase sequence remains intact while async workstreams may overlap.
- Alternative topologies map to the shared RFP capability and outcome contract.
- External due dates constrain only the affected work and carry authoritative provenance/timezone.
- Every designed run emits one canonical experiment record; observational runs remain labeled observational.
- Cull, retain, promote, and cherry-pick actions preserve version lineage and evidence.
- Existing CEEL, Delphi, DoE, lane registries, and repository gates retain their authorities.

## 11. Repository authorities

- DoE family: `docs/ops/DOE-FAMILY.md`
- Canonical 13-phase map: `docs/ops/ACTIONS-MATRIX-UPGRADE-PLAN.md`
- DoE taxonomy: `docs/ops/DOE-TAXONOMY.md`
- Experiment schema: `docs/ops/corpus/EXPERIMENT.schema.json`
- CEEL design: `docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md`
- CEEL plan: `docs/superpowers/plans/2026-11-11-continuous-capability-evolution-lab.md`
- Capability opportunity graph: `docs/integrations/capability-opportunity-graph.json`
- Delphi RFP gate: `docs/ops/DELPHI-ORACLE-RFP-GATE.md`
- Delphi generation and crossover: `docs/ops/DELPHI-STATUS-AND-CROSSOVER.md`
- Adaptive dispatch: `docs/ops/ADAPTIVE-DISPATCH.md`

**Truth boundary:** this document defines the target governance contract and delivery sequence. Implementation, automation, validation, live competitor connectivity, and production promotion require their own repository evidence.
