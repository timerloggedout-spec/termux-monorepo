# autoQuotaCadence — deterministic DoE pool generation + cadence derivation

QUE #5160. Spec: issue #5160 + Cadence domain review c.6802642639
(NO ledger-interface conflict) + QDesk addendum c.6802661589.

## What it is

A deterministic derivation — not a poller, not a ledger, not a router,
not a cron. `scripts/ops/auto_quota_cadence.py` reads files already in
the checkout and emits the DoE endpoint pool + per-arm cadence decisions:

- Inputs: `ops/dispatch/build-arms.json` (arm registry) +
  `ops/que/feeds/arm-census.json` (eligibility census) +
  `ops/quota/registry.json` (entitlement/observation evidence) +
  an optional published ledger snapshot (`ledger-snapshot/v1`, see
  `docs/ops/LEDGER-SNAPSHOT-CONTRACT.md`).
- Outputs: `ops/que/feeds/pool-cadence.json` (schema `pool-cadence/v1`)
  + the executor's `--usage` record (`pool-usage.json`, generated per
  run, not committed).

No model inference, no live provider calls, no credentials, no metering.
The derivation succeeds with zero eligible arms and with Gemini
unavailable — pool generation never depends on any single arm.

## The gate (clause 3)

An arm is dispatchable only when ALL hold:

1. Exact invoke route (endpoint URL, or a named harness with a ref).
2. Current census pass from the relevant environment (Actions evidence;
   a census without a run id is provenance-unknown and defers).
3. Entitlement: a named record in `ops/quota/registry.json`.
4. Usable quota headroom with source + observation time + reset
   window/timezone — read ONLY from a published ledger snapshot.
5. No duplicate `route_id` in the registry.

Anything else defers with a named reason (`quota_unknown`,
`census_not_passed`, `census_stale`, `route_dead`, `duplicate_route`,
`entitlement_unknown`, `quota_unbudgeted`, `quota_exhausted`,
`reset_window_unknown`, `reset_tz_unknown`,
`availability_env_unknown`, `quota_terminal_today`). A listing, a
`/v1/models` hit, a sandbox-only success, or a bare 429 never proves
entitlement or headroom.

## Gap 1 — ledger reads unavailable (BUILD CONSTRAINT)

The #5152 ledger read contract {store, fields, freshness} is
UNPUBLISHED until #5113 T2 publishes it. Until then the snapshot input
is absent by definition: `ledger_read.status = "unavailable"`, every arm
defers on `quota_unknown`, and the pool is empty with named reasons.
The derivation NEVER invents a metering leg in Actions (Cadence
c.6802642639 gap 1; QDesk addendum c.6802661589). Unknown/stale quota
means defer (clause 4).

## Gap 2 — reset window/timezone (T2 publication requirement)

Budget records carry reset only as prose today. The derivation reads
`{reset_window, reset_tz}` ONLY from a published snapshot's budgets;
the registry's prose `reset` field is cited as evidence and is NEVER
parsed into a window (QUOTA-RESET-CONTRACT boundary: observe, never
infer a reset from the calendar). Absent a snapshot the stamp is
UNKNOWN. The dispatch executor's pre-flight (`preflight()` in
`scripts/ops/dispatch_executor.py`) reads the same fields from the
usage record's `budgets` section and likewise stamps UNKNOWN when
absent — the hardcoded `"midnight PT"` / `"daily"` values are gone.

## Gemini position (clause 5)

Gemini competes on the SAME gate as every other arm. #5160 removed:

- `ops/dispatch/build-arms.json` `selection_rule`: the
  "fallback of record" phrasing is gone.
- `scripts/ops/build_arm_harness.py` `select_arm()`: no harness-class
  preference, no Gemini precedence — eligible free-tier arms in
  registry order, then credit-funded. When Gemini is the sole eligible
  arm it is selected as the first eligible free-tier arm, and the
  executor stamps the fire `constrained-arm` (never a preference).

NOT changed by this build (adjacent scope, needs a Desk/QDesk
decision, not a silent edit): the `build-dispatch.yml`
`@gemini-cli /build` issue-comment trigger is still Gemini-named.
Flagged here and in the #5160 receipt; the trigger does not affect pool
generation or the cadence derivation.

## Rotation

Eligible arms order: registry order, free-tier before credit-funded.
When the previous feed names a `last_selected_arm` that is still
eligible, it rotates to the end (no consecutive same-arm selection
where the DoE rules require it).

## Wiring

`.github/workflows/dispatch-executor.yml` runs the derivation before
`decide` on every executor cycle and passes the emitted record as
`--usage pool-usage.json`. No new workflow, no new cron (the executor's
`*/15` cadence clock is reused). The `pool-cadence.json` +
`pool-usage.json` files are uploaded in the `dispatch-executor-receipt`
artifact for provenance.

## Pool identity boundary

This is the DoE **provider/model inference execution-arm pool**
(eligible free endpoints) — NOT the Dreambeans candidate-method-version
pool (`docs/ops/DOE-DREAMBEANS-POOL.md`). The two populations are never
merged and neither owner's canonical store is duplicated. The g4f
working set (`data/g4f-working/working-endpoints.json`) stays
candidate/reference-only (`runtime_eligible: false`), never admission.

## Current state (seed, 2026-11-12)

`ops/que/feeds/pool-cadence.json` as committed: 0 eligible / 7 deferred,
`ledger_read = unavailable (ledger_snapshot_absent)`. Gemini-cli defers
only on `quota_unknown` + reset unknowns (its census is eligible, its
route and entitlement are proven); the other arms defer on named
census/quota/route reasons. The first live conversion lands when T2
publishes the ledger snapshot — the derivation, the snapshot contract,
and the executor wiring are the surface this build supplies.
