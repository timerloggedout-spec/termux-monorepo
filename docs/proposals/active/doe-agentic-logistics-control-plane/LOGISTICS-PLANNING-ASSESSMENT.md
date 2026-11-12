# Logistics planning source assessment

## Decision

Use the owned Air Cargo fork as a conceptual and test-fixture seed, not as an already executable PDDL repository. Build a small, standards-conformant PDDL domain/problem fixture as a separate DPLC-003 artifact, then compare compatible planners. Do not claim that a PDDL planner is already installed or running.

## What the owned repositories actually contain

### timerloggedout-spec/AI-Planning_fork-PDDL-air-transport

Inspected default branch: master.

| Path | Observed content | Evidence |
|---|---|---|
| README.md | Describes a classical Air Cargo PDDL exercise, three problem instances, Load/Unload/Fly action schemas, uninformed search and planning-graph heuristics. | Blob SHA 678c19d30c74c2ba93ec2acbec4da607d0e9e257. |
| my_air_cargo_problems.py | Python AirCargoProblem class. Grounds concrete Load, Unload and Fly actions, checks positive/negative preconditions, computes state transitions and goal tests, and exposes heuristics. | Blob SHA e526852d0c3fdbec6da6d56fd8c9593e55046fe7. |
| tests/test_my_air_cargo_problems.py | Unit tests for problem fluents/goals, action counts, applicable actions, state transitions and the ignore-preconditions heuristic. | Blob SHA 51ae8e74dd489221a2a3d49065dc8a3ac7d682c2. |
| Tree inventory | No .pddl files were present in the complete, non-truncated default-branch tree. | Tree SHA 4b3bf45036c6045a24f71705582952b3c1bac149. |

**Interpretation:** the README says the planning problems are defined in classical PDDL, but the repository snapshot inspected here represents the problem in a Python/AIMA-style propositional search implementation. It is not evidence of a serialized PDDL domain/problem file, a planner executable, or an integration-ready PDDL pipeline. The README also references my_planning_graph.py, lp_utils.py and AIMA support; these are Python implementation dependencies, not a PDDL interchange interface.

The Air Cargo semantics provide a useful minimal seed:
- Load(c,p,a): cargo and plane co-located at airport; cargo becomes in-plane.
- Unload(c,p,a): cargo is in plane and plane is at airport; cargo becomes at airport.
- Fly(p,from,to): plane at origin; plane moves to destination.

The README's problem instances define initial states and cargo destination goals for two to four cargo items and two to three airports/planes. This is small enough to serve as a deterministic symbolic fixture after the semantics are encoded and validated.

### timerloggedout-spec/rl-multiagent-transfer_fork

Inspected default branch: main.
- Complete tree contains only README.md.
- README describes multi-agent path planning based on reinforcement learning for intelligent library logistics.
- No implementation, environment, policy checkpoint, tests, benchmark, dependency manifest or root LICENSE was present in the inspected tree.

**Disposition:** discovery lead only. Do not benchmark, adopt or cite algorithmic performance until source code and reproducible environment are available.

### timerloggedout-spec/FrieghtFlow

Inspected default branch: main.
- README describes a freight/shipment product with Next.js/React, NestJS, PostgreSQL/TypeORM and Stellar components.
- Backend package manifest declares private: true and license: UNLICENSED.
- No root LICENSE file was found at the inspected path.

**Disposition:** domain vocabulary and workflow-discovery reference only. Do not copy, install, deploy, or treat it as an available logistics execution service without owner authorization and license resolution. The README's claimed smart-contract features are not independently verified by this assessment.

## DPLC-003 implementation boundary

### Phase 1 — normalize the symbolic model

Create a small PDDL 1.2 STRIPS-style Air Cargo domain/problem pair derived from the README's action schemas. Pin the exact domain/problem fixture hashes. Verify:
- every action's typed parameters, positive preconditions, add effects and delete effects;
- initial-state consistency (no fluent and its negation both asserted);
- every goal literal is reachable in the selected fixture;
- plans replay against an independent state-transition verifier;
- invalid action applications are rejected;
- planner result distinguishes solved, unsolvable, unsupported and timeout.

Do not add numeric fluents, temporal constraints or probabilistic effects to the first STRIPS fixture.

### Phase 2 — planner adapter comparison

Evaluate candidate planners against the exact same fixture:
- Unified Planning as a candidate problem/engine abstraction and PDDL parser/serializer;
- Fast Downward as a candidate classical planner, only for supported PDDL fragments;
- retain the Python search implementation as a baseline only if its dependencies and tests can be reproduced.

Record planner version, supported language fragment, invocation, plan cost, expanded nodes (if available), wall time, memory (if available), result status and independent replay result. No solver is accepted based on README marketing or a single successful example.

### Phase 3 — numeric scheduling is separate

Only after the symbolic model is stable, create a CP-SAT fixture for numeric constraints such as:
- vehicle/plane capacity and resource exclusivity;
- assignment of jobs to resources;
- pickup/delivery time windows;
- route duration/cost and shift boundaries;
- precedence constraints passed from the symbolic plan.

Compare objective and feasibility separately. An optimizer must never relax safety, eligibility or hard precedence to improve a score.

### Phase 4 — dynamic control is not planning

The runtime inference controller is a different problem from PDDL and route optimization. It reacts to measured arrival/completion rates, concurrency, latency, rate limits and quota evidence. It may recommend bounded pacing or admission changes only after the existing provider admission contract allows the exact instance. It must not be encoded as a duplicate logistics scheduler or infer provider eligibility from symbolic planner output.

## Acceptance evidence

DPLC-003 remains queued until all of the following exist:
1. Pinned PDDL domain/problem fixture files and documented fragment.
2. Parser/planner compatibility report.
3. Deterministic action validity and plan-replay tests.
4. CP-SAT feasibility fixture with independent constraint verifier.
5. Explicit timeout/unsupported/no-solution handling.
6. Source/license review for every dependency actually selected.
7. Same-head repo gate and Termux smoke after implementation.

No upstream package is installed, no repository is modified, and no external planner is represented as operational by this assessment.