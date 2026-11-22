# Tournament Implementation Competition

**Contract:** `tournament.implementation-comparison.v1`  
**Canonical cohort:** `manager.tournament.v1`

## Purpose

Compare two complete tournament implementation versions on the same frozen task cohort. This is the implementation-level competition requested for the DoE Tournament OS. Classifier capability and graph-composition experiments remain separate competition units.

## Receipt contract

Supply one immutable receipt per implementation and task. Each receipt includes:

- `implementation_id`, `implementation_version`, and `competition_role` (`incumbent` or `challenger`);
- `cohort_id`, `task_id`, `task_contract_hash`;
- `environment_fingerprint`, `evaluator_version`, `run_id`;
- `outcome`, `hard_gates`, and a `metrics` object.

The comparator requires exact task-set equality, one cohort, one task contract, one environment fingerprint, one evaluator version, and unique run IDs. This strict environment match is for tournament implementation comparisons. Heterogeneous model candidates use capability-specific cohorts and environment blocks.

Required hard gates: task contract, schema, security/policy, provenance, and deterministic checks. The comparator blocks a challenger recommendation when either arm fails a gate.

## Outcome vector

The comparator understands quality, acceptance, grounding, calibration, reproducibility, latency, compute/inference cost, human effort, context tokens, retries and integration conflicts. Each metric declares a maximize/minimize direction.

Missing metric observations remain null and reduce that metric's paired sample count. The report includes raw paired deltas, direction-normalized improvement, sample counts and approximate 95% intervals. Dominance requires interval-supported non-regression on every comparable metric and positive improvement on at least one.

## Execute

```bash
python scripts/tournament/compare_implementations.py receipts.json --output comparison.json
```

The input file may contain a JSON array or an object with a `receipts` array. The report identifies incumbent and challenger, paired outcomes, hard-gate failures and a recommendation.

Recommendations are human-review inputs. The comparator never changes the active implementation. Promotion requires held-out validation, owner approval and a pinned rollback target.

## Boundaries

- The comparator performs evidence reduction; it does not execute manager implementations.
- It does not infer missing costs or scores.
- It does not compare candidates across different task contracts or environments.
- It does not convert model namesakes into equivalent roles.
- A challenger recommendation remains separate from production promotion.
