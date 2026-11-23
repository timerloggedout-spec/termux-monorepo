# DoE Tournament Operating System

**Purpose:** govern the lifecycle of versioned tournament implementations and discover stronger classifier/routing compositions through evidence.

## 1. System boundary

The operating system contains six planes:

1. **Intent plane:** goal, task contract, success criteria, constraints and approval boundary.
2. **Registry plane:** classifier, agent, provider, model, evaluator, adapter and implementation versions.
3. **Experiment plane:** cohorts, factors, assignment, controls, repetitions, budgets and stopping rules.
4. **Execution plane:** DAG scheduler, admission, leases, isolated worktrees and adapters.
5. **Evidence plane:** append-only events, receipts, artifact hashes, provenance and evaluator results.
6. **Evolution plane:** comparison, diagnosis, challenger creation, promotion, canary and rollback.

SIE coordinates these planes as the evidence-to-improvement controller.

## 2. The three competitions

Keep three leaderboards and their units separate:

| Competition | Unit | Question |
|---|---|---|
| Capability tournament | classifier/version | Which classifier is strongest for this task contract? |
| Composition tournament | routing/graph version | Which combination discovers and uses complementary strengths best? |
| Implementation tournament | full tournament implementation/version | Which complete operating policy produces the best validated integrated outcome? |

The implementation tournament is primary. It can include the other two as controlled factors or ablation studies.

## 3. End-to-end operating cycle

~~~mermaid
flowchart TB
  GOAL[Goal + task contract] --> REG[Versioned registries]
  REG --> DESIGN[Preregistered DoE]
  DESIGN --> COHORT[Matched cohort + assignment]
  COHORT --> SCHED[Admission + DAG scheduler]
  SCHED --> GRAPH[Candidate classifier graphs]
  GRAPH --> RUN[Isolated execution]
  RUN --> RECEIPT[Events + receipts + artifacts]
  RECEIPT --> EVAL[Independent evaluation]
  EVAL --> COMPARE[Statistics + Pareto comparison]
  COMPARE --> DECIDE{Promotion gates}
  DECIDE -->|Pass| CANARY[Canary + monitor]
  DECIDE -->|Hold / reject| ARCHIVE[Preserve candidate + evidence]
  CANARY -->|Healthy| INC[New incumbent]
  CANARY -->|Regress| ROLLBACK[Rollback]
  INC --> SIE[SIE diagnosis + next hypothesis]
  ARCHIVE --> SIE
  ROLLBACK --> SIE
  SIE --> DESIGN
~~~

## 4. Version dimensions

Version separately:

- tournament implementation and manager policy;
- graph topology and router policy;
- classifier catalog snapshot and classifier versions;
- task contract and cohort;
- evaluator suite, rubrics and reducer;
- environment, tools and execution adapters;
- budgets, retries, concurrency and safety policy.

Any semantic change creates a new version and a new comparison record. Historical runs remain immutable.

## 5. Experiment design

Start with matched, blocked, randomized cohorts. Include a fixed incumbent control. Screen individual classifiers first, then test complementarity and selected graph combinations. Use full factorial only for small factor counts; use fractional designs when aliasing is documented; use sequential allocation after baseline variance and enough observations exist.

Keep a held-out cohort for robustness. Keep a randomized exploration share during adaptive routing. Record all exclusions, failures, unavailable arms and deviations.

## 6. Promotion policy

Promotion requires all of:

- hard safety/security/privacy gates pass;
- task outcome and integration acceptance pass;
- evidence and provenance are complete;
- evaluator and environment versions are pinned;
- held-out and repeated evidence meets the preregistered rule;
- Pareto/utility comparison supports the candidate under the current preference profile;
- rollback target and canary plan exist.

Promotion weighs throughput, nominal cost, classifier count and judge confidence alongside correctness, acceptance, reproducibility and safety gates.

## 7. Implemented operating-system contracts

### Inventory and identity

- The System One catalog contains 88 entries: 61 model families, 16 adapters, 7 runtimes and 4 directories.
- The classifier graph registry covers all 61 model entries and all 27 infrastructure entries by their declared catalog layer.
- Five model candidates retain the role mapping supported by census/trial evidence. Fifty-six retain `unclassified` status pending source-backed capability qualification.
- Every model candidate carries the catalog's exact claim text and source URL. Catalog claims and verified capability evidence remain separate fields.
- The classifier operating estate contains 71 units across 12 source-defined groups: 43 live, 26 dormant and 2 dead in the 2026-11-02 feed snapshot. Group counts reconcile against all source rows. Estate units describe operating systems, pipelines, routing, gates, feeds and external surfaces.
- The `model-catalog-screen` graph holds 61 model candidates as a parallel, design-only qualification arm. The `local-role-lateral-screen` holds Mev, Jev, Kev and Laya as four independent design-only arms; `local-role-baseline` preserves the current incumbent composition as a separate graph.

### Candidate admission

`scripts/ci/classifier_candidate_admission.py` emits a deterministic
`classifier.candidate-admission-report.v1` report. Four local role
implementations qualify as incumbent baselines. The previously evaluated
self-hosted Laya route qualifies for replication. External TypeSafe Jev
requires owner approval for the paid route; external Kev requires its
serving composition; recruiting Mev awaits a runnable release; Mellow mev
awaits host/egress readiness. The remaining 56 model candidates await
capability qualification.

### Registry and experiment plan

- Registry: `config/classifier_graph_registry.json`, version `0.9.0`.
- Registry schema: `docs/ops/CLASSIFIER-GRAPH-REGISTRY.schema.json`.
- Experiment plan: `config/classifier_tournament_experiment_plan.json`.
- Experiment schema: `docs/ops/CLASSIFIER-TOURNAMENT-EXPERIMENT-PLAN.schema.json`.
- Offline validation: `scripts/ci/classifier_graph_registry_validator.py`.
- Admission tests: `scripts/ci/test_classifier_candidate_admission.py`.
- Registry tests: `scripts/ci/test_classifier_graph_registry_validator.py`.

The five experiment phases are inventory qualification, lateral capability
screen, graph composition, tournament implementation comparison, and
promotion/canary. The plan preserves four independent comparison units:
classifier capability, routing policy, composition graph and tournament
implementation. Its status remains `design_only` until candidate-specific
admission gates pass.

### Tournament implementation competition

The registry pins the incumbent manager implementation against the SIE
control-plane challenger under the canonical `manager.tournament.v1`
cohort contract. The challenger remains design-only while its scheduler,
receipt-ledger, evaluator and promotion-controller integrations mature.

The executable comparison component is
`deepcli.observatory.implementation_competition@0.3.0`, with CLI
`scripts/tournament/compare_implementations.py`, with receipt schema `docs/ops/TOURNAMENT-IMPLEMENTATION-RECEIPT.schema.json`. It requires exact matched
task IDs, cohort, task contract, environment fingerprint and evaluator
version. It computes paired deltas, sample counts and 95% intervals using
Student-t critical values for small samples. Zero-observed-variance
intervals remain unestimated. Each receipt declares the same `metric_set`;
every declared key appears in `metrics`, with `null` for unobserved values.
Fully unobserved and partially observed dimensions block dominance.
Hard-gate failures block recommendations. Dominance requires complete paired
coverage, an estimated interval for every declared metric, interval-supported
non-regression and positive improvement on at least one. Recommendations route
to human review; held-out validation, owner approval and rollback lineage
remain separate promotion gates.

Run the operating-system checks from the repository root:

```bash
python scripts/ci/classifier_graph_registry_validator.py
python scripts/ci/classifier_candidate_admission.py
python -m unittest scripts/ci/test_classifier_graph_registry_validator.py
python -m unittest scripts/ci/test_classifier_candidate_admission.py
python -m unittest discover -s deepcli/tests -p 'test_implementation_competition.py'
```

## 8. Remaining implementation gates

1. Qualify the 56 unclassified models with primary-source review, task capability contracts, license/usage decisions, checkpoint or service revisions, and adapter smoke evidence.
2. Pin immutable source revision, model/checkpoint digest, adapter version and route authorization on each admitted candidate.
3. Implement candidate-specific execution adapters and dependency-aware graph scheduling.
4. Connect independent evaluator ensembles and append-only run receipts to the existing leaderboard and replay paths.
5. Run role-matched capability screens, graph ablations and matched manager-version cohorts with held-out tasks.
6. Add canary and rollback receipts after offline evidence supports promotion.

## 9. Source references

- Existing manager comparison: `docs/research/MANAGER-TOURNAMENT-CONTRACT.md`
- Canonical cohort: `docs/ops/MANAGER-TOURNAMENT.schema.json`
- Team optimization model: `docs/ops/AGENT-TEAM-ORCHESTRATION.md`
- Throughput observations: `docs/ops/AGENT-THROUGHPUT-METRICS.md`
- Replay/evolution: `docs/ops/EVOLUTIONARY-REPLAY.md`
- Classifier and routing comparison: `CLASSIFIER-GRAPH-TOURNAMENT.md`
- SIE controller: `SELF-IMPROVEMENT-ENGINE.md`
- Matched implementation comparison: `docs/ops/TOURNAMENT-IMPLEMENTATION-COMPETITION.md`
