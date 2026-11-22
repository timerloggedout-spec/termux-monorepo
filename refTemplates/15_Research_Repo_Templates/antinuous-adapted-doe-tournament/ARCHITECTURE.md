# DoE Tournament — adapted architecture

## 1. System objective

Optimize **validated, reproducible outcomes per total resource cost** across competing manager policies and execution configurations.

A treatment is a complete execution condition, not just a model name:

~~~text
treatment = manager_policy × topology × provider/model × prompt_version × toolset × environment × evaluator
~~~

Preserve these factors independently so main effects and interactions can be estimated.

## 2. Recommended hybrid architecture

~~~mermaid
flowchart TB
  OP[Operator / Goal] --> REG[Experiment Registry]
  REG --> PLAN[Versioned DoE Planner]
  PLAN --> ADM[Admission + Quota + Safety]
  ADM --> DAG[Versioned Task DAG]
  DAG --> MGR[Manager Policy Runtime]
  MGR --> LEASE[Claims + Leases + Write Sets]
  LEASE --> ADAPT[Execution Adapter Ports]
  ADAPT --> LOCAL[Termux / Local Workers]
  ADAPT --> GHA[GitHub Actions]
  ADAPT --> MCP[MCP / A2A Peers]
  ADAPT --> CON[Container / Optional Cloud]
  LOCAL --> EV[Append-only Event Ledger]
  GHA --> EV
  MCP --> EV
  CON --> EV
  EV --> ART[Artifact + Provenance Store]
  ART --> EVAL[Independent Evaluators]
  EVAL --> RED[DoE / SHE / 3L0 Reducers]
  RED --> SEL[Utility + Pareto + Promotion]
  SEL --> REG
~~~

### Control plane

Owns experiment definitions, policy versions, cohort assignment, admission, leases, cancellation and promotion decisions.

### Execution plane

Runs bounded tasks using pluggable adapters. Termux/local execution is the low-cost baseline; GitHub Actions supplies CI-scale workers; containers and external MCP/A2A/cloud compute are optional.

### Evidence plane

Append-only canonical JSONL observations plus immutable manifests, artifact hashes, environment fingerprints and run/SHA linkage. Vendor dashboards are projections only.

### Evaluation plane

Runs independent correctness, completeness, safety, integration and reproducibility evaluators. ATES/WTCV contributes execution-efficiency observations but does not decide quality.

## 3. Viable architecture schemas with dynamic utility

### A. Versioned DAG + dependency-wave scheduler
**Best for:** repository work, multi-step experiments, builds and validations.

Each node declares inputs, outputs, dependencies, resource estimate, capability requirements, deadline, write set and acceptance tests. The scheduler admits nodes when dependencies pass and resources are available. Independent nodes run concurrently; dependent nodes wait.

Dynamic utility: prioritize by expected value, dependency criticality, uncertainty reduction, resource scarcity and deadline slack.

### B. Event-sourced state machine
**Best for:** durable tournaments, audit, replay, resume and version history.

Every state change is an event: experiment-created, treatment-assigned, task-claimed, execution-started, artifact-produced, evaluation-recorded, promotion-proposed, promotion-accepted. Materialized views are rebuilt from events.

Dynamic utility: compute current state and ranking from event history without rewriting historical runs. Corrections append superseding events.

### C. Hierarchical manager/worker swarm
**Best for:** heterogeneous tasks requiring specialist decomposition.

A manager chooses sequencing and parallelism; planners decompose; specialists execute; critics/evaluators assess; integrators produce a final result. Roles and capabilities are explicit and provider-independent.

Dynamic utility: manager policies are treatments in the tournament. Compare whole-team outcomes, not raw model rankings.

### D. Blackboard / shared evidence workspace
**Best for:** open research, discovery and multi-agent synthesis.

Workers publish typed findings, hypotheses, evidence links, confidence, artifact references and contradiction edges to a shared board. Synthesizers consume evidence rather than entire chat histories.

Dynamic utility: route work to unresolved high-value evidence gaps; prioritize novelty, confidence, contradiction resolution and decision impact.

### E. Actor model + leases + write-set isolation
**Best for:** concurrent execution and preventing conflicting repository edits.

Each task/worker owns a bounded actor identity and lease. File write sets are reserved or isolated in Git worktrees. Lease expiry and fencing tokens prevent stale workers from committing after reassignment.

Dynamic utility: schedule by resource fit and expected marginal gain while respecting single-writer boundaries.

### F. Factorial / fractional-factorial DoE
**Best for:** identifying which manager, prompt, model, topology or validation factors drive outcomes.

Use randomized blocks and factorial designs for controlled factors. Use fractional factorial designs when full combinations are too expensive; preregister aliasing and follow-up runs.

Dynamic utility: estimate main effects and selected interactions, then allocate follow-up experiments to high uncertainty/impact regions.

The repository already has full-factorial, Taguchi L9 and seeded randomized assignment helpers in deepcli/deepcli/observatory/doe.py. Reuse and extend those implementations after checking design assumptions and tests.

### G. Sequential Bayesian optimization / multi-armed bandit
**Best for:** adaptive allocation after a stable baseline and sufficient observations.

Use Bayesian optimization for continuous parameters and constrained multi-armed bandits for discrete treatment selection. Keep a randomized exploration fraction and a frozen control cohort.

Dynamic utility: allocate additional trials where expected information gain or expected improvement is high, while preserving comparability and exploration.

### H. Evolutionary / island tournament
**Best for:** evolving manager policies, prompts and workflow topologies.

Each candidate has immutable parent lineage and a policy version. Mutation/crossover creates new candidates; islands maintain diversity; periodic migration shares strong candidates. Selection uses validated outcomes and Pareto dominance.

Dynamic utility: select by constrained multi-objective fitness, diversity and novelty rather than one noisy scalar. Preserve eliminated candidates and failure evidence.

The repository already documents deterministic replay and incumbent-preserving evolutionary policy screening in docs/ops/EVOLUTIONARY-REPLAY.md. Extend that history-first design before adding live evolutionary execution.

### I. Constraint-based utility / Pareto decision layer
**Best for:** balancing correctness, quality, latency, cost, context and operational risk.

First apply hard feasibility constraints: correctness, security, provenance, reproducibility and acceptance. Then compare feasible candidates on a Pareto frontier. A policy preference may select among non-dominated candidates using context-specific weights.

Dynamic utility: weights are versioned decision context; the raw objective vector remains intact for future re-evaluation.

## 4. Dynamic utility contract

Do not use one opaque score as the system of record.

Store a raw outcome vector:

~~~text
U = [quality, acceptance, reproducibility, time, compute_cost, inference_cost,
     human_effort, retries, conflicts, context_cost, risk]
~~~

Then apply:

1. **Feasibility:** hard gates for correctness, security, policy and evidence completeness.
2. **Normalization:** versioned, cohort-specific scaling with explicit units.
3. **Pareto filtering:** preserve non-dominated candidates.
4. **Preference selection:** use a versioned utility profile for the current objective.
5. **Uncertainty:** report sample size, interval, missingness and evaluator confidence.
6. **Promotion:** require repeat evidence and dual-gate/task-outcome acceptance.

Illustrative constrained utility:

~~~text
score = wq·quality + wr·reproducibility + wi·integration
        - wt·time - wc·total_cost - wh·human_effort - wx·risk
~~~

Weights are configuration, not truth. Keep each raw dimension and its provenance.

## 5. Versioning and identity

Use separate immutable identifiers:

- experiment_id + experiment_version for the DoE design.
- tournament_id + cohort_id for the canonical manager.tournament.v1 comparison.
- treatment_id for factor-level combination.
- manager_id + policy_hash and manager policy version.
- task_id + task version.
- run_id + run_attempt.
- evaluator_id + evaluator_version.
- environment_fingerprint.
- artifact_digest.

A changed prompt, topology, factor assignment, evaluator, environment or acceptance rule creates a new version. Historical records remain immutable. The canonical manager cohort schema remains the identity anchor; DoE design records extend it.

## 6. Execution lifecycle

~~~text
DRAFT → PREREGISTERED → ADMITTED → ASSIGNED → RUNNING → OBSERVED
      → EVALUATED → COMPARED → PROMOTION_PROPOSED
      → PROMOTED | HELD | REJECTED
~~~

Execution outcomes remain separate: SUCCEEDED, FAILED, CANCELLED, TIMED_OUT, INCOMPLETE, SKIPPED.

A queued task is admitted, not executed. A successful process is executed, not necessarily accepted. A passing evaluation is validated for its declared scope, not automatically promoted.

## 7. Termux-first deployment profile

- Python stdlib-compatible core for portability.
- SQLite WAL for local transactional state and append-only event tables.
- JSONL for portable receipts and evidence export.
- Git worktrees for repository isolation.
- Optional Docker/Podman for reproducible worker environments.
- GitHub Actions adapter for hosted CI execution.
- MCP/A2A adapters behind explicit capability and identity contracts.
- Optional object storage for large artifacts; keep hashes and manifests local.
- Offline operation with deferred sync and idempotent reconciliation.

The core scheduler must work without cloud accounts, paid observability vendors or a permanently running server.

## 8. Security and reliability

- Default-deny tool and filesystem permissions.
- Explicit per-task read/write sets.
- Secret injection at runtime only.
- Redact event attributes before persistence/export.
- Treat fingerprints as pseudonyms, not anonymization.
- Lease fencing for stale workers.
- Idempotency keys for dispatch and artifact publication.
- Bounded retries with preserved attempt history.
- Independent judge/evaluator role.
- Immutable manifests and SHA-256 artifact digests.
- Human approval only at declared high-impact boundaries.

## 9. Implementation sequence

1. Map existing manager tournament schema, DoE helpers, trial/tournament pipeline and replay simulator; retain current SSOTs.
2. Define a supplemental versioned experiment-design manifest that references manager.tournament.v1.
3. Add validators only for missing fields/invariants; avoid duplicate cohort schemas.
4. Connect design assignments to the existing DoE helpers.
5. Add deterministic local runner fixtures and matched cohorts.
6. Extend manager policy adapter and lease/write-set contract.
7. Add independent quality evaluator and Pareto reducer.
8. Add randomized/factorial assignment and preregistration.
9. Add sequential allocation after baseline evidence exists.
10. Add optional Actions, MCP/A2A, container and telemetry adapters.
11. Add dashboard projections only after canonical receipts and reducers stabilize.

## 10. Decision

Adopt the hybrid: event-sourced ledger + versioned DAG + manager/worker policies + actor leases + blackboard evidence + DoE planner + Pareto utility. Add bandit/Bayesian/evolutionary allocation as policy modules behind stable contracts.

Reuse existing manager.tournament.v1, DeepCLI DoE/trial/tournament and evolutionary replay implementations. This gives dynamic utility without creating a parallel source of truth.


## 11. SIE and classifier graph operating system

The **Self-Improvement Engine (SIE)** owns the bounded evidence-to-improvement cycle: observe, diagnose, preregister a challenger, execute matched treatments, evaluate, compare, record and promote/hold/reject. See SELF-IMPROVEMENT-ENGINE.md and OPERATING-SYSTEM.md.

The 70+ classifier population is a capability registry. Compare individual classifiers laterally, then measure conditional error overlap and complementary strengths. Candidate routes are DAGs, not a mandatory linear chain: fan-out independent classifiers, join evidence by stable candidate ID, evaluate, and route/escalate only when declared predicates require it. Mev/Jev/Kev/Laya remain the current functional-role baseline adapter, not the classifier system's fixed topology. See CLASSIFIER-GRAPH-TOURNAMENT.md.

Tournament implementation versions compete as complete policies (manager + router + graph + scheduler + evaluator + evidence/promotion rules). Classifier and graph tournaments are component-level experiments and ablations inside that larger competition.

## 12. Current implementation audit

Source inspection found that trial.py executes producer, critic and verifier loops sequentially. It independently filters successful artifact/Jev/Kev lists, while Laya joins them with positional zip; partial failures can therefore shift candidate alignment. The next implementation slice should introduce stable candidate IDs and keyed joins, explicit node status, and partial-evidence retention before parallel graph scheduling. This is a source-inspection finding; runtime test confirmation remains pending.
