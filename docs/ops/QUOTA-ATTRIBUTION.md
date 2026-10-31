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
