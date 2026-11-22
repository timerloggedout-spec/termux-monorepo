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

Throughput, low nominal cost, classifier count and judge confidence alone cannot promote an implementation.

## 7. Implemented registry slice and remaining gaps

The first versioned registry slice is now present:
- `scripts/ci/classifier_candidate_admission.py` produces a deterministic admission report. Four local role baselines and the previously evaluated Laya route are eligible for role-matched baseline/replication trials; 56 unclassified model entries remain outside execution. TypeSafe Jev remains owner-paid gated, Kev requires serving composition, recruiting Mev lacks a runnable release, and Mellow mev remains host/egress blocked.

- `config/classifier_graph_registry.json` registers the four local role implementations and five catalog-backed namesake candidates as distinct identities.
- The registry points to the separate `ops/classifiers/classifiers-feed.json` snapshot: 71 estate units (43 live, 26 dormant, 2 dead) as of 2026-11-02. These units include heterogeneous classifier systems, pipelines, routing, review, gate and feed surfaces; they are not 71 interchangeable model candidates.
- `docs/ops/CLASSIFIER-GRAPH-REGISTRY.schema.json` defines the registry contract.
- `scripts/ci/classifier_graph_registry_validator.py` checks candidate/catalog references, role compatibility, local source paths, graph node identity, DAG acyclicity and the pinned classifier-estate census counts.
- `scripts/ci/test_classifier_graph_registry_validator.py` covers valid input, unknown catalog entries, role mismatch, dependency cycles and duplicate node IDs.
- The registry points to `manager.tournament.v1` for cohort identity. The typed-decision candidate screen is design-only until candidate-specific adapters and matched trials exist.

Run the offline validator from the repository root:

```bash
python scripts/ci/classifier_graph_registry_validator.py
python -m unittest scripts/ci/test_classifier_graph_registry_validator.py
```

Remaining implementation gaps:

1. Reconcile the 71-unit classifier-estate feed with current Tier-1 steward records and preserve its separate state vocabulary. Expand model candidates from the verified model layer while retaining pipeline, routing, gate and infrastructure units as integration surfaces.
2. Add immutable source revision, model/checkpoint digest, adapter version and capability evidence to each trial candidate.
3. Implement graph execution adapters and dependency-aware scheduling; the current registry records topology and the local baseline still executes through its existing runner.
4. Replace the scalar-only reducer with independent evaluator evidence, uncertainty-aware Pareto comparison and a versioned preference profile.
5. Connect deterministic replay to matched-cohort challenger comparisons.
6. Add canary/rollback receipts after offline evidence supports promotion.
7. Preserve nulls for absent cost, latency, score and success observations in the leaderboard/evidence migration.

## 8. Source references

- Existing manager comparison: `docs/research/MANAGER-TOURNAMENT-CONTRACT.md`
- Existing canonical cohort: `docs/ops/MANAGER-TOURNAMENT.schema.json`
- Existing team optimization model: `docs/ops/AGENT-TEAM-ORCHESTRATION.md`
- Existing throughput observations: `docs/ops/AGENT-THROUGHPUT-METRICS.md`
- Existing replay/evolution: `docs/ops/EVOLUTIONARY-REPLAY.md`
- Classifier and routing comparison: `CLASSIFIER-GRAPH-TOURNAMENT.md`
- Self-improvement controller: `SELF-IMPROVEMENT-ENGINE.md`

## 8. Full inventory and implementation competition

The registry now covers the full System One catalog by layer:

- 61 model-layer entries are registered as classifier candidates.
- 56 remain `unclassified`; their catalog presence establishes an inventory identity, not a proven capability or runnable endpoint.
- Five S1 candidates retain the narrower role mapping supported by the existing census and trial records.
- 27 adapter, runtime and directory entries remain infrastructure references, outside model counts.
- The separate classifier-estate feed retains its 71 operating units and live/dormant/dead state counts.

The `model-catalog-screen` graph contains all 61 model candidates as a design-only parallel screening arm. Candidate admission requires a capability contract, execution adapter, source/checkpoint identity, permitted route and evidence plan. The graph is inventory-complete and execution-gated.

Tournament implementation versioning is recorded separately from classifier and graph versioning in `implementation_competition`:

- The incumbent pins the canonical `manager.tournament.v1` cohort contract and source components for trial execution, evidence reduction, leaderboard and replay.
- The SIE control-plane challenger is `design_only`; its hypothesis and source document are versioned while execution readiness remains false.
- Promotion compares complete implementation versions on matched cohorts, held-out tasks, independent evaluators and immutable receipts. Every promotion carries a rollback target and production approval gate.

The competition unit is explicit: classifier capability, composition graph, routing policy or tournament implementation. Results across these populations remain separately attributable.

