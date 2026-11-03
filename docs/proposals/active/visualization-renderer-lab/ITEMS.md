# Work items — visualization-renderer-lab

| ID | Priority | Work | Status | Acceptance evidence |
|---|---:|---|---|---|
| VIZ-01 | P0 | Establish a deterministic, explicitly synthetic shared cohort for hierarchy, network, and time-series workloads. | done | `experiments/visualization-renderers/fixtures/renderer-cohort-v1.json`; stdlib validator |
| VIZ-02 | P0 | Publish an isolated browser lab with D3 baseline and alternative renderer adapters. | in_progress | `experiments/visualization-renderers/index.html`; pinned CDN versions; no canonical feed access |
| VIZ-03 | P1 | Inventory all published web surfaces, source feeds, writers, freshness, navigation, and deployment targets. | todo | Evidence-backed surface registry with verified/candidate/unresolved distinctions |
| VIZ-04 | P1 | Compare D3, Observable Plot, Vega-Lite, ECharts, Cytoscape, Sigma, and existing ChartKit against the same workload cohort. | todo | Correctness, accessibility, interaction, payload, render-time, memory and maintenance scorecard |
| VIZ-05 | P1 | Harden snapshot publication against empty/malformed/provenance-free outputs; revalidate Tribute status writer. | in_progress | Standalone fail-closed validator + regression tests; canonical writer integration remains open |
| VIZ-06 | P1 | Upgrade shared web design tokens, navigation, responsive layout and accessible graph states. | todo | Screenshot/keyboard/contrast checks on representative surfaces |
| VIZ-07 | P2 | Evaluate Netlify, Render, Supabase/Neon, Cloudinary, Temporal and API tooling only against demonstrated requirements. | todo | Provider decision records; no duplicate production services or unnecessary paid resources |

## Guardrails

- Canonical data remains committed source feeds/snapshots; lab fixture is synthetic and cannot be presented as live telemetry.
- Do not add renderer dependencies to the production dashboard until the comparative scorecard and operator review justify it.
- Never copy the divergent `master` dashboard tree wholesale into `master-staging`.
- Do not change production DNS, hosting, databases, workflows, credentials, or deployment policies in this lane.
- Preserve per-series freshness, source provenance, gaps, null/unknown/unverified semantics and visible axes.
