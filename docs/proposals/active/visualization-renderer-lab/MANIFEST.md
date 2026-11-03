---
id: visualization-renderer-lab
title: "Dashboard surfaces and comparative visualization renderer lane"
author: ChatGPT
posted_at: 2026-11-02
source: source.md
status: executing
priority: P0
path: active/visualization-renderer-lab/
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: [1571]
related_prs: []
related_branches: [research/visualization-renderer-lab-master]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — visualization-renderer-lab

## Summary

Continue the existing parallel renderer preview on the canonical `master` base. Deliver a reproducible, synthetic-data comparison across ChartKit, D3, Observable Plot, Vega-Lite, ECharts, Cytoscape and Sigma; harden source snapshot ingestion and publication; preserve chart provenance, freshness and null-gap semantics.

## Review log

### 2026-11-02 — Operator / ChatGPT
- Disposition: executing on a branch created directly from `master`.
- Operator explicitly designated `master` as the integration target.
- Linear is intentionally skipped; this proposal and its branch are the execution ledger.
- Scope excludes deployment, credentials, DNS, database writes and provider migration.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] Work items defined
- [ ] All browser renderers independently verified in browser
- [ ] Performance/accessibility scorecard completed
- [ ] repo-gate and Termux smoke green on candidate SHA
- [ ] Non-author implementation review recorded
- [ ] Selective promotion reviewed

## Links

- Existing visualization RFP: https://github.com/timerloggedout-spec/termux-monorepo/issues/1571
- Canonical chart standard: `docs/ops/DASHBOARD-CHART-STANDARD.md`
- Telemetry visualization recon: `docs/ops/TELEMETRY-VIZ-RECON.md`
- Preview: `experiments/visualization-renderers/index.html`
