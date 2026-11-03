# Decision log — visualization-renderer-lab

## 2026-11-02 — master-targeted continuation

- Operator explicitly designated `master` as the integration target.
- Created `research/visualization-renderer-lab-master` directly from the verified master HEAD; no merge or wholesale history transfer from `master-staging`.
- Existing staging-based research branch remains intact as the parallel source lane. Only scoped renderer-lab artifacts are ported.
- Preview now includes the master ChartKit baseline, Observable Plot 0.6.17, and Sigma.js 3.0.0 with Graphology 0.25.4; D3, Vega-Lite, ECharts and Cytoscape remain pinned.
- Fixture remains deterministic and synthetic. No live telemetry is loaded into the preview.
- Production work is limited to fail-closed input handling, atomic snapshot publication, provenance/freshness display, and null-gap correctness. No live feed values are fabricated or rewritten.
- No production deployment, DNS, database, credential or provider configuration is changed.
- Linear tracking is intentionally skipped per operator instruction.

## Evidence boundary

- The renderer scorecard has not yet been measured in real browsers; implementation status is not a performance win.
- The current master Tribute status snapshots are empty; their writer path and collector resilience are being hardened, but this branch cannot repopulate the snapshots without a trusted workflow run.
- Vercel rate-limit failures are external checks and do not establish code correctness or failure.
