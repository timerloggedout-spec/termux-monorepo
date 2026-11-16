# Public Usage Value Board

## Purpose

Continue the merged Free-Tier Use Value Board (#1589) through the existing session-evidence integration lane (#1588) and the EPS/Moneyball contract work (#1592). Public display is intended: publish only bounded, validated, public-safe usage metadata and compare the same observed token workload against model-specific provider rate cards.

## Boundaries

- Reuse the existing Moneyball/provider-call evidence contract and Basksweep-approved export; do not create a second telemetry source, poller, or scheduler.
- Keep actual observed provider cost, counterfactual API list-price equivalent, verified no-cost value, entitlement, and human opportunity cost separate.
- Missing/stale usage remains unavailable, not zero.
- Public rows exclude prompts, completions, tool payloads/results, credentials, private balances/quota readings, and personal identifiers.
- Equivalent costs use identical aggregate input/output token counts across each valid model-specific price row and sort from most expensive to least expensive.

## Related work

- #1588 — wire validated public session usage.
- #1592 — EPS/Moneyball evidence projection and source manifest.
- #1593 — quota-awareness cross-link, without conflating quota and session economics.
- #1571 — visualization-layer evaluation.
- #1589 — initial board, merged.
