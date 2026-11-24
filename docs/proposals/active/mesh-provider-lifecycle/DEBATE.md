# Decision record — mesh-provider-lifecycle

## 2026-11-23 — Operator directive

**Decision:** Retire Fly.io and Koyeb from mesh execution and deployment selection. Preserve their historical records, quota evidence, configuration history, and commit lineage.

**Architecture:** Reuse `docs/DEPLOYMENT-LANES.md`, `docs/ops/DEVOPS-REGISTER.md`, and `docs/ops/INTEGRATION-MESH-MATRIX.md` as the existing lifecycle and inventory authorities. Use the Infrastructure CMDB/IDRR design for source reconciliation. Keep the topology index as a read-only synthesis.

**Execution boundary:** Replace Fly/Koyeb deployment and configuration workflows with manual-dispatch retirement receipts. Keep provider resource teardown, billing changes, and credential rotation under human authorization.

**Workload distinction:** Cloudflare Workers, Vercel Functions, and Supabase Edge Functions are function-runtime capabilities. VM nodes remain Muse VM and Hark VM. Database services remain Neon and Supabase; their presence in the mesh does not turn them into compute nodes.

**Open evidence:** BRR's private 4,103-branch registry cycle and Observatory/Provenance consumer read remain pending under issue #5552.
