# DASHBOARD CHART STANDARD — every surface carries a live chart

Owner standard 2026-11-01 22:28 PT: **all surfaces require live chart
graphs.** Every page in the dashboard family (`apps/help-wanted-dashboard/`)
carries at least one chart that is live-fed — not just the quota pages —
and every rate-limit event must be visible on the quota graphs.

## The standard

A page complies when its chart(s) satisfy all of:

1. **Feed-only data.** The chart renders exclusively from the page's
   feed file(s) — the same feed the page already consumes. No hardcoded
   points, no page-local numbers, no values copied from another surface.
2. **Stamped.** The feed's `generated_at` renders beside the chart.
   A feed without a stamp renders "stamp unknown" — never a silent pass.
3. **STALE-flagged.** Staleness shows next to the chart: for time
   series, per-series from its own last point (PR #3540 pattern —
   a fresh series never masks a stale one); for snapshot feeds, when
   the feed age exceeds 24h (or the feed's declared cadence, if longer).
4. **Automated chain.** The feed regenerates through its existing
   automation (workflow / single-writer collector). A chart fed by a
   hand-built pack names that gap on the page and in this audit.
5. **Legibility floor.** Axes are never omitted: bar charts label every
   value and state the max; line charts carry y ticks (min/mid/max)
   and first/last date labels. (Lesson of the 2026-11-01 visual
   inspection: axis-less sparklines and 5000/0-only axes are defects.)
6. **Events are data.** Incidents (rate-limit 403s, walls) render as
   markers from an events register — on quota-graphs from
   `ops/quota/rate-limit-events.json` (PR #3548 + #3564) — never as
   prose-only annotations.

Shared implementation: `apps/help-wanted-dashboard/chartkit.js`
(`CK.bars`, `CK.line`, `CK.stampState`) — pure string builders, pinned
by `tests/test_chartkit.py`. Pages with richer renderers (quota-graphs)
keep them; the standard governs data + stamps, not the drawing code.

## Audit — 2026-11-02 (firsthand, Web Design lane)

| page | chart state | feed |
|---|---|---|
| quota-graphs.html | ✓ compliant (series + events, per-series STALE, auto-regen) | usage-series.json |
| quota-usage.html | ✓ chart; CHAIN GAP: pack refresh is manual | quota-usage.json |
| admin-graph.html | ✓ graph surface | challenge-admin-metrics.json |
| countdowns.html | ✓ visual timers off feed | challenge-countdowns-feed.json |
| quota.html | ✓ headroom + state charts (chartkit, PR #3573) | quota.json |
| index.html | ✓ receipts-by-kind + outcomes charts (chartkit) | status.json |
| owner-records.html | ✓ records-by-class bar (chartkit) | owner-records envelope |
| family.html | ✓ nested tree + tasks-per-provider/outcome charts (chartkit); chrome (nav) PR follows | nested-family-feed.json |
| quota-swarm.html | ✓ layers funnel + records-per-family + events timeline (chartkit) + chrome (PR #3620) | swarm-feed.json + nested-family-feed.json |
| quota-event-audits.html | ✓ coverage + findings-by-state/class charts (chartkit); chrome (nav) rides the canon normalization | rate-limit-event-audits.json + register |
| 3l0.html | ✓ review cycles per provider (chartkit) | 3l0-feed.json |
| ates.html | ✓ observed runs per workflow (chartkit) | ates-feed.json |
| doe.html | ✓ campaigns by state + runs per campaign (chartkit) | doe-feed.json |
| mvt.html | ✓ experiment record population (chartkit) | mvt-feed.json |
| moneyball.html | ✓ scoring weights + penalty magnitudes (chartkit) | moneyball-feed.json |
| oracle.html | ✓ proposals + passes by status (chartkit) | oracle-panel-feed.json |
| delphi-rfp.html | ✓ open RFPs by status + group (chartkit) | delphi-rfp-feed.json |
| delphi-ledger.html | ✓ events per ledger (chartkit) | delphi-ledger-feed.json |
| proposals.html | ✓ proposals by status + priority (chartkit) | proposals-feed.json |
| free-tier-value.html | ✓ list prices per model (input/output) (chartkit) | free-tier-value.json |
| admin.html | ✓ feed-freshness: age in hours per consumed feed (chartkit) | all admin feeds |
| desk.html | viz lane | desk-feed.json |
| dispatch-tree.html | viz lane | dispatch-tree-feed.json |
| linguist.html | viz lane | linguist-panel-feed.json |
| pr-lanes.html | viz lane (phase-2 trend already owed) | pr-lane-feed.json |
| telemetry.html | viz lane | telemetry-feed.json |
| tracking.html | viz lane | tracking-feed.json |
| versioning.html | EXCEPTION — meta compare tool; its table is the surface | version-manifest |
| lanes-and-scopes.html | EXCEPTION — static reference, no feed exists | — |
| matrix.html | OUT OF FAMILY — landing-repo surface, not the dashboard app | lane-matrix-status.json |

P1 = Web Design, reference implementations. P2 = Web Design on the
chartkit pattern. Viz-lane pages are built by the viz lane to this
standard (PM merge by Web Design). Exceptions stand until the owner
rules otherwise; an exception is a documented state, not an omission.
