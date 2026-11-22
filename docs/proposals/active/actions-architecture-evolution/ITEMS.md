# ITEMS — actions-architecture-evolution

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| AAE-001 | P1 | executing | Establish typed automation entity model, stable identity, classification, authority, dependencies, and modularization lineage. | Versioned contract distinguishes workflow, reusable workflow, composite action, skill, AppID identity, execution receipt, DoE observation, BRR observation, and display event; lineage and unknown-state semantics are explicit. |
| AAE-002 | P1 | queued | Amend DoE Questions Matrix with topology and execution-identity factors; define the standing campaign design. | Dimensions 41–42 are additive; existing dimensions retain meaning; topology and AppID identity remain orthogonal factors; design record binds source SHAs and configured identity. |
| AAE-003 | P1 | queued | Crosswalk AppID migration gates and BRR/QUE evidence contracts into the architecture model. | Five AppID gates map to receipts; BRR captures baseline SHA, pagination/parse completeness, per-branch evidence, and structured capacity deferral; regression fixtures cover malformed rows and incomplete pages. |
| AAE-004 | P1 | queued | Implement the deterministic read-only automation architecture feed collector and feed contract. | Collector reads committed canonical records only; stable event IDs and deterministic ordering; missing evidence appears in gaps; tests cover schema, provenance, stale states, and empty feeds. |
| AAE-005 | P1 | queued | Build the Tribute Automation Architecture display page. | Existing Tribute chrome and chartkit conventions; feed-only rendering; accessible filters/statuses; evidence links; freshness stamps; responsive event cards. |
| AAE-006 | P2 | candidate | Evaluate Repo-Story as a narrative/temporal reconstruction extension. | Separate design and DoE admission; verified GitHub history remains distinct from candidate narrative; implementation begins only after explicit scope approval. |

## Validation

- `python3 scripts/proposals/validate_registry.py`
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- focused schema, collector, and page tests to be added with AAE-002–AAE-005

The current GitHub connector can create repository files and pull requests; a local checkout and shell runner are unavailable in this session. The PR's Actions runs are the executable validation evidence. Queued/running remains pending.
