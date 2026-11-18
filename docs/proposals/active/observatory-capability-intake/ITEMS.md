# ITEMS — observatory-capability-intake

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| OCO-001 | P1 | proposed | Freeze the existing-system ownership map and no-duplication boundaries. | Observatory, research-seed intake, CEEL, CRG, refTemplates and proposal lifecycle have explicit canonical responsibilities; no second registry, scheduler, collector or experiment ledger is introduced. |
| OCO-002 | P1 | queued | Define a deterministic Observatory-signal to research-seed handoff using existing repository snapshots and issue intake. | Owned/starred/watching/fork provenance and source revision are retained; duplicate identities merge without losing provenance; candidate classifications are marked inference; no adoption action is triggered by a star/fork alone. |
| OCO-003 | P1 | queued | Map research seeds and Observatory deltas into CEEL capability nodes and verified/candidate relationships. | Stable capability IDs, canonical upstream identity, observed revision/time, evidence references, internal consumers, owner, freshness and lifecycle state are present; graph validator and fixtures reject duplicate IDs, dangling edges and unsupported states. |
| OCO-004 | P1 | queued | Specify refTemplates disposition and promotion routing. | Each candidate receives one explicit disposition: reject, defer, watch, pattern-only, metadata reference under 15_Research_Repo_Templates/, or custom-fork proposal for smods/; SOURCE.txt, source map, license/provenance, pin and dual-gate rules are enforced; no automatic gitlink creation. |
| OCO-005 | P1 | blocked | Evaluate the operator-named Time_forkinto candidate against a confirmed canonical source. | Canonical URL/repository access is established; exact upstream/default branch/revision/license and maintenance/security posture are evidenced; capability contract and internal consumers are identified; alternatives and disposition are recorded. No evaluation claim before source access. |
| OCO-006 | P1 | queued | Reuse existing GitHub-native events and add regression/quality evidence for the handoff. | Observatory snapshot changes, research issue intake, release/PR changes and workflow completion are handled by existing event paths; idempotency and stale-event fixtures pass; no new scheduled poller; missed-event recovery uses existing bounded reconciliation. |
| OCO-007 | P2 | queued | Define longitudinal opportunity-discovery quality measures. | Report discovery-to-classification time, provenance completeness, duplicate/alias rate, mapped-consumer rate, validated capability yield, false-positive rate, stale-source rate and time/cost to validated adoption; unknown populations are not described as exhaustive. |

## Validation

- python3 scripts/proposals/validate_registry.py
- python3 scripts/integrations/validate_capability_graph.py
- python3 scripts/integrations/validate_portfolio.py
- python3 -m pytest tests/test_context_relationship_*.py -q
- Existing Repository Observatory and research-intake tests
- Existing refTemplates inventory and smods-scoped submodule-integrity checks
- python3 scripts/ci/repo_gate.py
- python3 scripts/ci/termux_smoke.py

Validation must run on the same immutable PR head. Queued/running checks are not passes. No local Termux device execution is claimed by this proposal-authoring session.
