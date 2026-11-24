# Mesh topology and provider lifecycle

**Canonical lifecycle contract:** `ops/mesh/provider-lifecycle.json` · `mesh.provider-lifecycle/v1`  
**As of:** 2026-11-23  
**Scope:** compute mesh, deployment mesh, provider/function lanes, VM nodes, and branch reconciliation.

## Executive ruling

The repository has several related mesh architectures, not 20+ deployed mesh versions. Provider lifecycle is now centralized in one versioned registry. Historical records remain searchable; retired providers stay excluded from execution admission.

Fly.io and Koyeb are **RETIRED** for this mesh. Their deployment workflows emit retirement receipts and run through manual dispatch only. Their old quota records, deployment history, and commits remain as provenance.

## Architecture/version inventory

| Plane | Canonical artifact | Version / vintage | Actual responsibility |
|---|---|---|---|
| Integration Mesh | `docs/ops/INTEGRATION-MESH-MATRIX.md` | Ninth census pass, 2026-11-02; snapshot document, no schema version | Connector, GitHub App, workflow, credential-name, and integration reach |
| Compute Mesh | `ops/mesh/REQUESTS-SCHEMA.md` | Request protocol v1, 2026-11-18 | Append-only request and completion records; allowlisted VM/Actions work |
| Compute Mesh topology | `docs/architecture/flows/compute-mesh.md` | Living map, readback 2026-11-23 | Cross-repo request, VM ledger, DoE result, and consumer edges |
| VM node manifest | `ops/vm-backup/hark-sandbox-node.json` | `resiliency-node/v1` | Hark node identity, capacity, allowlist, and request transport |
| VM allocation | `ops/compute/ALLOCATION.md` | Allocation record dated 2026-11-18 | Muse/Hark workload placement and compute capacity |
| Deployment admission | `scripts/ci/deployment_admission.py` on PR #4020 | `deployment-admission-input/v1` and `deployment-admission-decision/v1` | Offline quota admission and verified-alternate policy; PR remains open and does not prove live failover |
| Receiver Mesh | `receiver-mesh-prototype-20261029` lineage | Prototype | Event-receiver experiment; separate from compute request routing |
| BRR | Private `compute-exports/brr/2026-11-17/registry.json` | 2026-11-17 registry snapshot | Read-only branch reconciliation, branch class, ahead/behind, and feature discovery |

The mesh request protocol, VM node manifest, deployment admission contract, and BRR registry describe different objects. Their version numbers are not interchangeable.

## VM count and contract count

The compute allocation names **two VM nodes**:

- **Muse VM:** Temporal, staging index, registry cadence, CLF lab replication, and other assigned batch work.
- **Hark VM:** request drain, DoE execution, exports, evaluation, and workspace backup.

The Hark node manifest uses `resiliency-node/v1`; the request protocol uses `mesh request schema v1`; the Hark workspace backup registry is separately versioned. These are contract versions for two nodes, not additional VM instances.

GitHub branch-name search on 2026-11-23 returned **27 mesh-named branches** and **19 VM-named branches**. These counts include historical, experimental, and competing work branches. They do not establish 27 live meshes or 19 deployed VMs.

## Provider lifecycle

The machine-readable registry is authoritative for lifecycle admission. Current classifications:

| Provider | Product/workload class | Lifecycle | Evidence interpretation |
|---|---|---|---|
| GitHub Actions | CI/control plane | Active | Repository execution substrate |
| Vercel | Application hosting; serverless capability | Active, capacity-constrained | Primary MCP/demo hosting |
| Cloudflare | Workers edge runtime + D1 | Active, partial | 2 deployed Workers and 3 D1 databases reported 2026-11-23; Queues 0, R2 pending |
| Neon | PostgreSQL | Active | Database lane with live writes |
| Supabase | Backend/database; Edge Functions capability | Integrated, partial | One management-API project; deployed Edge Function inventory remains unverified |
| Render | Image-backed container service | Repository-wired, health pending | GHCR image workflow exists; provider service identity and health require confirmation |
| GitHub Pages | Static publication | Configured, publication unverified | Static-only lane |
| Fly.io | Historical Hindsight app/VM hosting | **Retired** | Trial-ended/card blocker; billing evidence remains historical |
| Koyeb | Historical Hindsight app/container hosting | **Retired** | Missing deploy credential; last workflow runs in September 2026 |

The registry separates provider capability from account connection, quota record, deployed resource, and successful workload execution.

## Are function providers replacing VMs?

Functions are a separate workload class, not a replacement for the VM plane.

- **Cloudflare Workers:** deployed edge-function execution is evidenced. D1 supplies a separate database capability.
- **Vercel Functions:** platform capability belongs to the active Vercel application-hosting lane; a distinct deployed function inventory is not established here.
- **Supabase Edge Functions:** quota capability is registered; deployed function inventory remains unverified.
- **Leapcell and Appwrite:** function/serverless candidates in PR #5807; candidate status is not production integration.
- **Deno Deploy, AWS Lambda, Azure Functions, and Cloud Run:** candidate or quota-research surfaces; account eligibility and deployed workloads require their own evidence.

Use VMs for persistent or checkpointed workloads that need a host-level execution environment. Use functions for bounded request/event work with compatible runtime, state, duration, and network constraints. Use databases as state services; they do not become compute nodes by virtue of appearing in the mesh.

## BRR relationship discovery and related work

BRR is the read-only discovery and reconciliation layer for branch work. The accessible GitHub evidence identifies these related workstreams:

| Work | Relationship |
|---|---|
| [PR #5807](https://github.com/timerloggedout-spec/termux-monorepo/pull/5807) | Current utilization extension; Cloudflare Workers/D1 inventory, Render path, and function candidates |
| [PR #4020](https://github.com/timerloggedout-spec/termux-monorepo/pull/4020) | Deployment admission evaluator; offline policy scaffold, no live failover |
| [PR #1626](https://github.com/timerloggedout-spec/termux-monorepo/pull/1626) | Initial source-backed mesh provider evidence |
| [PR #3908](https://github.com/timerloggedout-spec/termux-monorepo/pull/3908) | Historical Fly/Koyeb deploy-plane census |
| [PR #3628](https://github.com/timerloggedout-spec/termux-monorepo/pull/3628) | Historical Fly Hindsight model mapping |
| [PR #2663](https://github.com/timerloggedout-spec/termux-monorepo/pull/2663) | Historical Fly/Koyeb configured-instance mapping |
| [PR #5630](https://github.com/timerloggedout-spec/termux-monorepo/pull/5630) and [issue #5552](https://github.com/timerloggedout-spec/termux-monorepo/issues/5552) | BRR regression hardening and outstanding full-cycle/consumer acceptance |

The full 4,103-branch private BRR registry and its append-only cycle artifact were unavailable to this session. The related-work list above is a bounded GitHub evidence search, not a claim that the private BRR cycle has completed.

## Regression controls

1. Provider lifecycle lives in `ops/mesh/provider-lifecycle.json`.
2. Provider workflow discovery preserves lifecycle state; retired workflows carry a `RETIRED` name and manual-dispatch-only trigger.
3. `scripts/ci/validate_mesh_provider_lifecycle.py` checks registry uniqueness, lifecycle eligibility, retired workflow triggers, and retired provider operations.
4. Quota records and historical PRs remain available as provenance; they do not grant execution eligibility.
5. Provider promotion requires exact workload identity, source SHA, health, protocol, state dependency, quota evidence, and independent failure-domain evidence.

Run the focused contract:

```bash
python3 scripts/ci/validate_mesh_provider_lifecycle.py
python3 -m unittest tests.test_mesh_provider_lifecycle -v
```
