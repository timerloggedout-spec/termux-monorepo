# DoE Tournament — schema reference

The following YAML and JSON are illustrative v1 contracts. They are not yet wired to runtime validators.

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
- A manager cannot judge its own treatment as the sole acceptance authority.
- Provider identity and GitHub actor identity remain distinct.
- Every score links to evaluator version and source evidence.
- Every promotion links to a tournament version and exact candidate evidence set.
