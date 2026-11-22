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

## 7. Current gaps to close

1. Add stable candidate IDs and evaluator joins to the current Mev/Jev/Kev/Laya trial path.
2. Preserve nulls for absent cost, latency, score and success observations.
3. Add classifier capability registry with schema/version/evidence metadata.
4. Add graph manifest and DAG scheduler adapter.
5. Add independent evaluator ensemble and Pareto reducer.
6. Connect deterministic replay to matched-cohort challenger comparisons.
7. Add canary/rollback receipts after offline evidence supports promotion.

## 8. Source references

- Existing manager comparison: `docs/research/MANAGER-TOURNAMENT-CONTRACT.md`
- Existing canonical cohort: `docs/ops/MANAGER-TOURNAMENT.schema.json`
- Existing team optimization model: `docs/ops/AGENT-TEAM-ORCHESTRATION.md`
- Existing throughput observations: `docs/ops/AGENT-THROUGHPUT-METRICS.md`
- Existing replay/evolution: `docs/ops/EVOLUTIONARY-REPLAY.md`
- Classifier and routing comparison: `CLASSIFIER-GRAPH-TOURNAMENT.md`
- Self-improvement controller: `SELF-IMPROVEMENT-ENGINE.md`
