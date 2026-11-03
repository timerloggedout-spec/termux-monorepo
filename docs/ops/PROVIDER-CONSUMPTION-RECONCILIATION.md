# Provider Consumption Reconciliation

**Status:** implementation contract for the existing Provider Consumption & Entitlement Attribution Ledger. This document defines reconciliation over current registry, readings, dispatch stamps, cadence ticks, and event evidence; it does not introduce a second registry, poller, instrumentation store, or runtime admission gate.

## Purpose

Compare provider-observed consumption with attributable requisition/event totals only when both sides describe the same resource, account scope, unit, time window, and reset epoch. Reconciliation explains residuals; it never forces them into consumer rows.

Canonical semantics remain in Quota Attribution. The current usage-series projection is built by scripts/quota_usage_series.py; GitHub cadence tick validation and aggregation live in scripts/cadence_tick_ledger.py.

## Inputs and authority

| Input | Authority | Permitted use |
|---|---|---|
| Provider registry | ops/quota/registry.json and linked provider configuration | Provider/resource/account identity and supported measurement surface |
| Provider readings | Existing ops/quota/quota-usage.json and generated status projections | Snapshot counters, native units, reset metadata, observation times |
| Dispatch requisition stamps | Existing DoE routed-dispatch records/stamps and desk-feed records | Exact provider/model@version/configured-instance and dispatch-time usage evidence |
| Cadence ticks | Existing cadence tick JSONL and cadence_tick_ledger.py | Request-level GitHub bucket observations and request counts; bucket counters remain shared-scope evidence |
| Billing/credit evidence | Provider invoice, billing export, or explicit entitlement record | Actual billed cost or verified coverage, never inferred from a usage delta |

A projection is not a new source of truth. Every result retains source paths/IDs, source SHA/ref where available, observation timestamps, and reconciliation version.

## Required reconciliation key

A snapshot pair and its event set are comparable only when all applicable dimensions match:

provider + account/principal scope + resource/bucket + native unit + window + reset epoch

For model/consumer attribution, retain the full configured-instance tuple from Quota Attribution:

provider + model@version + system_prompt_ref + tools_ref + moniker + role + context

Do not aggregate away role, context, or configured-instance identity before validating the join. A provider that does not expose a model or consumer dimension stays at the coarser provider/resource scope.

## Snapshot-delta algorithm

For two ordered snapshots S0, S1 of the same scope:

1. Validate both records, units, account/resource identity, timestamps, and reset metadata.
2. Confirm both observations belong to the same reset epoch and that the later snapshot is not stale or out of order.
3. If the counter is monotonic, compute observed_delta = S1.used - S0.used.
4. If the counter decreases, do not take an absolute value. Classify a reset only when the provider's reset epoch proves it; otherwise emit a counter-regression finding and leave the delta unavailable.
5. Sum only established event usage with the same reconciliation key and covered interval: attributed_total = sum(event.usage.value).
6. Compute residual = observed_delta - attributed_total only when both quantities are comparable.
7. Persist the finding and its source lineage. Never allocate a residual to an individual consumer.

If the provider exposes only a current snapshot with no valid prior snapshot, retain the reading but do not fabricate a delta.

## Finding classes

| Finding | Meaning | Action |
|---|---|---|
| reconciled | Comparable observed delta equals established event total | Close the scoped comparison; retain lineage |
| positive_residual | Provider delta exceeds attributable events | Investigate unstamped calls, missing event coverage, or scope leakage; leave residual unallocated |
| negative_residual | Event total exceeds provider delta | Investigate duplicate/replayed events, interval mismatch, or provider counter semantics |
| scope_mismatch | Provider/account/resource/unit/window/reset epoch differs | Mark incomparable; do not compute a residual |
| reset_boundary | Provider reset epoch changed between observations | Start a new epoch; never bridge the reset with subtraction |
| stale_reading | Snapshot freshness exceeds the source-specific budget | Retain as stale evidence; exclude from current reconciliation |
| missing_baseline | No valid earlier snapshot exists | Keep the reading; delta unavailable |
| missing_events | Snapshot delta exists but no matching event coverage exists | Preserve provider-level delta; consumer attribution unavailable |
| activity_only | Evidence is a run/session/activity count rather than consumption | Keep in a separate activity series; never add to consumption totals |
| provider_limit | Provider does not expose the required consumer/model dimension | Keep the coarser provider-level result; do not split it synthetically |

## Append-only event and finding identity

- Consumption events are immutable observations. A correction is a new event that references the superseded event.
- A stable event identity includes provider, account/principal scope, source event ID (or deterministic source fingerprint), event time/window, resource, native unit, and configured-instance key when present.
- Replays with the same identity are idempotent and cannot increase totals.
- A reconciliation finding identity includes scope key, snapshot pair IDs, interval, and reconciliation version.
- Re-running the same input set yields the same finding identity and numeric result.
- Preserve supersession lineage; do not delete or silently rewrite prior findings.

## Economic projection rules

Reconciliation produces quantities and coverage evidence first. Economic views are separate projections:

- **Paid-equivalent API value:** exact input/output token counts × matching provider/model/version paid rates, divided by one million. Require an exact pricing identity and a source-linked, dated rate record.
- **Verified free-quota coverage:** only when an explicit entitlement/billing record proves the workload was covered at no charge.
- **Observed provider cost:** only from authoritative billing evidence.
- **Native quota usage:** remains in the provider's unit (calls, credits, requests, minutes, or tokens).
- **Opportunity cost:** belongs to the Competitive Opportunities Portfolio and requires a documented feasible alternative use forgone.

Unknown billing is not free. A provider quota delta is not automatically a token count, dollar cost, or model allocation.

## Privacy and export

Public outputs may include bounded identifiers, provider/model labels, units, timestamps, source references, status, and derived totals. They must exclude prompts, completions, raw tool payloads, credentials, private balances, personal identifiers, and arbitrary provider response bodies.

## Deterministic acceptance fixtures

The implementation must test at least:

1. Exact same-scope snapshots and matching events produce reconciled.
2. Positive and negative residuals remain unallocated and produce distinct findings.
3. Provider, account, resource, unit, window, or reset-epoch mismatch produces scope_mismatch.
4. Proven reset starts a new epoch; unexplained counter decrease produces counter_regression.
5. Missing baseline, stale reading, missing events, and provider-limited attribution remain explicit gaps.
6. Duplicate/replayed events do not increase totals.
7. Corrections supersede prior records without deleting history.
8. Activity-proxy records never enter consumption sums.
9. Configured-instance differences prevent false model/consumer joins.
10. Unknown billing, pricing, or alternative-use evidence remains unavailable rather than zero.

## Rollout sequence

1. Validate existing source shapes and record inventory without writing.
2. Add a pure reconciliation function over supplied snapshots/events.
3. Add deterministic fixtures for every acceptance case above.
4. Emit append-only findings to the existing ledger/projection path.
5. Add a read-only Moneyball view only after finding lineage and coverage tests pass.
6. Enable any scheduled collection or runtime integration only through a separate approved code/workflow proposal.
