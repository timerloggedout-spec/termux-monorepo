# Dispatch-Tree Feed — cadence & admission state for quota-dispatch-tree.yml

The contract for the dispatch-tree feed, sibling to the Oracle Panel feed
(`docs/ops/ORACLE-PANEL-FEED.md`) and the surface feeds
(`docs/ops/DASHBOARD-SURFACE-FEEDS.md`). It exists because the dispatch
tree's state — which lanes are due, whether Node A's admission guard is
open, what each tree run actually woke — was previously visible only
inside per-run job summaries (gap G-02 follow-up; fixes PR #1759 and
PR #1815).

## Feed

| Item | Value |
|---|---|
| Feed | `apps/help-wanted-dashboard/data/dispatch-tree-feed.json` |
| Schema | `dispatch-tree-feed/v1` — `{schema, surface, generated_at, sources, honesty_rules, data, gaps}` |
| First visualization | `apps/help-wanted-dashboard/dispatch-tree.html` (standalone prototype; page integration owned by the Web Design Specialist lane) |

`data` holds three blocks:

- **`lanes[]`** — one entry per lane in the tree's dispatch matrix
  (32 at first collection): workflow file, the decide output that gates
  it, the firing-rule expression extracted verbatim from
  `.github/workflows/quota-dispatch-tree.yml`, whether the rule is
  admission-gated (`!paused`), its lane-age staleness threshold where the
  workflow defines one (refresh 75m, pair 150m, execute 300m, assist
  450m, q6 dynamic — see below), the measured age the tree itself would
  use, latest + recent runs, and `due_at_read` (`null` for phase-only
  lanes — no staleness threshold exists to be due against).
- **`admission`** — Node A: the guard threshold (6, parsed from the
  workflow), the guard expression, what the comment says ("lane runs")
  vs what the code counts (all repo runs, queued + in-progress, no
  workflow filter), the current sample, the per-workflow breakdown of
  what is actually queued/running, and an append-only `samples` series.
- **`tree_runs[]`** — recent tree runs with the lanes each actually woke
  (from dispatch jobs' `Wake lane` step conclusions: success = woken,
  skipped = not), plus the Supabase persistence step's conclusion.

## Collectors

Two steps, mirroring the surface-feed pattern (the feed collector never
calls the network):

1. `scripts/dashboards/dispatch_tree_observe.py` — reads the GitHub
   Actions API firsthand (token from `GITHUB_TOKEN`/`GH_TOKEN`) and
   writes the stamped snapshot
   `scripts/dashboards/dispatch_tree_observation.json`
   (`dispatch-tree-observation/v1`). Repo variable *names* only are
   recorded; no values.
2. `scripts/dashboards/dispatch_tree_feed.py` — parses the workflow file
   for rules/thresholds/matrix and joins it with the snapshot to emit
   the feed. Re-running appends the snapshot's busy reading to the
   feed's `admission.samples` (deduped by `read_at`, capped at 500).

Refresh = re-run both, land by PR. Feeds are never hand-edited.

## Honesty rules

Carried in the feed itself (`honesty_rules`); the load-bearing ones:

- Busy history before the first collection does not exist in any record
  the collector can read and is never backfilled — the sample series
  starts at the first snapshot's `read_at`.
- The decide step's "Decision tree verdicts" summary table is not
  exposed by the Actions API; verdicts here are the equivalent evidence
  from dispatch jobs' step conclusions.
- Supabase `dispatch_verdicts`: repo variables `SUPABASE_URL` /
  `SUPABASE_ANON_KEY` are present and the persistence step concludes
  success on observed runs, and the REST endpoint answers — but anon
  SELECT returns no rows (insert-only RLS, per the workflow's own
  comment), so row contents are not a feed source.

## The q6 dynamic threshold

`dispatch_q6`'s staleness threshold is not a constant: the tree derives
it each run as 1.5× the median gap between provider-availability's 5
most recent runs, clamped to [120, 720] minutes (fallback 360). The
collector derives it the same way from the snapshot and records
`threshold_derived_from`; `measured_age_min_at_read` for q6 lanes is
provider-availability's age, because that is the age the tree measures.

## What this feed does not do

It presents the Node A evidence; it does not change the guard. Whether
`busy >= 6` should count all repo runs or only lane runs is a
quota-policy decision for the owner / tree owners.
