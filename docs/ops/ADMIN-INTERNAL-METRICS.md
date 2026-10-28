# Admin internal metrics — rendering contract

Owner correction (2026-10-28, via challenge manager): internal metrics
render in the **Admin Panel only** — an internal surface. They never
render on public feeds, pages, logs, briefs, or ledgers. This supersedes
the earlier "silent + hidden everywhere" posture for the admin surface
only; everywhere else the hidden rule stands unchanged.

## Metric in scope

`win_probability` — source of record:
`ops/challenge/coordinator.json` → `events[].metrics_internal.win_probability`

Shape (`winprob/v1`, landed PR #2229):

```jsonc
{ "method": "winprob/v1",
  "estimate": 0.025 | null,          // null = not established, never 0
  "inputs": { "award_slots_top": 1, "field_size": 40 | null,
              "field_scored_count": 0, "field_mean_composite": null,
              "our_composite": null },
  "computed_at": "RFC3339 UTC" }
```

State at contract landing (verified on master by the admin-panel lane):
7 events carry the block; only D0 has a non-null estimate (0.025,
field_size 40); all others are null pending the field-size OSINT pass.

## Amendment 2026-10-28 (challenge manager alignment)

- **Unsourced `field_size` is an OPEN TASK, not a settled
  "not established".** The two states are distinct in the UI:
  an estimate that does not exist yet renders `not established`;
  a field_size with no source renders **OPEN TASK**.
- **Delivery vehicle = admin feed `challenge-admin-metrics/v1`**
  (challenge lane's data PR, lands with the field-size count pass).
  Per event it carries `field_size_status: established | open_task`
  alongside the win-probability block. The admin renderer consumes
  this feed; it does not read the coordinator record directly and
  never computes values itself.
- **MoneyBall-refined estimates:** where the MoneyBall method supports
  one, the feed carries a refined `estimate` **plus its `basis`**
  (internal), replacing the coordinator null for that event. The panel
  renders estimate + basis verbatim from the feed; a null that the
  feed still carries renders `not established`.

## Amendment 2026-10-28 #2 (feed landed, PR #2244)

Feed verified on master by the admin-panel lane: schema
`challenge-admin-metrics/v1`, `surface` designation = admin panel only,
7 events. `field_size_status` carries a **third state, `partial`**
(the v1 amendment named only two — this amendment adopts the landed
reality): participants sourced, projects (the winprob base field)
not yet established.

| Status | Events at landing | Render |
|---|---|---|
| `established` | D0 | participants + projects numbers |
| `partial` | STRANDS-DECIDER, D1, D2, D4 | participants number + **PARTIAL** chip; projects null → `not established` |
| `open_task` | D3, D5 | **OPEN TASK** (no numbers) |

Estimates at landing: D0 0.025 only; all others null until MoneyBall
refinement arrives via this feed (estimate + basis). The designated
admin feed file itself (`data/challenge-admin-metrics.json`) is the
sole permitted data-file carrier of these values — it is an internal,
designation-level surface (same exposure class as the public repo);
the forbidden-surface scan below excludes it by name.

## Rendering rules (admin view of challenge data)

1. Render the block per event: estimate (as % when non-null, the words
   `not established` when null — never render null as 0 or blank),
   method, `computed_at`, and the inputs (field_size, field_scored_count,
   our/field composites when present). Render `field_size` by its
   `field_size_status`: the number when `established`, the words
   **OPEN TASK** when `open_task`. Where the admin feed carries a
   MoneyBall-refined estimate, render its `basis` next to the estimate.
2. Label the block **internal** in the UI; no export/share affordance.
3. The admin renderer reads values from the `challenge-admin-metrics/v1`
   admin feed only (which the challenge lane derives from the coordinator
   record + MoneyBall refinement) — it must not copy values into any
   public feed, page, log, brief, or the opportunity ledger
   (ledger = 1st-place gross only).
4. Null estimates stay visible as nulls in admin (absence of an estimate
   is itself information); do not backfill from other sources.

## Amendment 2026-10-28 #3 (winprob/v2, spec PR #2250, feed PR #2251)

Verified on master by the admin-panel lane: all 7 events now carry
`method: winprob/v2` with shape `{estimate, range, confidence, prior{},
standing{}, fit{}, unknowns{}, basis, computed_at, superseded_v1{}}`.
The v1 `inputs{}` object is **gone** — renderers must not read it.

Render rules (supersede rule 1 where they conflict):

- Estimate cell: % (lossless format) + range when non-null, rendered
  as `est% (range lo%–hi%)`; **realized events** (estimate `0`,
  range `[0,0]`, confidence `high` — Decider + D0, closed with recorded
  outcome) render `0% — realized`, never a bare `0%` and never
  `not established`. Null estimate (D3/D5) → `not established`.
- Confidence renders as a pill: `high | low | none` verbatim.
- Detail column (replaces the v1 inputs column): prior
  (base_rate + denominator + kind), standing (our_composite /
  percentile / field_mean when non-null), fit, unknowns
  (unscored_share, unverified_axis_weight_share) — verbatim, nulls
  shown as `—`.
- `superseded_v1` is history: at most a collapsed/secondary note
  (`v1: <estimate>`), never the headline value.

Acceptance additions: (d) v2 fields render per above on all 7 events;
(e) no renderer reads `inputs` or any v1 field for headline values.

## Forbidden surfaces (acceptance scan)

`win_probability` / `metrics_internal` must return **zero hits** in:
`apps/help-wanted-dashboard/**` public pages and `data/*.json` feeds
**except** the admin view surface itself and its designated feed
`data/challenge-admin-metrics.json`, the opportunity ledger
(`ops/challenge/opportunity_ledger.json` + its doc), challenge briefs
and logs. At contract landing the repo-wide hit list is exactly:
`docs/ops/MONEYBALL-PLANE.md`, `docs/ops/CHALLENGE-SCHEMA.md`,
`docs/ops/CHALLENGE-PARTICIPANT-MIRROR.md`,
`ops/challenge-participants/schema.sql`, `ops/moneyball/plane.json`,
`ops/challenge/coordinator.json` — no page or feed hits.

## Ownership + acceptance

- Data: challenge / MoneyBall lanes (coordinator record, winprob/v1).
- Wiring: Web Design lane builds the admin view.
- Acceptance: Linguist Admin Panel lane — (a) admin view shows the
  block for all 7 events with correct null handling (estimate null →
  `not established`; field_size `open_task` → OPEN TASK; refined
  estimates show their basis); (b) forbidden-surface
  scan stays zero outside the admin view; (c) estimates beyond D0 appear
  only as delivered by the `challenge-admin-metrics/v1` feed after the
  field-size count pass (the panel never computes or estimates values
  itself).
