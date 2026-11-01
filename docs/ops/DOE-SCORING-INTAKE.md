# DoE scoring intake spec

What DoE scoring consumes from routed dispatch work (Swarm-owned
routing, owner update 2026-11-01). Routing that emits these fields
populates DoE scoring from live work across all arms; dispatches
missing required fields score as OBSERVATIONAL only (DOE-FAMILY
rule 5), never as designed results.

## Per-dispatch stamp (required at dispatch time)

| field | format | notes |
|---|---|---|
| provider | string | arm identity, as named in the registry |
| model | `name@version` | configured-instance tuple member |
| system_prompt | `<ref>#<sha256[:12]>` | repo path, else `prompt:<moniker>:<slug>` |
| tools | `<ref>#<sha256[:12]>` | same ref scheme |
| role / moniker / context | strings | tuple members; instance_key = sha256 of the canonical tuple JSON — stamp either the tuple or the precomputed `instance_key` |
| entry | id | the work item dispatched (issue/entry id) |
| trigger | id | what fired the dispatch |
| set_index / cumulative_n | ints | DOE-FAMILY rule 7 (sets of 3, auditable looks) |
| selection_reason | string | why this arm (rotation, task-fit, reselection) |
| ts | ISO-8601 Z | dispatch timestamp |

## Outcome fill (required at PR/merge close)

| field | format | notes |
|---|---|---|
| first_pass_success | bool | PR merged with no rework dispatch |
| rework_cycles | int | rework dispatches for the unit |
| dispatch_to_pr_wall_time | seconds | or stamp pr_ts/merge_ts and scoring derives it |
| stalled_action_required | bool | wiring-health signal (rule 6 re-verification) |
| pr | PR number/URL | evidence pointer |

## Usage slots (EXPERIMENT schema rev 1.1, when the provider returns them)

`session_id` · `window {start, end}` · `usage {value, unit, source,
match, status}` with status in {measured, estimated, activity_only,
not_established}; value is null unless measured/estimated. Arms
that return no usage omit the slot — never fabricate zeros.

## Carriers

- Live stamps: desk-feed `traversals[].provider_usage[]`
  (desk-feed/v1.3 shape; util-1 auditor reads exactly this).
- Scored records: one EXPERIMENT.schema.json-conforming JSON per
  unit under the campaign's `records/`.
- Bench membership is read from `ops/quota/registry.json` at score
  time (rule 6: routes re-verified, never pinned).

## Backfill and versioning (owner doctrine, 2026-11-01)

Backfill is a standing first-class mechanism, not a fallback. At
every version change of a scoring test or definition, historical
records are re-scored under the new version by the backfill method
— itself a versioned, improvable artifact — and the backfill is
audited. Records therefore carry an origin field: `live`, or
`backfill` with {method, method_version, from_version, to_version}.
Results are compared across versions continuously until DoE
culling retires a method version, ending that version's comparison
line. Origin is never laundered: a backfilled score is reported as
backfilled, a live score as live.

## Populated-scoring report

doe-expert reports to main when an auditor cycle first shows
scored units with non-null outcomes originating from live routed
dispatches (not backfill): threshold = at least one full set
(n=3) with outcomes filled at close.
