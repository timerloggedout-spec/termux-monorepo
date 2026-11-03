# Work items — visualization-renderer-lab

| ID | Priority | Work | Status | Acceptance evidence |
|---|---:|---|---|---|
| VIZ-01 | P0 | Establish deterministic synthetic cohort for hierarchy, network and time-series workloads. | done | Versioned fixture + validator |
| VIZ-02 | P0 | Upgrade isolated browser preview with all renderer adapters and the master ChartKit baseline. | done | D3, Plot, Vega-Lite, ECharts, Cytoscape, Sigma, ChartKit and native SVG |
| VIZ-03 | P1 | Inventory published web surfaces, source feeds, writers, freshness, navigation and deployment targets. | in_progress | Existing chart standard + evidence-backed surface audit |
| VIZ-04 | P1 | Compare renderers against identical workload cohorts. | in_progress | Shared fixture; scorecard measurements still required |
| VIZ-05 | P0 | Fail closed on empty/malformed/provenance-free snapshots and distinguish partial/stale feeds. | in_progress | Snapshot validator + collector regression tests |
| VIZ-06 | P1 | Upgrade shared web design tokens, navigation, responsive layout and accessible graph states. | todo | Representative screenshot, keyboard and contrast evidence |
| VIZ-07 | P2 | Evaluate optional providers only against demonstrated requirements. | todo | No provider migration or paid resource without evidence |
| VIZ-08 | P0 | Make telemetry source ingestion resilient and attach per-source SHA, timestamp, age and state. | in_progress | Missing/empty/malformed/stale fixture tests |
| VIZ-09 | P0 | Publish Tribute status snapshots atomically to prevent partially written/empty reader windows. | done | Atomic-write unit test; real workflow repopulation still pending |
| VIZ-10 | P1 | Preserve null observations as chart gaps in the telemetry history renderer. | done | ChartKit regression test + telemetry page null-preserving adapter |

## Guardrails

- Canonical data remains committed feeds/snapshots; preview fixture is synthetic and never presented as live telemetry.
- No production renderer dependency is added; ChartKit remains the production baseline.
- Missing, stale, null and unverified remain distinct from zero.
- No wholesale merge of `master-staging`; the master branch is the integration base for this continuation.
- No DNS, hosting policy, database, credential or provider changes.
