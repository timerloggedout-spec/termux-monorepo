# ops/que — QUE feeds (producer: Optimizations & Assurance)

The QUE side of the Desk-upgrade commission (owner order
2026-11-04): the Desk holds the board; this directory is the
producer's served state. One collector
(`scripts/que/que_feed_collect.py`, workflow
`que-feed-collect.yml`, cron */10, single-flight, commits
via the Termux Fleet Swarm App) refreshes:

| File | Schema | Contents |
|---|---|---|
| `feeds/queue-feed.json` + mirror `apps/tribute-dashboard/data/que-queue-feed.json` | `que-queue-feed/v1` | **The producer-of-record feed for the Desk surface** (Desk-upgrade LEG ①): run-queue state by tier + dispatch claims folded live at publish from `ops/challenge/dispatch-state-feed.json`. Byte-identical canonical + mirror pair. Provenance carries the design input under its internal-label constraint (owner 2026-11-04: the label is internal only, ™-collision stamped, never a published surface name). |
| `feeds/queue-by-tier.json` | `que.queue-by-tier/v1` | Queued + in-progress census classified by tier (`ops/quota/dispatch-tiers.json`: first pattern match wins on workflow name, default tier 4). Wedged ancients (>7d queued) are excluded from counts and listed. |
| `feeds/priority-windows.json` | `que.priority-windows/v1` | Priority windows from the tiers `priority_window` stanza, state computed against the cycle time. Ships `windows: []` with the source named until the stanza lands (PR #4740). |
| `feeds/governor.json` | `que.governor/v1` | The **admission census**: admission thresholds + the deferral census folded from swarm-admission stamps (`deferred-by-tier` label). The **governor plane of record is Cadence's `que-governor-feed/v1`** (`ops/quota/que-governor-feed.json` + dashboard mirror — state · deferrals · priority windows; Desk reconciliation 2026-11-04): this feed's state section points at it, and Cadence's T1 batches (`que-governor-event/v1` in `events/governor-events-*.jsonl`) fold alongside as evidence. The board labels both feeds by source. |
| `events/YYYY-MM-DD.jsonl` | transition events | The T1 measurement plane (QUE.md): `{at, run_id, workflow, tier, event: queued\|started\|completed\|cancelled\|vanished, queue_wait_s?, conclusion?}` diffed per cycle against `feeds/state.json`. Repo snapshots are the store of record; `vanished` rows are the gap class for the ≤1% census-gap measure. Governor batches land alongside as `events/governor-events-<date>.jsonl` (Cadence's emitter; this collector folds, never authors). |
| `feeds/state.json` | internal | The differ's working state (active runs + watermark). Working copy, not a consumer surface. |

Consumers: the Desk surface (board) · Quota/Cadence · DoE —
per the consumer contracts in `docs/ops/QUE.md` (PR #4624).
