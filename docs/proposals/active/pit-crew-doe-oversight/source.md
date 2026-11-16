# Source and scope

User-directed request (2026-11-16): propose the similar-concept mappings, Pit Crew Chief and diagrams, with a high-detail whole-architecture report from architecture through DoE tournaments; clarify that DoE is Oversight; account for concurrent `*brain` architecture development; implement the bounded repository documentation.

Repository evidence inspected before drafting:
- `CLAUDE.md` and proposal lifecycle rules.
- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md`.
- `docs/ops/AGENT-TEAM-ORCHESTRATION.md`.
- `docs/ops/AGENT-TEAM-ROSTER.md`.
- `docs/ops/AGENT-TEAM-DEVELOPMENT-LANES.md`.
- `docs/ops/DOE-FAMILY.md`, `MVT-DOE-ATES-SEPARATION.md`, `ATES-ORCHESTRATOR-DOE-MVT.md`.
- `docs/ops/corpus/EXPERIMENT.schema.json` and `docs/ops/MANAGER-TOURNAMENT.schema.json`.
- Ballet RFP and DoE proposal on `feat/ballet-coordinator-doe-rfp` (PR #5529; issue #5528).
- Brain architecture subsystem map on `feat/root-brain-rust-core-final` and Brain RFP issue #5501 / PR #5503.

Scope is architecture, documentation, diagram and contract mapping only. This change does not add runtime dispatch, change provider routing, alter DoE scoring, create a new schema/ledger/registry/scheduler, grant permissions, merge concurrent work, or promote a production policy.
