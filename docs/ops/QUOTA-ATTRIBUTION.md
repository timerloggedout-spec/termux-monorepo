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
