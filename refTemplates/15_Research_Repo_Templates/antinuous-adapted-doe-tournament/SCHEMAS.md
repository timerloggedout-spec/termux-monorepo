# DoE Tournament — schema reference

The YAML and JSON examples below are reference contracts. The checked-in classifier graph registry and staged tournament experiment plan have dedicated JSON Schemas and offline CI validation.

## Experiment manifest

~~~yaml
schema: doe.experiment.v1
experiment_id: doe-manager-policy-screen
experiment_version: 1.0.0
title: Manager policy screening
objective: maximize validated integrated outcomes under bounded resource cost
hypothesis:
  statement: hybrid manager policies improve acceptance-adjusted utility
  status: preregistered
cohort:
  cohort_id: repo-task-cohort-2026q4
  task_manifest_digest: sha256:REPLACE_WITH_REAL_DIGEST
  blocking_factors: [complexity_band, language, risk_class]
design:
  type: randomized_blocked_factorial
  seed: 20261122
  control_treatment: sequential-baseline
  factors:
    - factor_id: manager_policy
      levels: [sequential, hierarchical, blackboard, hybrid]
    - factor_id: execution
      levels: [termux_local, github_actions]
    - factor_id: review
      levels: [single_judge, independent_dual_judge]
  allocation:
    mode: balanced
    exploration_fraction: 0.15
evaluation:
  evaluator_id: repo-acceptance
  evaluator_version: 1.0.0
  hard_gates: [correctness, security, evidence_provenance]
  objectives: [quality, reproducibility, integration_time, total_cost, human_effort]
budget:
  max_runs: 120
  max_compute_minutes: 600
  max_inference_cost_usd: 50
stopping:
  max_failures: 12
  require_held_out_validation: true
promotion:
  policy: pareto_then_preregistered_preference
  require_dual_gate: true
  require_task_outcome: true
~~~

## Treatment manifest

~~~yaml
schema: doe.treatment.v1
treatment_id: hybrid-termux-dualjudge
experiment_id: doe-manager-policy-screen
experiment_version: 1.0.0
factor_levels:
  manager_policy: hybrid
  execution: termux_local
  review: independent_dual_judge
manager_policy:
  policy_id: hybrid-manager
  policy_version: 0.3.0
provider_catalog:
  snapshot_digest: sha256:REPLACE_WITH_REAL_DIGEST
environment:
  target: termux
  fingerprint: sha256:REPLACE_WITH_REAL_DIGEST
prompt:
  template_id: tournament-manager
  template_version: 2.1.0
~~~

## Run receipt

~~~json
{
  "schema": "doe.run-receipt.v1",
  "experiment_id": "doe-manager-policy-screen",
  "experiment_version": "1.0.0",
  "tournament_id": "tournament-2026-11-22-001",
  "cohort_id": "repo-task-cohort-2026q4",
  "treatment_id": "hybrid-termux-dualjudge",
  "task_id": "task-00017",
  "task_version": "1.0.0",
  "run_id": "runner-generated-id",
  "run_attempt": 1,
  "head_sha": "full-git-commit-sha",
  "manager_policy_id": "hybrid-manager",
  "manager_policy_version": "0.3.0",
  "provider_id": null,
  "model_id": null,
  "execution_adapter": "termux-local",
  "environment_fingerprint": "sha256:...",
  "outcome": "SUCCEEDED",
  "started_at": "2026-11-22T00:00:00Z",
  "completed_at": "2026-11-22T00:03:00Z",
  "metrics": {
    "accepted": null,
    "quality_score": null,
    "integration_seconds": 180,
    "compute_cost_usd": null,
    "inference_cost_usd": null,
    "human_effort_seconds": null,
    "ates": null,
    "wtcv_per_min": null
  },
  "artifacts": [
    {
      "name": "result.json",
      "sha256": "sha256:...",
      "bytes": 1234,
      "media_type": "application/json"
    }
  ],
  "attribution_confidence": "high"
}
~~~

## Manager policy version

~~~yaml
schema: doe.manager-policy.v1
policy_id: hybrid-manager
policy_version: 0.3.0
parent:
  policy_id: hierarchical-manager
  policy_version: 0.2.0
roles:
  manager: [plan, allocate, sequence, escalate, stop]
  planner: [decompose, declare_dependencies, estimate]
  worker: [execute_declared_task, publish_artifacts]
  critic: [identify_gaps, challenge_claims]
  judge: [evaluate_against_frozen_rubric]
scheduling:
  mode: dependency_aware_dynamic_utility
  concurrency: capacity_and_independence_bounded
  lease_seconds: 900
  max_attempts: 2
isolation:
  worktree_per_task: true
  declared_write_set_required: true
  stale_lease_fencing: true
evidence:
  append_only: true
  require_manifest: true
  preserve_failures: true
~~~

## Event envelope

~~~json
{
  "schema": "doe.event.v1",
  "event_id": "uuid",
  "event_type": "execution.completed",
  "occurred_at": "2026-11-22T00:03:00Z",
  "experiment_id": "doe-manager-policy-screen",
  "experiment_version": "1.0.0",
  "tournament_id": "tournament-2026-11-22-001",
  "cohort_id": "repo-task-cohort-2026q4",
  "treatment_id": "hybrid-termux-dualjudge",
  "task_id": "task-00017",
  "run_id": "runner-generated-id",
  "run_attempt": 1,
  "producer": {
    "adapter": "termux-local",
    "agent_id": null,
    "manager_policy_id": "hybrid-manager",
    "manager_policy_version": "0.3.0"
  },
  "payload_digest": "sha256:..."
}
~~~

## Required invariants

- Unknown/unmeasured values remain null.
- Run and attempt identity is stable and unique in its namespace.
- Version references resolve to immutable manifests.
- Event timestamps are timezone-aware UTC.
- Artifact digest is verified before acceptance.
- Raw prompt/completion/tool payloads are excluded from exported receipts.
- Independent evaluators provide acceptance authority; manager self-scores remain separate observations.
- Provider identity and GitHub actor identity remain distinct.
- Every score links to evaluator version and source evidence.
- Every promotion links to a tournament version and exact candidate evidence set.


## Runtime classifier registry

The first checked-in registry uses `classifier.graph-registry.v1`:

- Registry data: `config/classifier_graph_registry.json`
- JSON Schema: `docs/ops/CLASSIFIER-GRAPH-REGISTRY.schema.json`
- Offline validator: `scripts/ci/classifier_graph_registry_validator.py`
- Validator tests: `scripts/ci/test_classifier_graph_registry_validator.py`

The registry separates role contracts, local implementations, catalog-backed candidates, and composition graphs. Catalog candidates refer to stable IDs in `config/system_one_catalog.json`; the registry keeps the catalog's heterogeneous layers intact. Local Mev/Jev/Kev/Laya roles are incumbent candidates. The similarly named external projects remain independent candidates with explicit adapter readiness. The typed-decision graph is design-only pending candidate-specific execution adapters and matched trials.

The registry separately pins `ops/classifiers/classifiers-feed.json`, a 71-unit estate snapshot generated 2026-11-02: 43 live, 26 dormant and 2 dead. The estate spans systems, pipelines, routing, gates and feed surfaces; its units form a broader operating inventory than the model-candidate set. The validator checks pinned counts against source rows and reports drift.

Each candidate records both `readiness` and `operational_state`. Example distinctions: the local Jev role is an incumbent used by dispatch; external TypeSafe Jev is catalogued while its hosted route remains paid-gated; external Laya has a self-hosted evaluation record; external Kev requires its compatible serving composition. See `docs/ops/SYSTEM-ONE-CATALOG.md` and the census `TRIALS.md` for evidence.

The registry's canonical cohort reference is `manager.tournament.v1`. It reuses `manager.tournament.v1` as the sole cohort identity.

## Classifier graph manifest (proposed)

~~~yaml
schema: classifier.graph-tournament.v1
implementation_id: tournament-hybrid-graph
implementation_version: 0.1.0
parent_implementation_id: tournament-incumbent
parent_implementation_version: 1.2.0
canonical_cohort:
  schema: manager.tournament.v1
  tournament_id: tournament-2026-11-22-001
  cohort_id: matched-code-tasks-q4
catalog:
  snapshot_digest: sha256:REPLACE_WITH_REAL_DIGEST
  classifier_versions:
    - classifier_id: syntax-intent
      version: 2.0.0
      implementation_digest: sha256:REPLACE_WITH_REAL_DIGEST
graph:
  graph_id: capability-routed-verification
  graph_version: 1.0.0
  nodes:
    - node_id: route
      kind: router
      policy_id: capability-router
      policy_version: 1.0.0
    - node_id: classify-a
      kind: classifier
      classifier_id: syntax-intent
      classifier_version: 2.0.0
      depends_on: [route]
    - node_id: verify
      kind: verifier
      verifier_id: independent-evidence-check
      verifier_version: 1.0.0
      depends_on: [classify-a]
    - node_id: merge
      kind: reducer
      reducer_id: pareto-evidence-merge
      reducer_version: 1.0.0
      depends_on: [classify-a, verify]
  execution:
    concurrency: dependency_and_capacity_bounded
    retry_policy: bounded_diagnostic
    missing_evidence: preserve_status
evaluation:
  evaluator_id: classifier-graph-evaluator
  evaluator_version: 1.0.0
  held_out_cohort_id: matched-code-tasks-heldout
~~~

## Candidate evaluation envelope (proposed)

~~~json
{
  "schema": "classifier.candidate-evaluation.v1",
  "candidate_id": "candidate-00017",
  "run_id": "run-00017",
  "run_attempt": 1,
  "graph_node_id": "classify-a",
  "classifier_id": "syntax-intent",
  "classifier_version": "2.0.0",
  "status": "completed",
  "output_ref": "sha256:...",
  "evaluators": [
    {
      "evaluator_id": "independent-evidence-check",
      "evaluator_version": "1.0.0",
      "status": "completed",
      "metrics": {
        "precision": null,
        "recall": null,
        "calibration_error": null
      }
    }
  ],
  "provenance": {
    "head_sha": "full-git-commit-sha",
    "environment_fingerprint": "sha256:..."
  }
}
~~~

Allowed node/evaluation statuses: `completed`, `failed`, `skipped`, `timed_out`, `unavailable`, `not_applicable`. Reducers join records by `candidate_id + run_id + run_attempt + graph_node_id`; Use stable IDs for joins; array position serves display ordering. Metrics absent from an observation remain null.

## SIE iteration receipt (proposed)

~~~json
{
  "schema": "sie.iteration-receipt.v1",
  "iteration_id": "sie-00042",
  "incumbent_implementation": "tournament-hybrid-graph@0.1.0",
  "challenger_implementation": "tournament-hybrid-graph@0.2.0",
  "hypothesis_id": "hypothesis-00042",
  "experiment_id": "doe-manager-policy-screen",
  "experiment_version": "1.0.0",
  "evidence_window_digest": "sha256:...",
  "decision": "held",
  "decision_policy_version": "sie-promotion@1.0.0",
  "reason_codes": ["held_out_evidence_pending"],
  "rollback_target": "tournament-hybrid-graph@0.1.0"
}
~~~

## Complete catalog and implementation competition

`classifier.graph-registry.v1` now covers the 88-entry System One catalog
without flattening its layers:

| Layer | Count | Registry treatment |
|---|---:|---|
| Model | 61 | Candidate records; 56 explicitly unclassified pending capability qualification |
| Adapter | 16 | Infrastructure references |
| Runtime | 7 | Infrastructure references |
| Directory | 4 | Infrastructure references |

The 71-unit operating-estate feed remains a separate inventory. Its 12 source-defined groups are versioned in the registry with per-group state counts and checked against the feed rows.

The 71-unit operating-estate feed remains a separate inventory.

The registry adds `tournament.implementation-competition.v1` as a
supplemental section. It records the incumbent implementation's component
source references, the design-only SIE challenger, and mandatory matched
cohort, held-out, independent-evaluator, receipt, rollback and owner
approval gates. `manager.tournament.v1` remains the canonical cohort
identity.


## Staged classifier tournament experiment plan

The checked-in plan is `classifier.tournament-experiment-plan.v1`:

- Plan: `config/classifier_tournament_experiment_plan.json`
- Schema: `docs/ops/CLASSIFIER-TOURNAMENT-EXPERIMENT-PLAN.schema.json`
- Validation: `scripts/ci/classifier_graph_registry_validator.py`

The five phases are inventory qualification, lateral capability screening,
graph composition, complete tournament-implementation comparison, and
promotion/canary. The plan remains `design_only` with
`execution_ready: false` until candidate-specific gates pass. It preserves
four independent comparison units: classifier capability, routing policy,
composition graph and tournament implementation.


## Candidate admission report

`scripts/ci/classifier_candidate_admission.py` emits the deterministic `classifier.candidate-admission-report.v1` view. It separates incumbent baselines, replication candidates, owner-gated candidates, serving-composition blockers, host/egress blockers, referenced-but-unrunnable entries and unclassified models. Admission is scoped to the same role and task contract; Candidate execution requires separate capability and adapter evidence.

Each catalog-backed model candidate retains the catalog's exact `note`
as `catalog_claim` and its exact `source_url` as
`catalog_source_url`. These are source claims, not verified capability
findings. The validator checks exact provenance alignment; qualification
work upgrades evidence state separately.

