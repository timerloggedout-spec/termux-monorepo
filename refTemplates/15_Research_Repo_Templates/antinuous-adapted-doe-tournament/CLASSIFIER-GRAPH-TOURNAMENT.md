# Classifier Graph Tournament

**Contract:** classifier.graph-tournament.v1 (proposed)  
**Parent cohort:** manager.tournament.v1  
**Purpose:** compare classifier capabilities laterally, discover individual strengths, and evolve useful routing/composition graphs.

## 1. Correct comparison unit

The tournament's primary competitor is a **versioned implementation**: a manager policy, routing policy, graph topology, classifier selection, evaluator configuration and execution contract treated as one reproducible candidate.

The System One catalog is the source inventory for the wider classifier work: the current catalog document reports 88 entries (61 model families, 16 adapters, 7 runtimes and 4 directories). The model and adapter entries form the relevant capability population; runtimes execute other entries and directories index them. The 70+ shorthand therefore refers to the broader classifier ecosystem, not 88 interchangeable classifiers. It is not a single serial chain and it is not the tournament leaderboard. A classifier can compete alone, serve a specialist node, participate in an ensemble, or be selected conditionally by a router.

Compare three distinct levels:

1. **Classifier capability:** a classifier's measured behavior on a declared task family and label/evidence contract.
2. **Composition / route:** a graph that selects, combines, cross-checks or escalates among capabilities.
3. **Tournament implementation:** the versioned manager, scheduler, router, graph, evaluators and execution policies that produce the integrated outcome.

Keep classifier identity, provider/model identity, execution identity and manager identity separate.

## 2. Mev / Jev / Kev / Laya: role labels, local implementations, external candidates

Keep four identity layers distinct:

| Layer | Meaning | Examples |
|---|---|---|
| Role contract | A capability slot | text generation, rubric critique, reference verification, evidence reduction |
| Local implementation | Code implementing that role | `observatory/mev.py`, `jev.py`, `kev.py`, `laya.py` |
| External candidate | Independently developed model/service/runtime | TypeSafe Jev, Jared Palmer Kev, ConvAI Laya, Mellow AI Mev |
| Adapter | Protocol bridge | generic chat adapters; System One typed-decision adapter |

The local names are labels for roles, not evidence of code/model lineage. The external projects are candidates for evaluation, and some already have a distinct integration route. The System One adapter is typed: it implements `decide(state, questions)`; its `ask(prompt)` method raises `NotImplementedError`. Therefore a TypeSafe-compatible endpoint can participate in the typed-decision lane, while it is not automatically a drop-in Mev text producer or Jev chat judge. The current `decide_check` path checks a trial result or a standalone state; a candidate-aligned verifier adapter remains a separate implementation task.

The current local baseline responsibilities are:

| Local role | Current behavior | Limits to preserve in evaluation |
|---|---|---|
| Mev | Captures output from a text-generation provider/model | Provider adapter and model identity determine actual capability |
| Jev | Scores artifact text against a rubric using an independent LLM judge | Judge quality and rubric validity require separate measurement |
| Kev | Compares artifact with a reference using exact or token-F1 | Lexical agreement is not semantic correctness |
| Laya | Weighted reduction of aligned Jev/Kev evidence | Default 0.7/0.3 weights are a baseline preference, not a universal objective |

This role baseline is one tournament arm. It does not prescribe a mandatory serial chain for the wider classifier ecosystem. Model classifier capabilities as a directed acyclic graph with fan-out and fan-in. A producer can feed multiple independent classifiers; critics, verifiers and specialists can run concurrently; a router can select nodes conditionally; a merger consumes evidence joined by stable candidate identity.

~~~mermaid
flowchart TD
  TASK[Task + contract] --> ROUTER[Versioned router]
  ROUTER -->|select / fan-out| CAP[Classifier capability pool]
  CAP --> C1[Classifier A]
  CAP --> C2[Classifier B]
  CAP --> C3[Classifier C]
  CAP --> CN[Classifier N]
  C1 --> EV[Evidence join by candidate ID]
  C2 --> EV
  C3 --> EV
  CN --> EV
  EV --> JUDGE[Independent evaluator set]
  JUDGE --> MERGE[Versioned composition / merger]
  MERGE --> OUT[Outcome + provenance]
  OUT --> SIE[Self-Improvement Engine]
  SIE --> ROUTER
~~~

The graph is a plan, not a hardcoded sequence. The scheduler admits independent nodes concurrently and waits only at declared dependency edges. A treatment can compare the current local baseline, parallel fan-out, conditional cascade, voting ensemble, specialist delegation, or hybrid graph.

## 2A. Classifier estate and operational status

The repository's classifier estate feed records **71 operating units** in
its 2026-11-02 snapshot: 43 live, 26 dormant and 2 dead. Its units span
observatory, ML pipelines, model selection/routing, Delphi, repo gates,
workflow review, intake, repository observatory, dashboards, provider
substrate and external surfaces. This is the operating estate census;
each row is a system/unit, not an interchangeable model candidate.

The System One catalog is a separate inventory: 88 entries across 61
model families, 16 adapters, 7 runtimes and 4 directories. Preserve the
layer distinction when deriving candidate pools.

| Operating group | Units | Live | Dormant | Dead |
|---|---:|---:|---:|---:|
| deepcli observatory | 3 | 3 | 0 | 0 |
| ml/pipelines | 7 | 1 | 6 | 0 |
| model selection / routing | 5 | 2 | 3 | 0 |
| Delphi system | 9 | 5 | 4 | 0 |
| repo gates & audits | 9 | 5 | 4 | 0 |
| workflow triage / review | 14 | 7 | 5 | 2 |
| intake classifiers | 6 | 6 | 0 | 0 |
| repository observatory | 2 | 1 | 1 | 0 |
| dashboard / feed classifiers | 4 | 3 | 1 | 0 |
| provider substrate | 4 | 3 | 1 | 0 |
| external surfaces | 6 | 6 | 0 | 0 |
| post-recon steward builds | 2 | 1 | 1 | 0 |
| **Total** | **71** | **43** | **26** | **2** |

**Jev status is scope-dependent:**

- Local `deepcli.observatory.jev` is part of the incumbent trial role set.
  The estate feed calls the quartet live via dispatch; the Tier-1 recon
  defines that as human-dispatched execution, with no standing trigger
  classifying repository LLM traffic.
- External TypeSafe Jev (S1-01) is catalogued, while its hosted route is
  blocked-paid in the census trial record. The free-only gate prevented
  an external Jev trial; owner approval is the admission prerequisite.
- External ConvAI Laya (S1-03) has a self-hosted evaluation record:
  quality 0.7139 and grounding 0.7692 on the recorded trial state.
- External Jared Palmer Kev (S1-02) remains a trial candidate pending its
  compatible LoRA-plus-head serving composition.

The registry stores `readiness` and `operational_state` separately.
Catalog presence, adapter availability, dispatch activity and measured
evaluation each represent different evidence.

## 3. Candidate tournament arms

Use small, interpretable families before searching arbitrary graphs:

- **Single-capability baseline:** one eligible classifier selected by a fixed policy.
- **Static parallel ensemble:** fixed set of classifiers with a declared reducer.
- **Capability-routed:** select a specialist from task features and capability evidence.
- **Conditional cascade:** run a low-cost capability first; escalate when uncertainty or a declared failure predicate crosses a threshold.
- **Independent verification:** producer and verifier are distinct; verifier sees the task contract and required reference, not hidden answers unavailable at runtime.
- **Committee / voting:** diverse classifiers return independently; a reducer resolves agreement, disagreement and abstention.
- **Manager-delegated graph:** a manager decomposes the task, assigns specialists and integrates outputs.
- **Adaptive graph:** a versioned policy chooses nodes/edges using past cohort evidence while retaining randomized exploration.

Each arm declares its graph, selection rule, node budgets, concurrency, timeout, retry, abstention and stopping policy.

## 4. Classifier registry contract

Every classifier entry should expose:

- immutable `classifier_id`, `classifier_version`, implementation digest and owner/source provenance;
- task families, input/output schemas, label ontology and supported languages/domains;
- capability claims with evidence references and confidence;
- invocation adapter, resource requirements, privacy/data handling class and safety constraints;
- calibration, coverage, abstention and known failure modes;
- measured quality vector by cohort, dataset, environment and evaluator version;
- availability lifecycle: discovered, eligible, experimental, admitted, suspended, retired.

A registry claim is a routing hint until a matched cohort validates it. Classifiers with incompatible output contracts require an explicit adapter and versioned mapping.

## 5. Fair comparison protocol

1. Freeze task contract, cohort, labels/references, environment, classifier catalog snapshot and evaluator versions.
2. Build blocks by task family, complexity, language, risk and input shape.
3. Assign classifier and graph treatments within blocks using recorded randomization and seed.
4. Keep a fixed incumbent/control arm and a held-out robustness cohort.
5. Record every selected, skipped, unavailable and failed node with a reason.
6. Join node outputs and evaluator records by stable `candidate_id` and `run_id`, never array position.
7. Evaluate individual capability, graph composition and end-to-end integrated outcome separately.
8. Preserve disagreements, abstentions, missing evidence and failed attempts as first-class observations.
9. Promote only after feasibility, repeatability, held-out and operational gates pass.

### Outcome vector

Preserve per-classifier and per-graph observations:

`correctness, coverage, calibration, precision, recall, F1, abstention, disagreement, robustness, latency, inference_cost, compute_cost, context_cost, retries, failures, conflicts, human_effort, provenance_confidence`

Select metrics that match the classifier's actual contract. Missing values remain null. A single composite is a view, never the evidence record.

## 6. Composition discovery

Discover strengths through a staged search:

- **Screen:** measure individual classifiers against representative task blocks.
- **Complementarity:** compute conditional error overlap and disagreement; identify capabilities that repair one another's failures.
- **Compose:** test a limited candidate set of graph patterns and reducers.
- **Route:** train or configure routing policies from out-of-fold capability evidence.
- **Stress:** evaluate shifted, adversarial, sparse and held-out cohorts.
- **Evolve:** mutate one graph/policy dimension at a time where possible; preserve parent lineage and compare against the incumbent.
- **Promote:** require measured end-to-end gain and operational feasibility.

Avoid selecting ensembles solely because member classifiers have high standalone scores. Complementarity, calibration, routing mistakes and combination overhead determine whether the graph improves the result.

## 7. Current code audit — verified baseline and current correction

1. `trial.py` executes provider production, critique and reference verification in separate loops. This is the current local baseline runner, not a concurrent DAG scheduler.
2. The earlier implementation filtered the three evidence arrays independently before Laya's positional zip. The tournament branch now assigns candidate IDs, preserves one stage result per candidate, rejects mismatched identities and excludes incomplete evidence triples. Regression cases cover direct identity mismatch and a partial Jev failure in a multi-candidate trial.
3. `kev.py` implements exact and token-F1 comparison. These are lexical reference checks, not a general semantic classifier evaluator.
4. `laya.py` applies a weighted Jev/Kev scalar (default 0.7/0.3). This remains a baseline reducer, not a calibrated, uncertainty-aware Pareto decision engine.
5. `leaderboard.py` stores role/task/provider/model aggregates and applies numeric defaults to absent observations. It remains a convenience ranking surface, not the canonical experiment evidence plane.

The candidate-identity correction is committed in this branch. Test execution remains pending CI. The next architecture step is a versioned capability graph manifest and scheduler, preserving the local baseline as an incumbent control.

### Current evidence contract

Each candidate stage record carries `candidate_id` and explicit `ok` state. Reducers require equal-length vectors and matching IDs, preserve excluded candidate details, and rank only complete evidence triples. The graph-level contract extends this with `run_id`, `graph_node_id`, attempt, status, artifact reference and immutable implementation identity.

## 8. External routing references

- RouteLLM provides an open framework for training, serving and evaluating multiple router strategies against benchmarks: https://github.com/lm-sys/RouteLLM
- RouterBench establishes multi-model routing comparison with large inference-outcome corpora: https://arxiv.org/abs/2403.12031
- LLMRouterBench provides a unified evaluation framework and highlights model complementarity, pool composition and the risk of simplistic routing baselines: https://arxiv.org/abs/2601.07206
- TwinRouterBench targets step-level routing in long-horizon agent trajectories and combines static router iteration with end-to-end execution evaluation: https://arxiv.org/abs/2605.18859
- Who Routes the Router analyzes task diversity, model-pool balance and evaluation methodology as major determinants of router conclusions: https://openreview.net/pdf?id=EEPostHMtF

These are design and benchmark references, not evidence that their results transfer directly to this repository's 70+ classifier pool.


## 9. Canonical classifier inventory

Use `config/system_one_catalog.json` (schema `system-one-catalog/1`) and `docs/ops/SYSTEM-ONE-CATALOG.md` as the existing inventory authority. The catalog document reports 88 entries: 61 model families, 16 adapters, 7 runtimes and 4 directories. Track lifecycle as referenced → catalogued → trial_candidate → evaluated, with firsthand evidence at each transition. Count each entry in exactly one layer. Treat directory entries as discovery aids, runtime entries as execution surfaces, adapters as techniques and model entries as model families. The trial quartet's local roles remain separate from same-named external projects.

## 2B. Full catalog screening boundary

The registry covers all 61 model-layer entries in `config/system_one_catalog.json`.
It records five S1 candidates with the role mapping supported by the
existing census/trial evidence. The remaining 56 are explicitly
`unclassified`: their catalog records provide identity and source
provenance, while task capability and runnable adapter remain open
qualification work.

The 27 adapter, runtime and directory entries are recorded in a separate
infrastructure collection. The 71-unit classifier-estate feed remains a
third inventory, describing operating systems and workflow surfaces.
These three inventories have different counting units and stay separate.

`model-catalog-screen` is a 61-node, parallel, design-only graph. It
defines the candidate screen boundary; it is not an execution claim.
A candidate enters a live cohort after capability mapping, source and
checkpoint pinning, adapter verification, route authorization, and
task-specific acceptance criteria.

## 2C. Tournament implementation competition

The registry also pins an incumbent implementation and SIE challenger:

- Incumbent: `incumbent.termux-manager-tournament@1.0.0`, with explicit
  source references for the canonical cohort contract, trial runner,
  reducer, leaderboard and replay simulator.
- Challenger: `challenger.sie-control-plane@0.1.0`, design-only and
  linked to the SIE architecture hypothesis.

Compare implementation versions as complete arms on the same
`manager.tournament.v1` cohort. Require held-out tasks, independent
evaluation, immutable run receipts, rollback lineage and owner approval
for production promotion. Component ablations attribute gains after
the complete-arm comparison.

