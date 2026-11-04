# Quota usage records — per-call consumption contract

Owner fix order 2026-11-03: the quota graphs must show per-call
CONSUMPTION, not activity-proxy dispatch counts. This doc is the
contract for the usage record of a routed inference call, the gap
metric that counts unstamped calls, and the legs that supply and
reconcile the records. Lead: quota-convergence. Supply leg: Swarm
(dispatch-side stamping). Reconciliation leg: quota-specialist.

## The record

Every routed inference call already produces a dispatch record. The
usage of record rides on that same record — never a parallel log:

- **3L0 intake row** (`ops/3l0/intake.jsonl`, written by
  `scripts/dispatch/stamp_fanout.py`): `usage{tokens_in, tokens_out,
  latency_ms, retries}` — token fields are numbers or JSON null.
- **Routed-dispatch record** (`experiments/doe/routed-dispatch/
  {records,stamps}/*.json`): `usage{status, source, unit, value,
  tokens_in, tokens_out, method}`.

A call is **usage-stamped** when either side carries a number:

- token form: `tokens_in` and/or `tokens_out` numeric (the
  http-llm-invoke action extracts them from the provider response;
  missing stays null — never zero-filled, per the invoke usage
  contract tests);
- native form: `usage.status == "measured"` with a numeric
  `usage.value` in `usage.unit` (a provider-native unit where tokens
  are not the meter), with `usage.source = "provider-response"` and
  `usage.method = "fleet-self-count/response-usage"`.

The filled token form on an experiment record is
`{status: "measured", source: "provider-response", unit: "tokens",
value: tokens_in + tokens_out, tokens_in, tokens_out,
method: "fleet-self-count/response-usage"}`.

Routes with no usage surface (CLI/session routes that return no
usage block) stamp `usage{status: "no-usage-surface"}` so the gap
splits by named cause instead of collapsing into one silent bucket.
The fleet self-counting rule applies throughout: where provider
readings fail, our count governs — stamped with its method, never
presented as a provider reading.

## Consumption series

`scripts/quota_usage_series.py` builds kind **`consumption`** —
distinct from `activity-proxy` (dispatch counts), `measured`
(provider readings), `reconstructed` and `estimated`:

- one point per usage-stamped call, cumulative, per provider and per
  model@version (the record's `model` field; NOT ESTABLISHED models
  are excluded, never inferred);
- unit is the record's unit (`tokens` or the provider-native unit);
  series never mix units;
- provenance names the record sources and this contract.

## The gap metric (coverage honesty, inverted)

`pack.consumption_gap` in `ops/quota/usage-series.json`:

- `routed_calls` — the denominator: routed calls of record (3L0
  intake + routed-dispatch records/stamps + nested-family carriers,
  dispatch_id-deduped, github-actions CI rows excluded);
- `usage_stamped` / `unstamped` / `unstamped_share`;
- `causes` — `no-usage-record` vs `no-usage-surface`;
- `by_provider` — calls/stamped/unstamped per provider family.

`quota-graphs.html` renders it as a NAMED card ("UNMEASURED —
unstamped routed calls") plus a summary line. Unstamped calls are
counted and named, never silently excluded. State at contract
landing (2026-11-03): 0 of 22 routed calls usage-stamped — the gap
is the headline until the supply leg lands.

## Legs

- **Swarm (supply):** stamp assembly carries the http-llm-invoke
  action's `tokens_in`/`tokens_out` outputs into `stamp.usage` so
  `stamp_fanout.py` lands real values in both record planes;
  no-usage-surface routes stamp the named status above.
- **Quota-specialist (reconciliation):** `quota_delta` semantics —
  a measured record's draw against its registry entitlement
  (limit/window of the matching registry record, joined via the
  record's `quota{pool, slice}` block); where units differ the delta
  stays null with the mismatch named. Coverage citations carry both
  numbers, labeled: provider-readings coverage and consumption
  coverage (this metric).
- **Quota-convergence (data plane):** the series builder, the gap
  metric, the page render, and this contract.
