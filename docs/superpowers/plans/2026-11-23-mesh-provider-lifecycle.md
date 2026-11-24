# Plan — mesh provider lifecycle reconciliation

**Proposal:** `mesh-provider-lifecycle`  
**Branch:** `fix/mesh-provider-lifecycle-20261123`  
**Base:** `master` at `0dec004144f4957c54d6c15f25bd3c12b38def74`

## Task 1 — Establish the lifecycle authority

- Reuse `docs/DEPLOYMENT-LANES.md` for deployment identity and hosting surfaces.
- Reuse `docs/ops/DEVOPS-REGISTER.md` for operational provider status.
- Preserve `docs/ops/INTEGRATION-MESH-MATRIX.md` as a dated integration census.
- Link the topology synthesis to the Infrastructure CMDB/IDRR authority matrix.
- Keep quota metadata and historical PRs as provenance.

## Task 2 — Retire Fly.io and Koyeb workflow execution

- Replace `deploy-hindsight.yml`, `fly-hindsight-config.yml`, and `koyeb-hindsight-deploy.yml` with dispatch-only retirement receipts.
- Remove provider API calls, secret references, restarts, deploys, and Koyeb's former push trigger.
- Preserve workflow paths and historical Git evidence.

## Task 3 — Add regression protection

- Add `scripts/ci/validate_mesh_provider_lifecycle.py`.
- Add `tests/test_mesh_provider_lifecycle.py`.
- Run the focused validator and test module.
- Wire the focused suite into the existing repo-gate workflow.

## Task 4 — Reconcile topology and workload classes

- Document distinct Integration, Compute, Deployment Resiliency, Receiver, and BRR planes.
- Record the two identified VM nodes and their contract versions.
- Separate deployed function execution, function capability, and function candidates.
- Link related PRs and branches with explicit evidence limits.

## Task 5 — Verify and promote

- Run focused tests, `repo_gate.py`, and `termux_smoke.py`.
- Inspect the PR checks on the exact head SHA.
- Re-fetch workflow files and deployment/operations status.
- Preserve BRR's private full-cycle acceptance as a separate blocked item.
