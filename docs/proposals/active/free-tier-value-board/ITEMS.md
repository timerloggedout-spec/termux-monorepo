# ITEMS — free-tier-value-board

| ID | Priority | Item | State | Evidence / exit condition |
|---|---|---|---|---|
| VALUE-BOARD-001 | P1 | Show validated public usage's counterfactual API-equivalent cost across model-specific provider rate cards, ordered most expensive to least expensive. Keep the arbitrary-workload calculator in the same descending order. | in_review | Public UI uses deduplicated rows that pass existing validation/Basksweep/publication gates; identical aggregate input/output tokens are applied to each valid price row; absent feed is explicitly unavailable, not zero; deterministic tests cover order and missing-feed semantics. |
| VALUE-BOARD-002 | P1 | Wire the board to the canonical provider-call/session evidence through the existing Basksweep/EPS export. | posted | #1588/#1592: immutable source SHA/run attempt, reproducible source manifest/hash, deterministic duplicate/privacy/unknown/token tests, reconciled counts/tokens/costs, and exact-head dual-gate receipts. |
| VALUE-BOARD-003 | P1 | Correlate session economics with quota-awareness evidence without conflating measures. | posted | #1593: read-only cross-link; actual cost, counterfactual value, verified no-cost status, entitlement, and private quota state remain separate; no new poller or public private-balance/routing data. |
