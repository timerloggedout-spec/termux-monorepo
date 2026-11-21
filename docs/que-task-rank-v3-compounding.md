# QUE task ranking v3-compounding — FCE-backed shadow candidate

**Method:** que-task-rank/v3-compounding  
**Efficiency reducer:** flywheel-compounding-efficiency/v1  
**Status:** PROPOSED / SHADOW-ONLY / NOT EXECUTED / NOT COUNTERSIGNED  
**Control:** que-task-rank/v1 remains binding. This module does not integrate with dispatch or auto-claim.

## Upgrade from the initial shadow candidate

The initial #5616 candidate implemented a local six-dimension efficiency calculation. This revision extracts the reusable FCE reducer, adds provenance and a matched-baseline comparison, and broadens normalized costs to include context, feedback cycles, conflict/retry burden, human intervention, and provider cost. It rejects zero-total-cost inputs rather than using an epsilon denominator.

## Ranking contract

- Complete rows are ranked only within one frozen cohort, task-contract, environment, validation-suite, cohort-manifest, and cost-normalization basis.
- The candidate arm uses FCE raw efficiency and cohort-local midrank percentiles. Percentiles are not absolute and cannot be compared across cohort snapshots.
- Missing/invalid evidence remains in a separate v1 fallback population. No mixed claim_order is emitted.
- The <=48h/overdue wall remains a lexicographic safety class within the candidate arm.
- Duplicate or non-integer issue IDs fail closed.
- A matched baseline comparison is computed only when the same task/cohort/contract/environment/validation/cohort-manifest/cost-normalization identity is present and the baseline itself has source/evidence provenance.

## Authority boundary

This remains a pure shadow scorer. It does not write feeds, call GitHub, claim work, alter admission/deferral, change leases, bind claim order, or mutate production routing weights. No L5 replay or DoE campaign is initiated. Evaluator admission, paired replay, prospective observation, DoE countersign, and QDesk/Desk decision remain separate required steps.

## Tests

python -m pytest scripts/que/test_flywheel_compounding_efficiency.py scripts/que/test_task_ranking_v3.py -q
