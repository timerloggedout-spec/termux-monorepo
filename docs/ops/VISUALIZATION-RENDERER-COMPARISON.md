# Visualization renderer comparison

**Status:** research lane scaffold · 2026-11-02  
**Proposal:** `visualization-renderer-lab`  
**Existing RFP:** [#1571](https://github.com/timerloggedout-spec/termux-monorepo/issues/1571)

## Architecture boundary

```
Canonical committed feeds / immutable snapshots
                   |
          schema + provenance checks
                   |
        shared workload fixture cohort
                   |
       +-----------+-----------+-----------+
       |           |           |           |
      D3       Plot/Vega    ECharts    Cytoscape/Sigma
       |           |           |           |
       +----------- renderer adapters ------+
                   |
       correctness + UX + performance scorecard
                   |
       selective recommendation / promotion
```

The experiment does not fetch production feeds, write snapshots, or change the canonical dashboard. The fixture is synthetic and fixed. Production adapters must later consume the existing page feed unchanged.

## Workload cohorts

| Workload | Required semantics | Primary candidates |
|---|---|---|
| Time series | timestamps, missing intervals, per-series freshness, nulls remain gaps | ChartKit, Observable Plot, Vega-Lite, ECharts, D3 |
| Hierarchy | parent/child identity, depth, collapse/expand, keyboard access | D3 hierarchy, ECharts tree, custom SVG |
| Network graph | stable node/edge IDs, directed links, labels, selection, focus, pan/zoom | D3 force, Cytoscape.js, Sigma.js |
| Dense event stream | time-window filtering, event markers, aggregation provenance | ECharts, Plot, Vega-Lite, D3 |
| Operational dashboard | multiple coordinated views, responsive sizing, empty/stale/error states | ChartKit, ECharts, Vega-Lite |

## Candidate matrix

| Renderer | Strong fit | Trade-offs / validation |
|---|---|---|
| Existing ChartKit | Lightweight static SVG; no runtime dependency | Limited interaction and graph layouts |
| D3.js | Bespoke hierarchy/force/interaction; maximal control | More custom code and accessibility responsibility |
| Observable Plot | Statistical/time-series charts with compact code | Not a network graph engine; verify interactivity requirements |
| Vega-Lite | Declarative repeatable chart grammar | Runtime/spec expressiveness and payload cost |
| Apache ECharts | Rich interactive dashboards, zoom and broad chart catalogue | Bundle size, accessibility and data transforms need measurement |
| Cytoscape.js | Network graph layout, selection and graph operations | Large graph performance and mobile interaction |
| Sigma.js | WebGL-oriented large network rendering | Graphology ecosystem and accessibility/labels need evaluation |

## Scorecard (no preselected winner)

Each candidate receives a 1–5 score with evidence and uncertainty for:
1. semantic correctness against the shared fixture;
2. accessibility (keyboard, focus, text alternatives, screen-reader behavior);
3. interaction fit (zoom, pan, brush, selection, linked views);
4. render time at 100 / 1,000 / 10,000 nodes or points as applicable;
5. memory and bundle/network payload;
6. mobile layout and touch ergonomics;
7. maintainability and adapter complexity;
8. static-hosting/offline behavior;
9. freshness/provenance display fidelity.

Do not average away a failed correctness or accessibility gate. Report workload-specific winners, p50/p95 timings, test environment, sample count, and confidence. Do not compare unlike workloads as if they were the same benchmark.

## Snapshot and freshness contract

- Source data remains the committed feed/snapshot, not browser-generated values.
- Carry `schema`, `snapshot_id` (when supplied), `source_sha`, `generated_at`, source list, coverage and per-series timestamps.
- Missing values stay null/unknown; gaps remain gaps; unverified is not zero.
- Render freshness per feed and per series. Do not infer a fresh series from a recent top-level stamp.
- Every chart exposes units, scale, axis labels, first/last observation and accessible tabular alternative.
- Browser experiment fixture is marked `synthetic`; no output may be labeled live.

## Reproduction

```bash
python3 scripts/visualization_lab/validate_cohort.py
```

Open `experiments/visualization-renderers/index.html` using a static HTTP server. Renderer libraries are pinned by exact CDN version in the page. The experiment gracefully reports when a CDN is unavailable; the fixture remains local.

## Promotion policy

No dependency is added to `apps/tribute-dashboard` until the relevant workload scorecard, security/license review, accessibility review, performance measurements and focused CI pass. Promotion is selective from the integration spine; never merge `master-staging` wholesale into `master`.
