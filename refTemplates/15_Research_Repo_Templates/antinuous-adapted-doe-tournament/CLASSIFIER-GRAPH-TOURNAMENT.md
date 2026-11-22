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

## 2. Mev / Jev / Kev / Laya relationship

Repository source inspection establishes these current role contracts:

| Role | Current module | Current responsibility |
|---|---|---|
| Mev | `deepcli/deepcli/observatory/mev.py` | producer; captures provider/model output |
| Jev | `deepcli/deepcli/observatory/jev.py` | critic; rubric-based LLM judge; judge differs from producer |
| Kev | `deepcli/deepcli/observatory/kev.py` | verifier; compares output against reference (currently exact/token-F1) |
| Laya | `deepcli/deepcli/observatory/laya.py` | merger; weighted rank over Jev/Kev evidence |

These are useful **local functional roles** in the current trial implementation. The System One Catalog documents Mev, Jev, Kev and Laya as namesakes in the external ecosystem; the local deepcli classes implement producer/critic/verifier/merger roles and are not deployments of those named projects. Their names do not imply a mandatory serial pipeline for the broader classifier ecosystem.

Model the capabilities as a directed acyclic graph with fan-out and fan-in. A producer can feed several independent classifiers; critics, verifiers and specialist classifiers can run in parallel; a router can select a subset; a merger can consume identity-aligned evidence; a judge can request another specialist only when an evidence gap justifies it.

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

The graph is a plan, not a hardcoded sequence. The scheduler admits independent nodes concurrently and waits only at declared dependency edges. A treatment can compare a serial baseline, parallel fan-out, conditional cascade, voting ensemble, specialist delegation, or hybrid graph.

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

## 7. Current code audit — evidence-backed issues

The existing `docs/ops/CLASSIFIER-TRIAL-DISPATCH.md` already records this known follow-up; source inspection confirms the code path described there:

1. `trial.py` executes provider production in a sequential loop, then executes Jev and Kev loops sequentially. This is a valid baseline implementation, not a graph scheduler.
2. `trial.py` independently filters successful artifacts, Jev records and Kev records before passing the three arrays to Laya. Laya uses `zip()`. A failed record in one list can shift positional correspondence and attach another candidate's evaluation to an artifact.
3. `kev.py` currently implements exact and token-F1 comparison. These are lexical reference checks, not a general semantic classifier evaluator.
4. `laya.py` currently applies a weighted Jev/Kev scalar (default 0.7/0.3). This is a baseline reducer, not a calibrated, uncertainty-aware Pareto decision engine.
5. `leaderboard.py` stores role/task/provider/model aggregates and uses default numeric values for several absent observations. That behavior requires a migration/validation boundary before it serves as the canonical experiment evidence plane.

This is an existing documented steward backlog item, not a newly discovered defect. Runtime regression coverage remains a prerequisite for the graph scheduler work.

### Required repair before expanding graph search

Introduce stable candidate records, for example:

`candidate_id, producer_id, classifier_id, graph_node_id, run_id, attempt, output_ref, status`

Attach every Jev/Kev/other evaluator record to the same `candidate_id`. Use explicit status values such as `completed`, `failed`, `skipped`, `timed_out`, `unavailable`, `not_applicable`. Preserve partial evidence and make reducers reject ambiguous joins. Keep the current Mev/Jev/Kev/Laya path as a baseline adapter during migration.

## 8. External routing references

- RouteLLM provides an open framework for training, serving and evaluating multiple router strategies against benchmarks: https://github.com/lm-sys/RouteLLM
- RouterBench establishes multi-model routing comparison with large inference-outcome corpora: https://arxiv.org/abs/2403.12031
- LLMRouterBench provides a unified evaluation framework and highlights model complementarity, pool composition and the risk of simplistic routing baselines: https://arxiv.org/abs/2601.07206
- TwinRouterBench targets step-level routing in long-horizon agent trajectories and combines static router iteration with end-to-end execution evaluation: https://arxiv.org/abs/2605.18859
- Who Routes the Router analyzes task diversity, model-pool balance and evaluation methodology as major determinants of router conclusions: https://openreview.net/pdf?id=EEPostHMtF

These are design and benchmark references, not evidence that their results transfer directly to this repository's 70+ classifier pool.


## 9. Canonical classifier inventory

Use `config/system_one_catalog.json` (schema `system-one-catalog/1`) and `docs/ops/SYSTEM-ONE-CATALOG.md` as the existing inventory authority. The catalog document reports 88 entries: 61 model families, 16 adapters, 7 runtimes and 4 directories. Track lifecycle as referenced → catalogued → trial_candidate → evaluated, with firsthand evidence at each transition. Count each entry in exactly one layer. Treat directory entries as discovery aids, runtime entries as execution surfaces, adapters as techniques and model entries as model families. The trial quartet's local roles remain separate from same-named external projects.
