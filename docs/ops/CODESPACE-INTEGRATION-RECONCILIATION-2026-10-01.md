# Codespace + Integration Surface Reconciliation

**Recon date:** 2026-10-01  
**Issue:** #976  
**Source of truth:** current `master`  
**Purpose:** recover historical Codespace/environment lineage and reconcile adjacent Bifrost, Gravitee, Temporal, and Hindsight lanes without resurrecting stale carriers.

## 1. Current environment spine

Current `master` contains these devcontainer surfaces:

| Surface | Path | Role | Disposition |
|---|---|---|---|
| BASH/Ops Agent | `.devcontainer/devcontainer.json` | Admin / production operator | **LIVE** |
| Docs / Mintlify | `.devcontainer/docs-lane/devcontainer.json` | Discovery / docs | **LIVE** |
| PR-Triage / Governance | `.devcontainer/governance-lane/devcontainer.json` | Governance | **LIVE** |
| General Dev/Build | `.devcontainer/general-dev/devcontainer.json` | Collaborator / build | **LIVE** |
| Oracle | `.devcontainer/oracle/devcontainer.json` | Evaluator / watch | **LIVE** |

The historical `codespaces-multi-lane-agent-roles` branch is retained as provenance. It is not a second production configuration to resurrect.

The repository's role-lane documentation should be treated as descriptive history where it still says the multi-lane surface is merely "live on" the historical branch; the current tree is the authoritative implementation surface.

## 2. Codespace lifecycle evidence

Known provider-observed records:

| Codespace | Observed state | Evidence date | Interpretation |
|---|---|---|---|
| `agent-bifrost-006-5g7qvg7pqjggh4jqv` | Provisioning → Available | 2026-09-23 | Real Codespace creation evidence for BIFROST-006 |
| `glorious-capybara-wrq7vrqj7xqjh995p` | Shutdown | ~2026-09-15 | Idle stop; disk retained; **not** evidence of deletion or limit rotation |

Lifecycle semantics remain:

`Provisioning → Available → Shutdown → Deleted`

A missing Codespace record is **UNKNOWN**, not Deleted. Current GitHub connector capabilities available to this reconciliation do not expose a Codespaces inventory endpoint, so this document intentionally does not invent a live/deleted inventory.



## 2A. Recovered Codespace name ledger

**Source:** user-provided Codespace inventory recovered during the 2026-10-01 continuation pass.
**Important:** names below are confirmed as recovered identifiers, but their current provider lifecycle state is not independently observable through the connected GitHub surface. Where development is reported, preserve the workspace and treat it as **ACTIVE/PROTECTED** until explicitly reconciled.

| Friendly name | Codespace identifier | Recovery classification | Action |
|---|---|---|---|
| glorious capybara | `glorious-capybara-wrq7vrqj7xqjh995p` | **RECOVERED / DEVELOPMENT CANDIDATE** | Preserve; reconcile state before cleanup |
| agent-bifrost-006 | `agent-bifrost-006-5g7qvg7pqjggh4jqv` | **RECOVERED / BIFROST EVIDENCE** | Preserve; link to BIFROST-006 evidence |
| list-only-probe | `list-only-probe-v6jvp6j7v75xfxxv9` | **RECOVERED / PROBE** | Preserve as probe lineage; do not promote to production |
| congenial space doodle | `congenial-space-doodle-5g7qvg7pqpw92q7v` | **RECOVERED / UNKNOWN** | Inventory first; no deletion assumption |
| hindsight-1552 | `hindsight-1552-4jp7qjp975j73q9qj` | **RECOVERED / HINDSIGHT DEVELOPMENT** | Protect active work; reconcile against current Hindsight lane |

### Recovery invariants

- A recovered identifier establishes **identity**, not current lifecycle.
- A user-reported "being developed" workspace is treated as **PROTECTED** for consolidation until explicitly reconciled.
- No workspace is deleted, recreated, or repurposed during this recovery pass merely because it is absent from the connector inventory.
- `list-only-probe` remains diagnostic/probe lineage unless current evidence promotes it.
- `agent-bifrost-006` and `hindsight-1552` are linked to their respective integration lanes rather than treated as generic disposable environments.
- The next operational pass should capture: `codespace_id`, friendly name, repository/ref, current lifecycle, last observed time, devcontainer/config, uncommitted-work indicator, branch/SHA, owner/agent lane, and disposition.



## 2B. Branch-lineage census

The repository currently exposes these relevant historical/current branches. Branch existence is **provenance evidence**, not proof that a Codespace is live or that the branch should be merged.

### Codespace / environment carriers

- `codespaces-multi-lane-agent-roles` — historical multi-lane role architecture
- `docs/proposals/codespaces-enablement` — enablement proposal lineage
- `feat/codespace-agent-devcontainer` — agent devcontainer implementation lineage
- `feat/codespace-production-lane` — production-lane implementation lineage
- `gaps-opps/add-devcontainer-codespaces` — gap/opportunity lineage
- `ops/codespace-create-secret-chain` — creation credential chain lineage
- `ops/codespace-create-use-archwiz-token` — creation/auth lineage
- `ops/codespace-create-workflow-dispatch` — dispatch creation lineage
- `ops/codespace-start-existing` — start-existing lifecycle lineage
- `docs/codespace-bifrost-006-run` — BIFROST-006 Codespace execution lineage
- `ops/bifrost-006-evidence-and-codespace-ssot` — BIFROST Codespace evidence/SSOT lineage

### Bifrost

- `docs/bifrost-006-benchmark-runbook`
- `docs/bifrost-gateway-recon-reconcile`
- `docs/codespace-bifrost-006-run`
- `ops/bifrost-006-evidence-and-codespace-ssot`

### Hindsight

- `hindsight-wire`
- `fix/hindsight-tool-envelope`
- `lane1/deadcode-hindsight-finish`

### Gravitee

- `feat/gravitee-repository-observatory`

### Temporal

- `bolt-temporal-lag-index-optimization-7092498872592714131`
- `feat/temporal-langsmith-adapter`
- `ops/fa-ade-claude-temporal-smoke`
- `ops/fa-ade-claude-temporal-smoke-e2757801`
- `ops/temporal-langsmith-matrix-residual-20261001`

### Consolidation rule

The branch census is deliberately retained as a **lineage graph**. The operational source of truth remains current `master` plus merged artifacts. Before deleting or closing anything, compute its unique delta against current `master` and classify it as `LANDED`, `SUPERSEDED`, `RE-EXTRACT`, `ACTIVE`, or `UNKNOWN`.

## 3. Bifrost lineage

Bifrost is already a reconciled integration concept, not a pending wholesale source merge.

- #611 merged the thin RECON/catalog/provider-capability/orchestration slice.
- #613 merged the BIFROST-006 benchmark smoke runbook.
- #671 merged the Codespace-host path for BIFROST-006.
- #775 merged workflow-dispatch Codespace creation.
- #778 merged the Codespace credential/lifecycle SSOT and BIFROST-006 smoke evidence lane.
- The Bifrost Go repositories remain external evaluation surfaces.

**Remaining evidence gap:** the historical Codespace observation is not proof that a Codespace is available today, and the benchmark result must be treated as an observed artifact rather than an architectural claim.

## 4. Gravitee lineage

PR #702 (`feat/gravitee-repository-observatory`) is still open and materially stale relative to current `master`.

Current comparison at recon:

- head: `cd8e1dac94bb34122889ef2a92c41da37c1020e4`
- current master: `79a9914e20f5da6d222f1f3694106ba8c79ec283`
- ahead: 5 commits
- behind: 703 commits
- status: diverged

Disposition: **RETAIN RESEARCH SEED / RE-EXTRACT IF NEEDED**.

Do not merge the historical carrier. Preserve the Gravitee research-seed concept and its repository-observatory tests, then re-root only the unique delta onto current `master` if the capability remains useful.

## 5. Temporal lineage

Temporal is already landed.

- #825 merged the self-host + LangSmith Trajectories adapter.
- #830 merged the current-SHA FA-ADE/Temporal smoke extract.
- #960 merged the 2026-10-01 residual matrix verification.
- Current docs identify GHA Temporal smoke as primary automated evidence, `mcp-docker/temporal/` as the Docker self-host lane, and Codespaces as an optional Worker reproduction surface.

Disposition: **ESTABLISHED P1 SUBSTRATE / NO RESURRECTION**.

Temporal remains downstream of the canonical OTEL/ATES/JSONL evidence boundary; it does not become the evidence authority.

## 6. Hindsight lineage

Hindsight is the current claimed development lane, but most of the functional lineage has already landed:

- #881 merged the `_v1_hindsight.py` client scaffold.
- #885 merged env-gated tool registration.
- #913 merged the OpenAI function-tool envelope repair.
- #931 merged Cloud-wire/path-alignment work.

PR #914 (`lane1/deadcode-hindsight-finish`) remains open but is stale:

- head: `b8e4698170df2035df068789c3c4497545bf809a`
- current master: `79a9914e20f5da6d222f1f3694106ba8c79ec283`
- ahead: 1 commit
- behind: 159 commits
- status: diverged
- unique change: `deepcli/deepagent.py` only

Disposition: **RE-EXTRACT ONE-FILE CLEANUP**, not merge wholesale.

If the dead-code cleanup is still desired, re-root the intent on current `master`, then validate the real async lifecycle rather than preserving the historical no-op cleanup context.

## 7. Consolidated architecture

```text
                    CURRENT MASTER
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Codespaces      Docker/CI       Evidence
     env surfaces      substrate      OTEL/ATES/JSONL
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  Integration Graph
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Bifrost          Temporal         Hindsight
   gateway eval      durable runtime    agent memory
        │                │                │
        ▼                ▼                ▼
    provider          workflows        retain/recall/
    evidence          + traces         reflect
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  manager/evaluation
                  + provenance ledger
```

Gravitee remains adjacent to this graph as a **research-observatory seed**, not a required runtime dependency.

## 8. Rules for the next pass

1. Current `master` wins over stale branch state.
2. Preserve branch/PR history as provenance.
3. Re-root useful deltas; never wholesale-merge a materially stale carrier.
4. Codespace lifecycle states require provider evidence.
5. UNKNOWN is a first-class state.
6. Environment surfaces do not become evidence authorities.
7. Bifrost, Gravitee, Temporal, and Hindsight retain separate ownership boundaries.
8. Every recovered surface records source SHA/ref, observed_at, lifecycle/disposition, and evidence confidence.
9. A "deleted space" claim requires explicit provider evidence; a missing historical name is insufficient.
10. A current development lane must point to a current-SHA carrier or to already-landed functionality.

## 9. Immediate follow-through

- [x] Create #976 reconciliation record.
- [x] Reconcile known Codespace records.
- [x] Reconcile Bifrost lineage.
- [x] Reconcile Temporal lineage.
- [x] Identify stale Gravitee carrier (#702).
- [x] Identify stale Hindsight cleanup carrier (#914).
- [ ] Add this SSOT to the integration-graph navigation.
- [ ] Re-root #702's unique Gravitee delta if still required.
- [ ] Re-root #914's one-file Hindsight cleanup if still required.
- [ ] Add a provider-backed Codespace inventory workflow when an authorized Codespaces API surface is available.

**Policy:** RECON → RE-ROOT → VALIDATE → WATCH → RECORD. No stale-space resurrection by assumption.
