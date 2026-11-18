# QUE task ranking v3-compounding — shadow candidate

**Method ID:** `que-task-rank/v3-compounding`  
**Status:** PROPOSED / SHADOW-ONLY / NOT EXECUTED / NOT COUNTERSIGNED  
**Control:** `que-task-rank/v1` remains binding. This module does not integrate with dispatch or auto-claim.

## Benefit vector

All six inputs are cohort-frozen, source-pinned normalized values in [0, 1].

| Dimension | Weight |
|---|---:|
| Direct verified outcome | 20 |
| Downstream unlock | 20 |
| Recurrence eliminated | 20 |
| Reuse / leverage | 15 |
| Reliability / risk reduction | 15 |
| Evidence confidence | 10 |
| **Total** | **100** |

`C = Σ(weight × normalized dimension)`

Cost inputs are normalized execution effort, expected elapsed delay, and coordination/rework burden:

`E = execution_effort + elapsed_delay + coordination_rework`

`raw_efficiency = 100 × C × confidence_adjusted_realization / max(E, ε)`

The code retains all component and cost values in its result. The normalized efficiency is converted to a midrank percentile **within the supplied eligible cohort only**. Do not compare percentiles across cohort snapshots as absolute values.

## Evidence contract

Each issue's evidence map contains:
- `dimensions`: all six benefit dimensions above;
- `costs`: all three normalized cost fields;
- `realization`: observed confidence-adjusted realization in [0, 1].

The producer of this map must retain the original raw values, units, source refs, source SHAs, observation window, and cohort ID. This module validates normalized numeric shape; it cannot authenticate provenance or independently verify outcome truth. Booleans, missing, malformed, non-finite, and out-of-range values are rejected as missing evidence, never converted to zero.

## Incomplete coverage and ordering

- Complete rows are scored and ranked only against other complete rows in the same supplied cohort.
- Rows missing any required v3 value are emitted separately in their existing v1 order.
- The module intentionally emits no combined `claim_order`; v1 and v3 percentile scales are not mixed.
- The <=48h / overdue wall is a lexicographic safety class among v3-eligible rows. Existing v1 remains the control for fallback rows.
- Duplicate or invalid issue IDs fail closed.
- Ties are deterministic by v1 score then issue number; tied efficiency values share a midrank percentile.

## Authority and integration boundary

This is a pure shadow scorer and test fixture. It does not write a feed, call GitHub, claim work, alter admission/deferral, change lease rules, or bind claim order. L5 in #5546 is reserved to the existing evaluator. No new L5 replay is initiated here. Evaluator admission, paired replay, prospective shadow observation, DoE countersign, and QDesk/Desk decision remain required before any promotion.

## Tests

Run from repository root with the Python test runner used by the repository:

`python -m pytest scripts/que/test_task_ranking_v3.py`

This work was authored through GitHub's repository API; no local test execution is claimed.
