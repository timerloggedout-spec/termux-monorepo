# Optimized Routing Control Plane

## Core invariant

> **There is no primary provider and no secondary provider. There is only optimized routing.**

Provider, model, agent, adapter, tool, and human/operator are **candidate nodes**. A route is a policy decision over the currently eligible graph.

The graph may be:

`single → series → dynamic → parallel → nested → co-working → volley`

and may change topology between experiment epochs.

## Control loop

`OPERATOR → objective/constraints → classifier → Scout → manager/Orchestrator → admission → topology → execution → evidence → evaluation → re-route`

The names describe functions, not a permanent authority hierarchy.

### OPERATOR
Defines or authorizes objective, risk tolerance, acceptance conditions, scope, and stop conditions.

### Classifiers
Determine task family, required capabilities, dependencies, risk, freshness, and independence. Classification is an input to routing—not a provider selection.

### Scout
Discovers candidate providers/models/tools, current availability, relevant repository context, and experimental opportunities.

### Manager / Orchestrator
Chooses the topology and candidate set using current evidence. It may:
- select one participant;
- create ordered series stages;
- dispatch independent work in parallel;
- create nested specialist subroutes;
- establish co-working ownership boundaries;
- run bounded volley/review cycles;
- wait when downstream context is not ready;
- re-solve admission after failure, quota change, or new evidence.

### MEV / Jev / Kev / LAYA
These are **measurement and context vectors**, not model rankings:
- **MEV** captures measurable outcome/effort dimensions.
- **Jev** captures joint/co-working contribution across participants.
- **Kev** captures knowledge/evidence provenance and context utility.
- **LAYA** can encode lane-aware yield/allocation dimensions for a given experiment.

Concrete fields must be defined per experiment epoch and preserved with the evidence ledger.

## DoE + MVT

Routing research is an experimental system.

**DoE factors** can include provider, model, manager policy, topology, prompt variant, context budget, concurrency, validation policy, and retry policy.

**MVT** is the smallest independently observable treatment capable of testing a routing hypothesis.

Every experiment preserves:
`run_id + run_attempt + head_sha + manager + policy_version + cohort + task + topology + provider + model + catalog_hash`

A treatment that never executes is an admission observation, not a performance result.

## Hard gates before scoring

1. capability
2. credential/configuration
3. live catalog or explicit stale evidence policy
4. availability/health
5. quota/cooldown
6. task ownership / freshness
7. current SHA when mutation is possible
8. policy authorization

A failed hard gate excludes the candidate. It does not become a negative score that another candidate can "beat".

## Optimization objective

The system should optimize integrated result quality subject to:
- correctness and verification
- time to integrated result
- useful context consumed
- duplicate work
- conflicts
- retries
- provider failures
- human intervention
- quota/credit consumption
- attribution confidence

**$0 capacity is an opportunity, not the objective.**

## Recovery

Recovery is **re-solving the route**, not traversing a fixed fallback chain.

If a selected participant fails:
`observe → classify failure → update evidence → re-admit candidates → re-select topology/participant → continue or stop`

A provider outage is not automatically a model-quality observation. A manager failure is not automatically a provider failure. A skipped invocation is not an execution result.

## Routing notation examples

- `SINGLE[A]` — one participant.
- `SERIES[A → B → C]` — ordered dependency stages.
- `PAR[A | B | C]` — independent parallel treatments.
- `DYN{A,B,C}` — candidate set re-evaluated as evidence changes.
- `NEST[A{B,C}]` — A orchestrates a bounded B/C subroute.
- `CO[A ↔ B]` — explicit shared ownership/co-working.
- `VOLLEY[A ⇄ B]×N` — bounded alternating passes.

Notation is descriptive. The evidence ledger remains authoritative.

## Implementation boundary

The current GitHub composite router exposes `routing-mode` and performs optimized **single-node selection** from a unified candidate pool. The broader topologies are now a first-class control-plane contract for the manager/orchestrator and MVT/DoE experiments; workflows should only claim a topology when the corresponding execution steps actually run.

That distinction prevents documentation from pretending a single-provider invocation is a parallel or co-working experiment.

## Continuous loop

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

The routing plane plugs into this loop at **CLASSIFY → admission → selection → execution → evidence**, while the observation/watch plane remains independent and immutable.


## Executable topology boundary

The routing topology contract is now executable through `scripts/routing_topology.py`.

- `single`: one admitted participant.
- `series`: ordered handoff; each stage receives the previous output.
- `parallel`: bounded concurrent independent treatments.
- `dynamic`: selection is recomputed from an explicit selector/context.
- `nested`: a bounded participant may return a subordinate route specification.
- `co-working`: participants operate against explicit shared state.
- `volley`: bounded alternating passes with an explicit stop condition.

Every execution emits `routing-execution/v1` evidence containing declared participants,
actually executed participants, outputs, round count, status, timestamp, and sanitized
error classes.

This preserves the invariant:

`declared route != executed route != successful outcome`.

The executor does **not** perform provider admission, credential validation, security
authorization, or quality scoring. Those remain upstream control-plane responsibilities.
A topology implementation is therefore not evidence of provider quality, and a failed
participant is recorded as execution evidence rather than silently converted into a
routing preference.
