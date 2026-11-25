# ASSERT — Agent Specification and Trace Evaluation Pattern

**Category:** `11_Evaluation_Quality`  
**Disposition:** concept-adaptation candidate · metadata-first

## Source

See `SOURCE.txt`. Upstream source revision remains unpinned; record an immutable commit/tag before a reproducible comparison.

## Pattern to extract

- Translate behavior specifications into structured test cases.
- Evaluate agent runs against the declared behavior contract.
- Ground evaluator judgments in execution traces where available.
- Emit portable evaluation artifacts for repository-owned analysis.

## Repository adaptation

Map the behavior-specification and trace-judging concepts onto the existing ATES cohort, native tests, redacted evidence receipts and evaluator lane registry. Keep the native test harness as the control. Preserve candidate status until a same-cohort experiment demonstrates measurable incremental value.

## Measures

Acceptance detection, regression detection, evaluator agreement, trace coverage, reproducibility, latency, cost and operator review effort.

## Ownership

CEEL owns concept extraction and experiment evidence. The designated licensing duty owner handles licensing disposition separately.
