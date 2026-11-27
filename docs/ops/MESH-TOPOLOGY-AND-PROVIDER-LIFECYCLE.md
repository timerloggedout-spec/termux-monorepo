# Mesh topology and provider lifecycle

**Lifecycle authorities:** `docs/ops/DEVOPS-REGISTER.md` §4A and `docs/DEPLOYMENT-LANES.md`; this document is a read-only synthesis.  
**As of:** 2026-11-24 (branch census captured 2026-11-23)  
**Scope:** compute mesh, deployment mesh, provider/function lanes, VM nodes, and branch reconciliation.

## Executive ruling

The repository has several related mesh architectures. Provider lifecycle remains with the existing deployment and operations authorities; historical records remain searchable and retired providers stay excluded from execution admission.

Fly.io and Koyeb are **RETIRED** for this mesh. Their deployment workflows emit retirement receipts and run through manual dispatch only. Their old quota records, deployment history, and commits remain as provenance.

## Architecture/version inventory

| Plane | Canonical artifact | Version / vintage | Actual responsibility |
|---|---|---|---|
| Integration Mesh | `docs/ops/INTEGRATION-MESH-MATRIX.md` | Ninth census pass, 2026-11-02; snapshot document, no schema version | Connector, GitHub App, workflow, credential-name, and integration reach |
| Integration Intelligence portfolio | `docs/integrations/registry.json` | Schema 1.0.0, updated 2026-11-11 | 36 catalog records: 32 planned adapters, 2 implemented adapters, 1 native repository integration, 1 not applicable |
| Inference quota mesh | `ops/quota/registry.json` and `docs/ops/INTEGRATION-MESH-MATRIX.md` | 27 provider quota families in the 2026-11-02 census | Model inference endpoints/quota families; separate from app hosting and VM compute |
| Compute Mesh | `ops/mesh/REQUESTS-SCHEMA.md` | Request protocol v1, 2026-11-18 | Append-only request and completion records; allowlisted VM/Actions work |
| Compute Mesh topology | `docs/architecture/flows/compute-mesh.md` | Living map, readback 2026-11-23 | Cross-repo request, VM ledger, DoE result, and consumer edges |
| VM node manifest | `ops/vm-backup/hark-sandbox-node.json` | `resiliency-node/v1` | Hark node identity, capacity, allowlist, and request transport |
| VM allocation | `ops/compute/ALLOCATION.md` | Allocation record dated 2026-11-18 | Muse/Hark workload placement and compute capacity |
| Deployment admission | `scripts/ci/deployment_admission.py` on PR #4020 | `deployment-admission-input/v1` and `deployment-admission-decision/v1` | Offline quota admission and verified-alternate policy; PR remains open and live failover remains unverified |
| Receiver Mesh | `receiver-mesh-prototype-20261029` lineage | Prototype | Event-receiver experiment; separate from compute request routing |
| BRR | Private `compute-exports/brr/2026-11-17/registry.json` | 2026-11-17 registry snapshot | Read-only branch reconciliation, branch class, ahead/behind, and feature discovery |

The mesh request protocol, VM node manifest, deployment admission contract, and BRR registry describe different objects. Treat their version numbers as separate namespaces.

## VM count and contract count

The compute allocation names **two VM nodes**:

- **Muse VM:** Temporal, staging index, registry cadence, CLF lab replication, and other assigned batch work.
- **Hark VM:** request drain, DoE execution, exports, evaluation, and workspace backup.

The Hark node manifest uses `resiliency-node/v1`; the request protocol uses `mesh request schema v1`; the Hark workspace backup registry is separately versioned. These are contract versions for the two identified VM nodes.

GitHub branch-name search on 2026-11-23 returned **27 mesh-named branches** and **19 VM-named branches**. These counts include historical, experimental and competing work branches; deployed-system counts require runtime evidence.

## Provider lifecycle

The existing deployment-lane SSOT and DevOps register are authoritative for deployment identity and operational status. The infrastructure CMDB design governs field-level reconciliation. Current classifications:

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

The source records separate provider capability, account connection, quota record, deployed resource, and successful workload execution.

## Are function providers replacing VMs?

Functions are a separate workload class alongside the VM plane.

- **Cloudflare Workers:** deployed edge-function execution is evidenced. D1 supplies a separate database capability.
- **Vercel Functions:** platform capability belongs to the active Vercel application-hosting lane; a distinct deployed function inventory requires evidence.
- **Supabase Edge Functions:** quota capability is registered; deployed function inventory remains unverified.
- **Leapcell and Appwrite:** function/serverless candidates in PR #5807; candidate status remains separate from production integration.
- **Deno Deploy, AWS Lambda, Azure Functions, and Cloud Run:** candidate or quota-research surfaces; account eligibility and deployed workloads require their own evidence.

Use VMs for persistent or checkpointed workloads that need a host-level execution environment. Use functions for bounded request/event work with compatible runtime, state, duration, and network constraints. Use databases as state services; they do not become compute nodes by virtue of appearing in the mesh.

## BRR relationship discovery and related work

BRR is the read-only discovery and reconciliation layer for branch work. The accessible GitHub evidence identifies these related workstreams:

| Work | Relationship |
|---|---|
| [PR #5807](https://github.com/timerloggedout-spec/termux-monorepo/pull/5807) | Current utilization extension; Cloudflare Workers/D1 inventory, Render path, and function candidates |
| [PR #4020](https://github.com/timerloggedout-spec/termux-monorepo/pull/4020) and [PR #4083](https://github.com/timerloggedout-spec/termux-monorepo/pull/4083) | Deployment admission evaluator and fresh-master refresh; offline policy scaffold, no live failover |
| [PR #1626](https://github.com/timerloggedout-spec/termux-monorepo/pull/1626) | Initial source-backed mesh provider evidence |
| [PR #3908](https://github.com/timerloggedout-spec/termux-monorepo/pull/3908) | Historical Fly/Koyeb deploy-plane census |
| [PR #3628](https://github.com/timerloggedout-spec/termux-monorepo/pull/3628) | Historical Fly Hindsight model mapping |
| [PR #2663](https://github.com/timerloggedout-spec/termux-monorepo/pull/2663) | Historical Fly/Koyeb configured-instance mapping |
| [PR #5630](https://github.com/timerloggedout-spec/termux-monorepo/pull/5630) and [issue #5552](https://github.com/timerloggedout-spec/termux-monorepo/issues/5552) | BRR regression hardening and outstanding full-cycle/consumer acceptance |
| [Issue #5640](https://github.com/timerloggedout-spec/termux-monorepo/issues/5640) | Explicit join requirement: BRR delta + commits export + regression suite + existing context-relationship graph; no new page or parallel graph surface |

The prior implementation branch `fix/mesh-provider-lifecycle-20261123` compared at 63 commits ahead / 31 behind and carried unrelated quota/allocation rewrites; the extended-utilization branch `docs/mesh-extended-utilization-20261123-v2` compared at 20 ahead / 965 behind. This PR extracts the lifecycle slice onto a clean master-based branch instead of promoting either divergent branch wholesale. The current PR branch has since fallen behind generated master feed commits; those changes are outside its 19-file source scope.

The full 4,103-branch private BRR registry and its append-only cycle artifact remain outside this session's access. The related-work list above is a bounded GitHub evidence search; the private BRR cycle remains pending.

## Regression controls

1. Provider lifecycle remains in the existing deployment-lane SSOT and DevOps register; the infrastructure CMDB design defines the reconciliation model.
2. Provider workflow discovery preserves lifecycle state; retired workflows carry a `RETIRED` name and manual-dispatch-only trigger.
3. `scripts/ci/validate_mesh_provider_lifecycle.py` checks the existing status authorities, retired workflow triggers, and retired provider operations.
4. Quota records and historical PRs remain available as provenance; execution eligibility follows the current deployment and operations records.
5. Provider promotion requires exact workload identity, source SHA, health, protocol, state dependency, quota evidence, and independent failure-domain evidence.

Run the focused contract:

```bash
python3 scripts/ci/validate_mesh_provider_lifecycle.py
python3 -m unittest tests.test_mesh_provider_lifecycle -v
```
