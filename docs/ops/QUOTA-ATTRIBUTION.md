# Quota Attribution — the requisition × actor join

`[MUSEai]@{role:{quota-specialist}}` · Owner demand 2026-10-30 (via `viz-dispatch-tree`): provider/model attribution for code + requisitions, per-entry usage rendered in `desk.html`. Evidence class refs per #1734; notation per #320.

## The join problem

Requisitions are visible per service (readings, bucket walls, lane-events). Actors are visible per artifact (bot authors, check-run apps, signed roles). The JOIN between them exists only where a principal or a key separates the calls.

- Shared PAT bucket ⇒ GitHub exposes ∅ per-consumer breakdown (one user principal). Per-lane PAT consumption is NOT RECOVERABLE from GitHub telemetry — historically (storms) or now.
- Attribution therefore starts at instrumentation: consumers self-key at the requisition point. Nothing is backfilled; views carry that line.

## Join keys (the render contract)

| key | surfaces | strength |
|---|---|---|
| `app_id` | GitHub App principals (collector 5535733, publisher 5537873, reviewer/gate/lifecycle as provisioned) | exact — own bucket per installation, `<slug>[bot]` authorship |
| `workflow_name` | GitHub Actions runs (`GITHUB_TOKEN` bucket, 1000/h/repo) | exact per workflow |
| `session_id` | Jules sessions ⇒ PRs (`google-labs-jules[bot]`) | exact link; consumption units ∅ exposed (see below) |
| `lane_role` | signed artifacts `[MUSEai]@{role:{…}}` + helper-stamped requisitions | exact where stamped; dark where unstamped |
| `null` | everything else | honest blank, never estimated |

## Per-provider consumption exposure (2026-10-30)

- `github.api.app_*` — per-installation rate headers: calls consumed per window = measurable per app.
- `github.actions` — run counts/durations per workflow = measurable; token split per run = ∅.
- `github.api.user_token` — aggregate bucket only; per-consumer split = ∅ from GitHub; self-stamped ledger (below) is the only route.
- `jules` — session state + activity feed per session; per-session consumption units (tokens/calls) = ∅ exposed by the API. Activity counts are activity, ≠ consumption.
- All other registry providers — per-consumer consumption NOT_ESTABLISHED unless the provider's own usage surface names the consumer key.

## `usage{}` field shape (desk-feed contract)

```json
"usage": {
  "value": null,
  "unit": null,
  "source": null,
  "window": null,
  "match": null,
  "note": null
}
```

Fill rules (match or silence):

- `value` — number ONLY on a keyed match (`session_id` | `app_id` | `workflow_name` | stamped `lane_role`) ∧ the provider exposes consumption for that key.
- `unit` — the provider's own unit verbatim (`calls`, `tokens`, `credits`, `minutes`, `sessions`).
- `source` — readings row / lane-events key / provider surface the number came from.
- `window` — the interval the number covers, ISO 8601.
- `match` — `exact` (consumption for that key) | `activity-proxy` (counts of sessions/runs/activities — rendered labeled as activity, never as consumption).
- `note` — the caveat line when `match = activity-proxy`, or the darkness reason when `value = null`.
- No match ⇒ `value = null` + `note` carries the reason. Estimates are never rendered as usage.

Worked state at landing: every current desk entry is honestly `value = null` EXCEPT keyed activity (e.g. a Jules-backed entry: `unit = sessions, match = activity-proxy, value = <session count>`), because no provider yet exposes per-entry consumption units to our surfaces.

## Instrumentation (how numbers start existing)

1. Readings v-next gains a `consumer` axis: `{app_id | workflow_name | lane_role | null}` alongside the resource axis.
2. The PAT helper + publishers stamp requisition batches with the acting `lane_role` ⇒ lane-events rows `(lane_role, surface, window, calls)` ⇒ PAT-side per-lane numbers exist from stamp day forward.
3. lane-events remains the join store (Neon); viz renders witnesses × requisitions × PRs on `head SHA ∧ signed role ∧ key`.

## Out of scope / dark by construction

- Historical burn attribution (no retroactive join exists).
- Unstamped interactive reads (dark unless the helper stamp is on).
- Any per-entry split of a shared-bucket aggregate (mathematically ∅ from readings alone).

## Telemetry requirement (owner, 2026-10-30 23:10 PT)

Per-entry quota usage is REQUIRED telemetry for ALL entries. Consequences:

- Stamping is mandatory at requisition time for every dispatch at/after **2026-10-30T23:10 PT**: provider + session/key + window + consumption (or the null-reason) are recorded when the draw is made, not reconstructed later.
- `usage{}` gains a `status` field, rendered by desk-feed as the coverage strip (established/total per entry):

```json
"status": "established | activity-only | waived | fault | pending"
```

- `established` — `match = exact`, `value ≠ null`. `activity-only` — `match = activity-proxy`. `pending` — no dispatch yet.
- `waived` — ALL of the entry's dispatches predate the mandate AND consumption is unrecoverable (provider exposes ∅ per-entry units, or the draw sat in a shared bucket with ∅ per-consumer split). `note` MUST carry the reason verbatim. D0, D1-original, D3, M4 land here at the mandate's start.
- `fault` — ANY dispatch at/after the mandate lacks its stamp. Fault is a live, fixable state: stamping the late record (with its true window) clears it. Fault-forever is rejected as a state: it would mark mathematically unrecoverable history as a standing failure and destroy the signal.
- Coverage counts `established + activity-only + waived` as covered; `fault` and unstamped post-mandate `pending` render as visible gaps.

## Telemetry key set + roll-ups (owner, 2026-10-30 23:10 PT)

Every requisition record carries the full key tuple. The identity atom is the CONFIGURED INSTANCE — a single model@version under different system prompts / tools per role/context is a different consumer. This atom stands since init; QUOTA-ATTRIBUTION lagged it, and the owner clarified the standing fact on 2026-10-30 (clarification, not a delta, per #1734).

```json
"keys": {
  "provider": "<registry provider id>",
  "model": "<model id>@<version> — version provider-verbatim; no version exposed => version NOT ESTABLISHED, never inferred (e.g. Jules)",
  "system_prompt_ref": "<ref per the DoE scheme; encoding NOT ESTABLISHED until the DoE seat names it — adopted verbatim when named>",
  "tools_ref": "<ref per the DoE scheme; same status as system_prompt_ref>",
  "moniker": "<fleet moniker from the signed identity>",
  "role": "<fleet role — per-dispatch axis, never aggregated away>",
  "context": "<entry id / dispatch context>"
}

- `moniker` + `role` = the dispatching lane's signed identity `[MUSEai]@{role:{moniker}}`; `context` = the entry/dispatch the draw served. All three are known at requisition time — a post-mandate record missing any of them is unstamped ⇒ `fault`.
- `system_prompt_ref` + `tools_ref`: carried on every record; until the DoE seat names the ref scheme they are `null` and NOT a fault axis (unstampable until nameable); after the scheme lands, a missing ref on a dispatch = unstamped ⇒ `fault`. The spec adopts the DoE scheme verbatim when named.
- `provider` from the registry id space; `model` is the provider's own model id verbatim, `null` (never guessed) when the surface doesn't split by model.
- `usage{}` records sit under these keys; desk-feed groups on exactly this tuple.

Roll-ups (rendered totals):

- TOTAL quota used = Σ `usage.value` over `established` records, per `unit` (units never summed across).
- Split BEFORE any Σ: records group by {provider, model@version, role} first (role is per-dispatch, never aggregated away); per-axis totals for moniker / context / instance (prompt/tools refs) derive from the split rows, never from pre-aggregated sums.
- `activity-proxy` values roll up separately under their unit, labeled activity — never merged into consumption totals.
- `waived` records contribute ∅ to totals and count as covered in the coverage strip; `fault` records contribute ∅ and count as gaps.

## Ref scheme (DoE, landed PR #2656 `82bd529b17fc` — adopted verbatim)

`system_prompt_ref` / `tools_ref` are now NAMEABLE:

- ref = repo-relative PATH ∨ scoped id `prompt:<moniker>:<slug>` / `tools:<moniker>:<slug>`, ALWAYS + the full SHA-256 of the exact dispatched content.
- Compact stamp = `<ref>#<sha256[:12]>`.
- `instance_key` = `sha256(canonical tuple JSON)`; helper `scripts/doe/instance_key.py` on master computes it.
- Fault boundary flips at the scheme landing: dispatches after PR #2656 carry both refs or they are unstamped ⇒ `fault`. Pre-scheme records keep `null` refs, waived on those two axes.

## Duplicate rule + desk-feed ↔ DoE mapping (landed with the duplicate integration)

Rows that share `{provider, model@version}` are DUPLICATES on the model axis alone — the standing case is the pair of `Muse — desk-spawned subagents` rows in desk-feed (D3 + AMD M4, same provider, same model, same moniker/role). Rule:

- A duplicate pair stays TWO consumers iff their configured instances differ: entry-scoped `context` + distinct `system_prompt_ref` slugs (per-entry prompt sets). Roll-ups group by the full key tuple incl. instance — never merge a duplicate pair on provider+model.
- desk-feed `provider_usage[].instance_key{system_prompt_ref, tools_ref, note}` is the feed's transitional stamp object (pilot: Jules row, content hash in compact `<ref>#<sha256[:12]>` form where the dispatched content is retrievable). It maps 1:1 onto DoE `treatment.instance` (`docs/ops/corpus/EXPERIMENT.schema.json`, PR #2656): `system_prompt{ref, sha256}` / `tools{ref, sha256}` + `{provider, model, role, moniker, context}`; when both content hashes are established, the hex `instance_key` is computed by `scripts/doe/instance_key.py` and the EXPERIMENT record supersedes the feed object as the identity of record.
- Hashes are NEVER fabricated: where the exact dispatched content is not retrievable from a repo or provider-API record (the retracted 2026-10-30 desk-spawned briefs), the stamp carries the named ref + `NOT ESTABLISHED` in its note, and the axes stay waived for pre-mandate rows.
- Desk dispatch intake carries the stamp fields as required inputs (desk-feed `dispatch.intake_url` template): provider + session_id + model@version + both refs. No stamp ⇒ no dispatch.
## Auditability contract — Provider Consumption & Entitlement Attribution Ledger

This section strengthens auditability across the existing quota registry, provider readings, requisition stamps, cadence ticks and lane-events projection. It extends the current evidence plane; it does not create another poller, registry, instrumentation store, scheduler or runtime admission gate.

### Canonical record families

Keep these record families independently addressable and independently reconcilable:

1. **Entitlement observation** — provider and resource IDs; account scope at a privacy-safe stable alias; plan/tier when sourced; limit; native unit; window/reset semantics; authoritative source reference; observed timestamp; freshness and evidence status. A configured registry limit is a declared entitlement datum, while a live poll is an observation. Preserve that distinction.
2. **Consumption event** — immutable event ID; provider/resource; the existing full consumer/instance key tuple where exposed; amount and native unit; window start/end; observed timestamp; source surface and source-record reference; counted/activity classification.
3. **Attribution assessment** — exact, activity-proxy, or unattributed match; existing established, activity-only, waived, fault, or pending status; evidence class/confidence; null reason; provider granularity capability. Provider-only and shared-bucket totals remain provider/resource-level facts.
4. **Billing and coverage assessment** — paid, verified_no_cost, included_or_subscription, or unknown; observed cost and currency only from authoritative billing evidence; explicitly evidenced free-quota/credit coverage in its native unit; pricing snapshot reference for counterfactual paid-equivalent valuation.
5. **Audit lineage** — schema version; collector/actor; recorded timestamp; source URI/ref and source hash where safe; idempotency key; validation result; and optional supersedes/correction reference.

### Metric vocabulary and unit discipline

Every quantity carries a metric name, numeric value, unit, scope, and observation window. Keep these distinct:

- entitlement limit / capacity;
- remaining balance;
- consumption delta;
- API request count;
- token count (input, output, cached input where supported);
- provider credits;
- execution minutes / seconds;
- deployments, sessions, and other native service units;
- observed monetary cost;
- paid-equivalent monetary value.

Never aggregate unlike units. A request count is not a token count; a credit is not a dollar unless the provider's official conversion and billable-unit mapping support it. A remaining-balance snapshot is not a consumption event. A configured limit is not a live observation.

### Append-only correction and idempotency

- Persist source observations/events as append-only evidence. A correction is a new record linked to the superseded record, with reason and provenance; preserve the original.
- Derive a deterministic idempotency key from the canonical source identity + source event/record identity + metric/unit/window. Replays become duplicate findings rather than extra consumption.
- Preserve source timestamps separately from ingestion/recorded timestamps. Retain source window boundaries and reset epoch so counter rollover can be interpreted.
- Keep raw credentials, account identifiers, prompts, completions and arbitrary provider payloads outside public evidence. Public projections use an explicit allowlist and privacy-safe aliases.

### Reconciliation and audit findings

Reconcile a snapshot delta to event-ledger totals only when provider, resource, account scope, unit, window boundaries and reset epoch match. Emit a quantified residual and a finding when they do not reconcile; never force the residual into a consumer row.

The audit should classify at least:

- duplicate/replayed event;
- missing required post-mandate dispatch stamp;
- missing source reference or source hash;
- event timestamp outside its declared window or inverted boundaries;
- counter reset/rollover and negative apparent delta;
- stale or future-dated observation;
- unit/metric mismatch;
- scope, resource, window or reset-epoch mismatch;
- shared-bucket / provider-only unattributed consumption;
- unknown billing or unsupported no-cost claim;
- missing or mismatched pricing snapshot/model version;
- reconciliation residual and incomplete source coverage.

Each finding records finding_id, finding_type, severity, affected source refs, observed scope/window, first/last observed timestamps, disposition, and resolution evidence. Unknown is a first-class state; it is never normalized to zero.

### Derived economic measures

Keep the following separate in the value board and source data:

- **Repo time investment value** = measured repository human/agent time × an explicitly documented valuation rate.
- **Repo time opportunity cost** = value of the best feasible alternative use of those resources that was forgone. A time-rate proxy qualifies only when its rate is explicitly grounded in that alternative-use value.
- **Paid-equivalent API value** = observed attributable workload repriced against the matching provider/model/version paid rate card.
- **Verified free-quota/credit coverage** = usage explicitly evidenced as covered by a free entitlement or credit.
- **Observed provider cost** = authoritative billed cost, where available.
- **Potential time recovered** = a scenario until measured against a comparable baseline.

A paid-equivalent estimate does not establish free-tier coverage, and verified no-cost billing status does not by itself establish which entitlement covered a particular event.

### Acceptance fixtures

The offline contract suite should cover exact model/instance attribution; exact provider-only attribution; shared-bucket unattributed totals; activity-only records; waived historical rows; post-mandate pending and fault states; duplicate replay; counter rollover; stale/future timestamps; missing provenance; metric/unit mismatch; unknown billing; pricing snapshot/version mismatch; mismatched reconciliation scope; and a non-zero reconciliation residual.

Projections must be deterministic, preserve source refs and evidence states, expose freshness/completeness/reconciliation status, and leave unresolved findings visible. Existing readers and projection scripts remain the integration points.
