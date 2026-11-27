# ITEMS — mesh-provider-lifecycle

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| MPL-001 | P1 | executing | Retire Fly.io and Koyeb deployment/configuration workflow operations. | Three workflows publish retirement receipts through manual dispatch; provider mutation operations are absent; historical evidence remains preserved. |
| MPL-002 | P1 | executing | Reconcile deployment, integration, provider, function, VM, and mesh-version records. | Deployment lanes, DevOps register, integration matrix, and topology index agree on lifecycle and evidence classes; existing authorities remain canonical. |
| MPL-003 | P1 | executing | Add an offline regression validator and focused tests. | Validator checks lifecycle source rows, retired workflow labels, dispatch-only triggers, and provider-operation markers; focused CI suite passes. |
| MPL-004 | P1 | blocked | Join BRR branch-range reconciliation, commit exports, differential regression verdicts, and the existing context-relationship graph. | Consume the private 4,103-branch registry and commit export; map branch → commits → PR/issues/comments → feature/proposal; publish append-only cycle deltas and per-feature green/regressed/untestable verdicts; demonstrate an Observatory/Provenance consumer read with SHA and run attribution. Reuse #5523/#5552/#5640 and the existing graph; create no parallel registry or graph. Private registry access and consumer receipt remain pending. |

## Validation

- `python3 scripts/ci/validate_mesh_provider_lifecycle.py`
- `python3 -m unittest tests.test_mesh_provider_lifecycle -v`
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
