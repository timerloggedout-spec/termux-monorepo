# Plan — mesh provider lifecycle reconciliation

**Proposal:** `mesh-provider-lifecycle`  
**Branch:** `fix/mesh-provider-lifecycle-master-20261124`  
**Base:** `master` at `b8487426e3a1b9e3bb3e64a2b55ed0808801f199`

## Task 1 — Establish lifecycle authority
Reuse `docs/DEPLOYMENT-LANES.md`, `docs/ops/DEVOPS-REGISTER.md`, and the dated `docs/ops/INTEGRATION-MESH-MATRIX.md` correction. Preserve the infrastructure CMDB/IDRR authority model.

## Task 2 — Retire provider execution paths
Replace two Fly and one Koyeb workflow with manual-dispatch retirement receipts. Block stale Fly/Koyeb Hindsight URLs before telemetry network I/O. Preserve history and quota records.

## Task 3 — Regression protection
Add an offline lifecycle validator and focused tests for status authorities, workflow triggers, forbidden provider operations, and endpoint admission.

## Task 4 — Reconcile topology
Document separate Integration, Compute, Deployment, Function, Database, Receiver, and BRR planes. Record two identified VM nodes and their independent contract versions. Label branch counts as branch counts, not runtime counts.

## Task 5 — Verify
Run focused validator/tests, repo gate, Termux smoke, and exact-head CI. Preserve private BRR full-cycle and consumer acceptance as a separately blocked item.
