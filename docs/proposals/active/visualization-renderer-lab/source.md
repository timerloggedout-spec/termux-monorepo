# Source and decision basis

## Operator direction

The operator requested a full web-surface audit and visual upgrade, with live/latest snapshot-aware graphs, and explicitly requested alternate implementation lanes such as D3.js and competing visualization/graph technologies. The operator then explicitly took over scope and directed that Linear usage be skipped.

## Existing repository evidence (checked 2026-11-02)

- Existing RFP: issue #1571, `web.visualization_layers`.
- Existing telemetry feed: `apps/tribute-dashboard/data/telemetry-feed.json`, schema `telemetry-viz-feed/v1`.
- Existing feed builder: `scripts/dashboards/telemetry_feed.py`.
- Existing history builder: `scripts/dashboards/telemetry_feed_series.py`.
- Existing page: `apps/tribute-dashboard/telemetry.html`.
- Existing renderer: `apps/tribute-dashboard/chartkit.js`, pure SVG string builders for bars/lines and feed-stamp state.
- Existing chart contract: `docs/ops/DASHBOARD-CHART-STANDARD.md`.
- Existing visualization research: `docs/ops/TELEMETRY-VIZ-RECON.md`.
- PR #3937 is recorded in the tracking snapshot as merged at 2026-11-02T14:20:07Z and adds telemetry feed refresh cadence to the surface collector.
- PR #3969 is recorded in the tracking snapshot as the next open task to synchronize the Vercel root directory; do not assume it is merged or deployed.
- Revalidated on 2026-11-02: both Tribute status JSON paths on master are zero bytes with identical blob SHA `bb2f8218accf56b4279665f40a9aeeb04e7dca49`. The telemetry feed is stamped `2026-10-30T07:47:32Z`, and its two-row history ends on 2026-10-30. The telemetry collector uses direct `json.loads` on existing source files, so the empty status file causes a hard decode failure rather than a named unavailable-source state. The latest workflow execution could not be retrieved through the connected GitHub tool surface; do not claim a collector run succeeded.

## Branch topology warning

GitHub compare reports `master-staging` and `master` diverged, with the compare capped at 10,000 commits (master-staging reported 10,497 ahead and 54 behind at collection). The dashboard implementation files were found on `master` but were not found at their expected paths on `master-staging`. This proposal therefore creates an isolated research scaffold only. No wholesale branch merge or production promotion is implied.

## Renderer shortlist

- D3.js: custom interaction, hierarchy, force layouts, transitions; higher implementation responsibility.
- Observable Plot: concise statistical charts and exploratory time series; not a general network-graph engine.
- Vega-Lite: declarative statistical visualization, repeatable specifications and grammar.
- Apache ECharts: broad interactive dashboard charts and data zoom; heavier general-purpose runtime.
- Cytoscape.js: graph/network layouts, selectors and graph interaction.
- Sigma.js: large network graph rendering with Graphology; WebGL-oriented.
- Existing ChartKit: tiny dependency-free SVG baseline for current static surfaces.

## Comparison principle

Use the same fixture cohort and explicit workload classes. Compare correctness and semantic fidelity first; then accessibility, interaction, rendering performance, bundle/runtime cost, mobile behavior, maintainability and deployment constraints. A library may win one workload and lose another. No universal winner is assumed.
