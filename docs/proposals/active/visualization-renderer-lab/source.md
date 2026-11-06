# Source and decision basis

## Operator direction

The operator requested a full dashboard-surface audit and visual upgrade, live/latest snapshot-aware graphs, alternate renderer implementations, and explicitly designated `master` as the target. The parallel renderer preview is retained and upgraded, not replaced by a second unrelated prototype. Linear tracking is skipped by instruction.

## Verified master sources

- Existing RFP: issue #1571 (`web.visualization_layers`).
- Chart standard: `docs/ops/DASHBOARD-CHART-STANDARD.md`.
- Visualization recon: `docs/ops/TELEMETRY-VIZ-RECON.md`.
- Existing telemetry feed: `apps/tribute-dashboard/data/telemetry-feed.json`.
- Feed builder: `scripts/dashboards/telemetry_feed.py`.
- History builder: `scripts/dashboards/telemetry_feed_series.py`.
- Page: `apps/tribute-dashboard/telemetry.html`.
- Shared production renderer: `apps/tribute-dashboard/chartkit.js`.
- Status writer: `scripts/ci/tribute_status.py`.
- Status outputs: `apps/tribute-dashboard/data/status.json` and `docs/ops/generated/tribute-status.json`.
- Collector workflow: `.github/workflows/surface-feeds-collect.yml`.

## Revalidated data boundary

- Both Tribute status JSON paths on master are zero bytes and share blob SHA `bb2f8218accf56b4279665f40a9aeeb04e7dca49`.
- Telemetry feed stamp: `2026-10-30T07:47:32Z`; the history file contains two rows dated 2026-10-30.
- The collector previously called `json.loads` directly on existing source files; an empty file raised JSONDecodeError rather than producing a named unavailable-source state.
- Status writer used direct `Path.write_text` for both JSON outputs, exposing readers to truncation during replacement. Atomic replacement is the hardening change; it does not establish why the committed files became empty.
- Existing workflow push paths omitted `scripts/dashboards/actions_observations.json`.
- A collector run that regenerates the feed has not been verified through the connected GitHub workflow-run tool.

## Branch topology and integration

The previous `research/visualization-renderer-lab` branch is 24 commits ahead of `master-staging`, but GitHub reports it diverged from `master` by thousands of commits. This continuation branch was created directly from master HEAD `56c3105758ef8e8223ece48421afa5071ed9d531`. Only the scoped renderer-lab files are ported; no staging history or unrelated application changes are merged.

## Renderer candidates

- ChartKit (master): lightweight production SVG baseline.
- D3 7.9.0: hierarchy, force graphs and custom interaction.
- Observable Plot 0.6.17: statistical/time-series charts.
- Vega-Lite 5.21.0: declarative statistical visualization.
- ECharts 5.6.0: interactive operational charts.
- Cytoscape.js 3.30.4: network graph operations and layouts.
- Sigma.js 3.0.0 + Graphology 0.25.4: WebGL-oriented network visualization.

## Evidence and limitations

All renderer implementations use the same synthetic fixture. No live feed is fetched by the preview. Performance, memory, accessibility and mobile scorecards are not yet measured; implementation does not equal a winning result. Production ChartKit remains authoritative until a workload-specific evidence review approves any replacement.
