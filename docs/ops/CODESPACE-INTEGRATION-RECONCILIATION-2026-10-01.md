# Codespace + Integration Surface Reconciliation

**Recon date:** 2026-10-01  
**Issue:** #976  
**Source of truth:** current `master`  
**Purpose:** recover historical Codespace/environment lineage and reconcile adjacent Bifrost, Gravitee, Temporal, and Hindsight lanes without resurrecting stale carriers.

## Current environment spine

Current `master` contains the production devcontainer role surfaces:

| Surface | Path | Disposition |
|---|---|---|
| BASH/Ops Agent | `.devcontainer/devcontainer.json` | **LIVE** |
| Docs / Mintlify | `.devcontainer/docs-lane/devcontainer.json` | **LIVE** |
| PR-Triage / Governance | `.devcontainer/governance-lane/devcontainer.json` | **LIVE** |
| General Dev/Build | `.devcontainer/general-dev/devcontainer.json` | **LIVE** |
| Oracle | `.devcontainer/oracle/devcontainer.json` | **LIVE** |

Historical branches remain provenance. They are not additional production configurations.

## Recovered Codespace identity ledger

Recovered identifiers establish identity, not current lifecycle. Reported development workspaces are protected until explicitly reconciled.

| Friendly name | Codespace identifier | Classification | Action |
|---|---|---|---|
| glorious capybara | `glorious-capybara-wrq7vrqj7xqjh995p` | **RECOVERED / DEVELOPMENT CANDIDATE** | Preserve; reconcile before cleanup |
| agent-bifrost-006 | `agent-bifrost-006-5g7qvg7pqjggh4jqv` | **RECOVERED / BIFROST EVIDENCE** | Preserve; link to BIFROST-006 |
| list-only-probe | `list-only-probe-v6jvp6j7v75xfxxv9` | **RECOVERED / PROBE** | Preserve as diagnostic lineage |
| congenial space doodle | `congenial-space-doodle-5g7q7pqpw92q7v` | **RECOVERED / UNKNOWN** | Inventory first; no deletion assumption |
| hindsight-1552 | `hindsight-1552-4jp7qjp975j73q9qj` | **RECOVERED / HINDSIGHT DEVELOPMENT** | Protect active work; reconcile against current lane |

Known lifecycle evidence:

- `agent-bifrost-006-5g7qvg7pqjggh4jqv`: Provisioning → Available observed 2026-09-23.
- `glorious-capybara-wrq7vrqj7xqjh995p`: Shutdown after idle timeout; not evidence of deletion.
- Lifecycle semantics: `Provisioning → Available → Shutdown → Deleted`.
- Missing inventory is **UNKNOWN**, not Deleted. The connected GitHub surface does not expose an authoritative Codespaces inventory endpoint.

## Carrier delta audit

All comparisons below are against the **current** `master`, not the historical merge base. A stale carrier is not merged wholesale.

| Carrier | Ahead | Behind | Unique surface | Disposition |
|---|---:|---:|---|---|
| `codespaces-multi-lane-agent-roles` | 4 | 980 | 5 devcontainers + oracle watch + docs | **SUPERSEDED / PROVENANCE** |
| `docs/proposals/codespaces-enablement` | 10 | 902 | enablement manifest/checklist/registry | **RE-EXTRACT** |
| `feat/codespace-agent-devcontainer` | 2 | 1006 | root devcontainer + setup | **RE-EXTRACT** |
| `feat/codespace-production-lane` | 2 | 1005 | root devcontainer + lane docs | **RE-EXTRACT** |
| `gaps-opps/add-devcontainer-codespaces` | 1 | 1041 | root devcontainer | **SUPERSEDED** |
| `ops/codespace-create-secret-chain` | 0 | 689 | none | **LANDED / STALE** |
| `ops/codespace-create-use-archwiz-token` | 3 | 689 | Codespace create workflow | **LANDED / STALE CARRIER** |
| `ops/codespace-create-workflow-dispatch` | 1 | 691 | create workflow + lane docs | **LANDED / STALE CARRIER** |
| `ops/codespace-start-existing` | 2 | 683 | start-existing workflow | **RE-EXTRACT IF STILL REQUIRED** |
| `docs/codespace-bifrost-006-run` | 1 | 857 | BIFROST runbook/evidence docs | **LANDED / PROVENANCE** |
| `ops/bifrost-006-evidence-and-codespace-ssot` | 2 | 686 | smoke workflow + credentials/evidence SSOT | **LANDED / PROVENANCE** |
| `docs/bifrost-006-benchmark-runbook` | 1 | 914 | benchmark smoke/runbook | **LANDED / PROVENANCE** |
| `docs/bifrost-gateway-recon-reconcile` | 3 | 922 | gateway recon + provider/catalog deltas | **RE-EXTRACT SELECTIVELY** |
| `hindsight-wire` | 24 | 1838 | Hindsight client + agent/CI/session surfaces | **PROVENANCE / RE-EXTRACT SELECTIVELY** |
| `fix/hindsight-tool-envelope` | 0 | 214 | none | **LANDED / STALE** |
| `lane1/deadcode-hindsight-finish` | 1 | 246 | `deepcli/deepagent.py` cleanup | **RE-EXTRACT ONE FILE** |
| `feat/gravitee-repository-observatory` | 5 | 790 | research seed + observatory changes | **RETAIN SEED / RE-EXTRACT** |
| `bolt-temporal-lag-index-optimization-7092498872592714131` | 1 | 1083 | lag/index scripts + bolt note | **RE-EXTRACT AFTER VALIDATION** |
| `feat/temporal-langsmith-adapter` | 5 | 564 | Temporal self-host/adapter substrate | **LANDED / PROVENANCE** |
| `ops/fa-ade-claude-temporal-smoke` | 4 | 558 | Temporal smoke workflow/docs | **LANDED / PROVENANCE** |
| `ops/fa-ade-claude-temporal-smoke-e2757801` | 0 | 557 | none | **LANDED / STALE** |
| `ops/temporal-langsmith-matrix-residual-20261001` | 3 | 128 | residual matrix/docs | **LANDED / PROVENANCE** |

### Important delta findings

1. The historical Codespaces role branch contains five role-oriented devcontainers, but the same role surfaces are already present on current `master`; it is **not** a merge candidate.
2. Codespace creation/start carriers contain historical workflow variants. They should be treated as implementation archaeology and only re-extracted where current behavior still lacks coverage.
3. Bifrost has landed evidence/runbook/credential surfaces; the remaining work is evidence quality and selective reconciliation, not wholesale branch restoration.
4. Hindsight's functional lineage is largely landed. The one-file cleanup carrier remains a surgical re-extraction candidate.
5. Gravitee remains an adjacent research-observatory seed. Its unique five-file delta is useful for inspection but is too stale for wholesale integration.
6. Temporal is established. The residual matrix branch is recent enough to preserve as provenance, but the production substrate should continue to follow current `master`.
7. The Temporal lag/index optimization carrier is a distinct unique delta and should be validated before any re-rooting; no claim that it is required is made here.

## Consolidated architecture

```text
CURRENT MASTER
     |
     +-- Codespaces = environment
     +-- Docker/CI = execution substrate
     +-- OTEL/ATES/JSONL = evidence boundary
     |
     +-- Integration Graph
          +-- Bifrost  = gateway/provider evaluation
          +-- Temporal = durable runtime/workflows
          +-- Hindsight = agent memory
          +-- Gravitee = adjacent research-observatory seed
```

**Invariant:** environment, execution, evidence, and integration lanes remain separate authorities.

## Recovery / consolidation invariants

- `RECON → RE-ROOT → VALIDATE → WATCH → RECORD`.
- Never infer Deleted from an absent Codespace record.
- Never delete/recreate/repurpose a recovered workspace solely because the connector cannot inventory it.
- Preserve active/developing work until its current state is explicitly reconciled.
- Before branch cleanup, compare against current `master` and classify the unique delta.
- Prefer surgical re-extraction over stale branch merges.
- Every recovered surface should record source SHA/ref, observed_at, lifecycle/disposition, and evidence confidence.
- `list-only-probe` remains diagnostic unless promoted by evidence.

## Next operational gates

- [x] Current-master carrier comparison completed.
- [x] Recovered Codespace identifiers normalized into the ledger.
- [x] Bifrost/Temporal/Hindsight/Gravitee carrier boundaries identified.
- [ ] Re-root validated unique deltas from Gravitee, Hindsight cleanup, Codespace lifecycle, and Temporal lag/index work where still valuable.
- [ ] Add provider-backed Codespace inventory when an authorized API surface is available.
- [ ] Close/supersede stale carriers only after unique-delta disposition is recorded.

**Policy:** no stale-space resurrection by assumption; useful history is recovered by evidence-backed re-rooting.
