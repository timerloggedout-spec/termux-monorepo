# ITEMS — actions-architecture-evolution

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| AAE-001 | P1 | executing | Establish typed automation entity model, stable identity, classification, authority, dependencies, and modularization lineage. | Versioned contract distinguishes workflow, reusable workflow, composite action, skill, AppID identity, execution receipt, DoE observation, BRR observation, and display event; lineage and unknown-state semantics are explicit. |
| AAE-002 | P1 | queued | Amend DoE Questions Matrix with topology and execution-identity factors; define the standing campaign design. | Dimensions 41–42 are additive; existing dimensions retain meaning; topology and AppID identity remain orthogonal factors; design record binds source SHAs and configured identity. |
| AAE-003 | P1 | queued | Crosswalk AppID migration gates and BRR/QUE evidence contracts into the architecture model. | Five AppID gates map to receipts; BRR captures baseline SHA, pagination/parse completeness, per-branch evidence, and structured capacity deferral; regression fixtures cover malformed rows and incomplete pages. |
| AAE-004 | P0 | queued | Implement the deterministic read-only automation feed collector and automated refresh workflow. | Scheduled + source-triggered collection, `workflow_dispatch`, stable refresh PR, deterministic output, clean no-op when unchanged, schema/provenance/stale/empty-state tests. |
| AAE-005 | P0 | queued | Publish the feed and Tribute Automation Architecture page through our existing GitHub Pages pipeline. | Merge to `master` triggers `tribute-dashboard-deploy.yml`; monorepo `gh-pages` and user-site `/tribute/` + `/help-wanted/` artifacts publish; live URL/source-SHA verification passes. |
| AAE-006 | P1 | queued | Build the Tribute Automation Architecture display page. | Existing Tribute chrome and chartkit conventions; feed-only rendering; accessible filters/statuses; evidence links; freshness stamps; responsive event cards. |
| AAE-007 | P3 | reference | Preserve the existing Repo-Story concept as a linked architecture reference. | Cross-reference existing concept artifacts and pilot records; no new product implementation or MVP dependency. |

## Validation

- `python3 scripts/proposals/validate_registry.py`
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- focused schema, collector, and page tests to be added with AAE-002–AAE-005

Automation updates and GitHub Pages publication are explicit P0 delivery gates. The collector's Actions run, refresh PR, publisher run, deployed version manifest, and live URL check form the end-to-end receipt chain. Queued/running remains pending.
