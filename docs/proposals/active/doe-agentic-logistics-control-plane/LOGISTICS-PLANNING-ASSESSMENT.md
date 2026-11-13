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


### sunsided/pddl-rs — parser candidate, not planner

Inspected default branch: main; complete tree SHA `c0a84ba41c104f9e1c04250925b6de5962e576c0`.

- README describes a strongly typed PDDL 3.1 parser written in Rust using nom.
- Cargo package `pddl` v0.3.0; edition 2021; minimum Rust 1.80. Default features enable parser + interning; pretty-print is optional.
- README demonstrates Briefcase World parsing and a multi-block PddlFile with one domain and multiple problems.
- `examples/pretty_print.rs` demonstrates typed names/variables/types, either-types and a durative-action pretty-print case; run with `cargo run --example pretty_print --features pretty`.
- Cargo.toml declares EUPL-1.2. Legal compatibility review is required before adding it as a dependency or copying code. An isolated parser toolchain remains a candidate subject to supply-chain review.
- Parser support does not establish planner/search/optimization or execution capability.

**Disposition:** high-value parser/AST candidate for DPLC-003. Validate fixture coverage and AST/pretty-print round-trip in an isolated toolchain. Parser acceptance is not plan validity; the independent action-transition verifier and planner remain separate.

### timerloggedout-spec/rl-multiagent-transfer_fork — full library RL implementation

Inspected default branch: `main`. The repository is a fork of `Hiago013/rl-multiagent-transfer`; GitHub fork metadata identifies that parent. The fork has one branch and seven commits, dated 2023-10-21 through 2024-01-10. The fork and upstream root listings expose the same implementation-file blob SHAs in the inspected snapshot.

This is **not** a README-only repository. The root tree contains a substantive Python implementation and associated data/artifacts:

| Path / artifact | Observed role |
|---|---|
| `GridWorld.py` (17.2 KB) | Two-floor grid environment; state/action/reward transitions, pickup/drop-off/elevator/obstacle handling, dynamic flags and curriculum integration. The configured example uses a 9×9 grid, two floors and five actions (four moves + wait). |
| `brain.py` (3.5 KB) | Tabular Q-learning policy: epsilon-greedy action selection, Q updates, Q-table save/load. |
| `multi_agent.py` (24.2 KB) | Multi-agent coordinator, shared policy/Q-table, per-agent observations/metrics, action selection and collision-neighbor flagging; includes transfer-learning entry points. |
| `training.py` (14.5 KB) | Staged training loop, obstacle/curriculum changes, transfer-learning stages and runtime logging. |
| `curriculum.py`, `curriculum_kevin.py` | Curriculum state/stage generation. |
| `transfer.py` | Q-value transfer helpers between states/policies. |
| `view.py` (9.4 KB) | Loads a saved Q-table and runs a two-agent visualization/evaluation loop; records agent metrics. |
| `logger.py`, `stack.py`, `node.py` | JSON logging and stack support. |
| `library_info/` | Pickup bays, elevators, delivery points, obstacles, sample JSON and single-/double-agent data. |
| `qtable.txt` | Serialized Q-table, 74,166,360 bytes. |
| `qtable_backup/qtable.txt` | Backup Q-table, 72,923,780 bytes. |
| `rewards_training/`, `Figures/` | 45 reward-plot images and 42 figure images in the inspected tree. |
| `animation.gif` | 11,507,198-byte run/behavior visualization artifact. |

Implementation evidence is directly visible in the source: `brain.learn` applies the tabular Q-learning update; `GridWorld.step` applies actions and rewards; `multi_agent.step` iterates agents against a shared environment/policy; `training.py` configures staged curriculum training; and `view.py` loads the persisted Q-table and runs a multi-agent visualization. The training script configures one agent; the view script configures two agents. This distinction matters when describing the trained policy versus the multi-agent evaluation scenario.

**What is established:** full source code, serialized learned state, library topology/data, training/evaluation scripts and historical output artifacts are present. The project is a real, domain-specific multi-agent RL implementation—not merely a problem statement.

**What is not yet established by this RECON:** a clean reproducible install, exact dependency versions, successful execution on the current Termux/runtime target, deterministic benchmark reproduction, or collision/deadlock guarantees. The inspected tree has no root LICENSE, dependency manifest or test suite. GitHub history is historical (last listed commit 2024-01-10), so maintenance status must be checked before depending on it. The large tracked Q-table and committed `__pycache__` also warrant repository-hygiene review.

**Disposition:** retain as the existing Library RL research implementation and a primary domain-specific baseline candidate. Do not discard it or replace it with a generic newly built simulator. First preserve source identity and license provenance; then reproduce its documented training/evaluation path in an isolated environment, record dependency/runtime versions and Q-table hashes, add deterministic fixtures and independent safety checks, and benchmark it against classical MAPF/OR-Tools baselines. Distinguish historical artifacts from newly reproduced results.

### timerloggedout-spec/FrieghtFlow

Inspected default branch: main.
- README describes a freight/shipment product with Next.js/React, NestJS, PostgreSQL/TypeORM and Stellar components.
- Backend package manifest declares private: true and license: UNLICENSED.
- No root LICENSE file was found at the inspected path.

**Disposition:** domain vocabulary and workflow-discovery reference only. Do not copy, install, deploy, or treat it as an available logistics execution service without owner authorization and license resolution. The README's claimed smart-contract features are not independently verified by this assessment.


## Library multi-agent logistics example — current evidence

The library example is `timerloggedout-spec/rl-multiagent-transfer_fork`, not a runnable simulator at this snapshot. Its complete `main` tree contains only `README.md` (tree SHA `8efb5703256167e29bbec4916c6dca6d1e973891`). That README names “Multi-agent Path Planning Based on Reinforcement Learning for Intelligent Logistics applied to a Library” and supplies no model, environment, agents, reward function, data, dependency lock, training/inference code, tests or benchmark. It is a domain scenario and candidate problem statement only.

Recovery path:
1. Locate upstream source/commit or a complete maintained fork; verify license and provenance.
2. Define the environment: map graph, shelves/locations, pickup/drop tasks, agent capacity, one-way/blocked edges, collision zones, service times and dynamic arrivals.
3. Establish deterministic baselines first: shortest-path routing, prioritized multi-agent path finding (MAPF), reservation-table planning and OR-Tools CP-SAT/Routing where constraints fit.
4. Add RL only as a separately compared treatment; pin observation/action/reward definitions, seeds, train/evaluation split and policy checkpoint hashes.
5. Verify collision-free paths, task completion, fairness, deadlock handling and constraints independently of reward. Measure throughput, makespan, travel distance, wait time, conflicts and energy proxy.
6. Keep the library environment separate from air-cargo fixtures; share task/resource vocabulary only after both adapters are tested.

No implementation or benchmark can be attributed to this README-only fork.

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