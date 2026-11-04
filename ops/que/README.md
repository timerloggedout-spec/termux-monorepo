# ops/que — QUE feeds (producer: Optimizations & Assurance)

The QUE side of the Desk-upgrade commission (owner order
2026-11-04): the Desk holds the board; this directory is the
producer's served state. One collector
(`scripts/que/que_feed_collect.py`, workflow
`que-feed-collect.yml`, cron */10, single-flight, commits
via the Termux Fleet Swarm App) refreshes:

| File | Schema | Contents |
|---|---|---|
| `feeds/queue-by-tier.json` | `que.queue-by-tier/v1` | Queued + in-progress census classified by tier (`ops/quota/dispatch-tiers.json`: first pattern match wins on workflow name, default tier 4). Wedged ancients (>7d queued) are excluded from counts and listed. |
| `feeds/priority-windows.json` | `que.priority-windows/v1` | Priority windows from the tiers `priority_window` stanza, state computed against the cycle time. Ships `windows: []` with the source named until the stanza lands (PR #4740). |
| `feeds/governor.json` | `que.governor/v1` | Admission thresholds + the deferral census folded from swarm-admission stamps (`deferred-by-tier` label). The PAT flow governor's live state is `NOT_ESTABLISHED` with the gap named until governor events join the T1 stream (Cadence seam). |
| `events/YYYY-MM-DD.jsonl` | transition events | The T1 measurement plane (QUE.md): `{at, run_id, workflow, tier, event: queued\|started\|completed\|cancelled\|vanished, queue_wait_s?, conclusion?}` diffed per cycle against `feeds/state.json`. Repo snapshots are the store of record; `vanished` rows are the gap class for the ≤1% census-gap measure. |
| `feeds/state.json` | internal | The differ's working state (active runs + watermark). Working copy, not a consumer surface. |

Consumers: the Desk surface (board) · Quota/Cadence · DoE —
per the consumer contracts in `docs/ops/QUE.md` (PR #4624).
