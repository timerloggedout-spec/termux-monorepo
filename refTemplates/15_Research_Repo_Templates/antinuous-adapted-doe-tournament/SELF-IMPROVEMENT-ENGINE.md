# Self-Improvement Engine (SIE)

**Contract:** sie.control-plane.v1 (proposed)  
**Role:** turn validated observations into controlled improvements to classifier capabilities, routing graphs and tournament implementations.

SIE is the improvement controller inside the wider DoE Tournament operating system. It owns the evidence-to-change loop; it does not silently rewrite its own acceptance criteria or promote its own candidates.

## 1. Operating model

~~~text
RECON → REGISTER → DESIGN → ASSIGN → EXECUTE → OBSERVE
  ↑                                              ↓
  └── EVOLVE ← PROMOTE / HOLD / RETIRE ← COMPARE ← EVALUATE
~~~

Each cycle is bounded by a goal, cohort, resource budget, policy version and stopping rule. Every change produces a run receipt and a decision record.

## 2. SIE subsystems

| Subsystem | Responsibility | Output |
|---|---|---|
| Capability registry | discover and version classifiers, agents, tools and providers | capability manifest + evidence |
| Experiment designer | define hypotheses, factors, blocks, controls and sample strategy | preregistered design |
| Cohort and assignment service | freeze tasks and assign comparable treatments | assignment manifest |
| Graph composer | create candidate routing/composition DAGs | graph manifest + hash |
| Scheduler / admission | enforce dependencies, quota, leases, safety and budgets | execution claims |
| Execution adapters | run local, Actions, provider, MCP/A2A or container workers | attempt receipts |
| Evidence ledger | append observations, artifacts, hashes and provenance | immutable evidence |
| Evaluator ensemble | deterministic checks, specialist classifiers, independent judges and human adjudication | versioned evaluation |
| Statistical reducer | estimate effects, uncertainty, interactions, drift and complementarity | comparison report |
| Evolution controller | mutate/crossover policies and graphs; preserve diversity and parent lineage | challenger versions |
| Promotion controller | apply feasibility, held-out, robustness and dual-gate/task-outcome rules | promote / hold / reject |
| Memory / knowledge index | retain reusable findings, known failure modes and decision context | indexed evidence references |
| Oversight console | expose state, costs, blockers, approvals and rollback target | operator decision surface |

## 3. Improvement targets

SIE compares and improves four separate populations:

1. **Classifier capabilities** — individual 70+ classifier entries, measured within supported task contracts.
2. **Routing policies** — which classifier or provider receives which task and when.
3. **Composition graphs** — which capabilities run together, in parallel, conditionally or sequentially.
4. **Tournament implementations** — the manager, scheduler, evaluator, evidence and promotion machinery itself.

The fourth population is the central tournament objective requested here. The other three populations are inputs and levers. A better classifier score alone does not prove a better tournament implementation.

## 4. Versioned implementation competition

Every challenger must carry:

- `implementation_id`, semantic version and source commit;
- parent/incumbent IDs and change set;
- graph, routing, scheduler and evaluator hashes;
- accepted schema versions;
- task contract, cohort and environment fingerprints;
- classifier catalog snapshot and capability versions;
- experiment design, random seed and assignment digest;
- resource ceilings, safety envelope and stopping rule.

Competition protocol:

1. Freeze incumbent and candidate definitions.
2. Run both on the same matched task cohort and environment.
3. Randomize order/assignment where feasible; isolate mutable state and caches.
4. Capture complete per-attempt events and artifacts.
5. Run deterministic checks before model-based judges.
6. Compare quality, integration, robustness and resource cost as a vector.
7. Re-run promising variants on held-out tasks and a later time window.
8. Promote by explicit gate; preserve rollback pointer and full parent lineage.

The tournament compares complete implementation versions. It can separately run ablations to attribute gains to one component.

## 5. Evolution policy

Use a conservative hybrid:

- **Incumbent/challenger:** maintain one known-good incumbent and bounded challengers.
- **Ablation:** vary one factor at a time when causal attribution matters.
- **Factorial screening:** test interactions across a small declared set of factors.
- **Island evolution:** preserve several diverse candidate families; periodically exchange high-value components.
- **Adaptive allocation:** use bandits/Bayesian methods only after a stable baseline and sufficient observations.
- **Shadow evaluation:** replay historical or held-out inputs without affecting live decisions.
- **Canary admission:** expose a promoted candidate to a small controlled slice before broad default routing.
- **Rollback:** restore the last accepted implementation when canary constraints fail.

Every mutation records parent, operator, changed dimensions, seed and rationale. Retain eliminated candidates and negative evidence.

## 6. Decision logic

Use hard gates first:

- task contract and schema validity;
- security, privacy and safety;
- provenance completeness;
- deterministic correctness and integration;
- reproducibility and held-out robustness;
- budget and operational feasibility.

Then compare the feasible set with Pareto dominance. Use a versioned preference profile only to choose among non-dominated candidates. Keep raw measures and uncertainty available for later re-scoring.

SIE optimizes **validated integrated outcome per total resource cost**. Total cost includes compute, inference, wall time, context, human effort, retries, conflicts and integration overhead. Nominally free calls are not automatically efficient.

## 7. Bounded feedback loop

Each iteration executes:

1. **Observe:** re-fetch current code, registries, run receipts and evidence.
2. **Diagnose:** classify the limiting factor as capability, routing, graph, evaluator, execution, data, or environment.
3. **Choose:** select one high-value, in-scope change with a falsifiable hypothesis.
4. **Act:** create a versioned challenger in an isolated worktree/branch.
5. **Verify:** run the same acceptance checks and matched cohort.
6. **Compare:** calculate effect, uncertainty, failures and cost delta.
7. **Record:** append immutable receipts, lineage and decision.
8. **Continue or stop:** continue only when measurable improvement remains and budget permits.

Terminal states: `promoted`, `held`, `rejected`, `clean_noop`, `blocked`, `approval_required`, `budget_exhausted`, `stagnated`, `failed`.

A failed experiment remains a useful observation. A timeout remains distinct from a provider error. A route that was selected but never invoked earns no performance credit.

## 8. Improvement safeguards

- Keep the evaluator independent from the candidate under evaluation.
- Pin evaluator versions and protect held-out labels from worker context.
- Preserve immutable raw outcomes; derive scores through versioned reducers.
- Detect evaluator drift, cohort contamination and selection bias.
- Retain a randomized exploration/control share during adaptive allocation.
- Require human approval for high-impact policy, security, privacy and production changes.
- Make every promotion reversible and auditable.
- Keep scheduling and external side effects behind explicit admission/authorization.

## 9. Bounded reusable loop

**SIE Evidence Loop**

> Re-fetch the incumbent, candidate registry and latest receipts. Diagnose one measurable gap. Create one isolated, versioned challenger with a falsifiable hypothesis. Run the preregistered matched checks within budget. Compare raw outcomes, uncertainty and total cost. Record the receipt and promote, hold, reject or stop under the declared gates. Repeat while measurable improvement remains.

## 10. Relationship to existing repository systems

- `manager.tournament.v1` remains the canonical manager cohort.
- `deepcli/deepcli/observatory/doe.py` remains the existing assignment helper.
- `deepcli/deepcli/observatory/trial.py` remains the current Mev/Jev/Kev/Laya baseline adapter until candidate-ID joins and graph scheduling are implemented.
- `deepcli/deepcli/observatory/tournament.py` and `leaderboard.py` remain existing baseline aggregation surfaces; validate their missing-value semantics before canonical evidence use.
- `scripts/agent_evolution/replay_simulator.py` and `docs/ops/EVOLUTIONARY-REPLAY.md` provide the existing deterministic evolution/replay foundation.
- SHE / 3L0 / Moneyball remain downstream evidence and decision projections.

SIE is a proposed integration architecture. This document records the target contract, not a claim that every subsystem is already implemented.

## 11. Implemented registry alignment

The classifier registry now provides the initial SIE control-plane
inventory:

- 61 model candidates and 27 infrastructure references, preserving all
  88 catalog entries by declared layer.
- Explicit `role_mapped`, `role_mapped_unverified` and
  `unclassified` capability qualification states.
- A 61-node design-only model screen.
- An implementation competition record for the incumbent manager
  tournament and the design-only SIE challenger.
- Matched-cohort, held-out, independent-evaluator, immutable-receipt,
  rollback and owner-approval gates.

The next SIE implementation tranche qualifies candidates individually,
builds candidate-specific execution bindings, and runs bounded screens.
The full classifier estate remains a separate operating-surface inventory.


## 12. Executable matched-implementation comparator

`deepcli/deepcli/observatory/implementation_competition.py` adds a
stdlib-only comparison engine for exactly two versioned implementations.
It joins immutable receipts by task ID and requires the same cohort,
task contract, environment fingerprint and evaluator version.

The reducer reports per-metric paired deltas, sample counts, missing-value
preservation and approximate 95% intervals. Hard-gate failures block a
challenger recommendation. Dominance requires interval-supported
non-regression across every comparable metric and positive improvement
on at least one. A challenger recommendation routes to human review;
the module leaves promotion as a separate owner-approved operation.

Tests live in `deepcli/tests/test_implementation_competition.py` and
run in the repository gate. This is an executable comparison component;
the complete SIE control plane remains a design-only challenger pending
scheduler, receipt-ledger, evaluator and promotion-controller integration.

