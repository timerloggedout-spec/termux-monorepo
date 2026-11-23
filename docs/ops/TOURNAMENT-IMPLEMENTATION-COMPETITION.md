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
- `outcome`, `hard_gates`, a cohort-wide `metric_set`, and a `metrics` object.

The comparator requires exact task-set equality, one cohort, one task contract, one environment fingerprint, one evaluator version, one identical declared metric set, and unique run IDs. Every receipt supplies every metric-set key; use JSON `null` for an unobserved value. The comparator rejects omitted keys, mismatched metric sets, non-finite values and unsupported metric IDs. This strict environment match is for tournament implementation comparisons. Heterogeneous model candidates use capability-specific cohorts and environment blocks.

Required hard gates: task contract, schema, security/policy, provenance, and deterministic checks. A hard-gate failure in either arm sets the recommendation to `blocked_by_hard_gate`.

## Outcome vector

The comparator understands quality, acceptance, grounding, calibration, reproducibility, latency, compute/inference cost, human effort, context tokens, retries, integration conflicts and policy violations. Each metric declares a maximize/minimize direction.

Missing metric observations remain null and reduce that metric's paired sample count. Partial coverage blocks dominance for the cohort; the report lists incomplete and wholly unobserved metrics explicitly. The report includes raw paired deltas, direction-normalized improvement, sample counts and approximate 95% intervals. Paired intervals use Student-t critical values through 30 degrees of freedom and a normal approximation for larger samples. Dominance requires complete paired coverage, interval-supported non-regression on every observed metric and positive improvement on at least one.

## Execute

```bash
python scripts/tournament/compare_implementations.py receipts.json --output comparison.json
```

The input file may contain a JSON array or an object with a `receipts` array. The report identifies incumbent and challenger, paired outcomes, hard-gate failures and a recommendation.

Recommendations route to human review. Promotion uses held-out validation, owner approval and a pinned rollback target; the active implementation changes only through that separate promotion process.

## Boundaries

- The comparator performs evidence reduction; execution remains with the selected manager implementation.
- Missing costs and scores remain null.
- Implementation arms share task contracts and environment fingerprints.
- Model namesakes retain separate capability contracts.
- Challenger recommendations route through held-out review and owner-approved promotion.
