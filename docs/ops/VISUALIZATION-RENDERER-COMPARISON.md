# Visualization renderer comparison

**Status:** master-targeted research lane · 2026-11-02  
**Proposal:** `visualization-renderer-lab`  
**Existing RFP:** [#1571](https://github.com/timerloggedout-spec/termux-monorepo/issues/1571)

## Architecture

Canonical committed feeds → schema/provenance/freshness checks → shared synthetic fixture → renderer adapters → correctness/accessibility/performance scorecard → selective promotion.

The browser lab does not fetch production feeds or write snapshots. The synthetic fixture is explicitly labeled and deterministic.

## Implemented preview adapters

| Renderer | Pinned version | Workloads | State |
|---|---:|---|---|
| Master ChartKit | repository source | lightweight bars/lines | baseline rendered |
| D3.js | 7.9.0 | hierarchy, force network | rendered |
| Observable Plot | 0.6.17 | time series | rendered |
| Vega-Lite | 5.21.0 | declarative time series | rendered |
| Apache ECharts | 5.6.0 | interactive time series | rendered |
| Cytoscape.js | 3.30.4 | network | rendered |
| Sigma.js | 3.0.0 | WebGL network | rendered |
| Graphology | 0.25.4 | Sigma graph model | rendered |
| Native SVG | browser platform | time series | fallback baseline |

"Rendered" means the adapter is implemented in the preview; it is not a benchmark result or independent browser verification.

## Contract

- Source data remains committed snapshots; preview uses only `data_class=synthetic`.
- Every source records path, SHA-256, byte count, source timestamp, age and state.
- Empty, malformed, missing, naive-timestamp and stale sources are explicitly unavailable/partial/stale; no fabricated zero values.
- Null observations remain gaps, not interpolated or connected.
- Charts expose units, axis labels, time bounds and an accessible data table.
- Feed freshness is per source; a fresh top-level collection timestamp never masks stale inputs.

## Scorecard still required

Score each workload separately for correctness, keyboard/screen-reader access, touch interaction, p50/p95 render time, memory, payload, mobile behavior, static/offline behavior and maintenance cost. Use 100/1,000/10,000 nodes or points where applicable. Do not average away a correctness or accessibility failure. No global winner is selected.

## Reproduction

```bash
python3 scripts/visualization_lab/validate_cohort.py
python3 -m unittest discover -s tests -p 'test_visualization_lab.py' -v
python3 -m unittest discover -s tests -p 'test_telemetry_feed_resilience.py' -v
python3 -m unittest discover -s tests -p 'test_chartkit.py' -v
```

Open `experiments/visualization-renderers/index.html` with a static HTTP server. Libraries are pinned by exact CDN version. CDN failure is reported as renderer-unavailable, not fixture failure.

## Promotion

ChartKit remains the production baseline. No renderer dependency is added to production until scorecard, license/security, accessibility, performance and dual-gate evidence pass.
