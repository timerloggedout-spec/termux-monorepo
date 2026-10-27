# Architecture — Index & Conventions

**Status:** living index
**Owner/lane:** Infrastructure Architecture (organization | documentation | specification)
**Canonical for:** where the canonical architecture spec for each domain lives
**Last verified:** 2026-10-26, against the live master tree (docs/ = 2,043 files; docs/ops root = 238 Markdown files; docs/ops/generated = 1,334 files; docs/architecture = 13 Markdown + 3 Mermaid + 1 JSON receipt, post-#1678)

## How this surface is organized

- Canonical architecture specs and decision records live in `docs/architecture/`.
- Operational contracts that are architecture-grade legitimately live in `docs/ops/` (and a few in `docs/schemas/`). This index **points** at them — it never copies their content. The pointed-to document is the single source; if this index and a source disagree, the source wins and the index gets fixed.
- `docs/ops/generated/` holds generated projections (1,334 files). A projection is never a canonical spec, no matter how spec-like it reads.
- One canonical spec per domain. A proposal names what it would replace; a superseded doc keeps its text, gains a status line and a pointer to its successor, and leaves the canonical slot in this index.

## Residents of docs/architecture

| Document | Class | Status (per its own text) | Scope |
|---|---|---|---|
| [AGENT-EVALUATION-FRAMEWORK.md](AGENT-EVALUATION-FRAMEWORK.md) | Canonical spec | Not stated — backfill tracked below | The measurement layer: evaluation units for agents, managers, prompts, tools, orchestration policies, providers/models (the MVT/DoE measurement home) |
| [AGENT-SELECTION-BLIND-EVALUATION.md](AGENT-SELECTION-BLIND-EVALUATION.md) | Companion spec | Not stated — backfill tracked below | Double-blind-style evaluation layer separating treatment identity from evaluation identity, inside the framework above |
| [TOOL-DEFINITION-QUALITY-SCORE.md](TOOL-DEFINITION-QUALITY-SCORE.md) | Integration spec | Stated: integrated as an evaluation/observability provider lane | Tool-definition quality as a signal inside the Agent Evaluation Framework; explicitly not a router policy or leaderboard metric |
| [AGENT-TEAM-CONTROL-PLANE.md](AGENT-TEAM-CONTROL-PLANE.md) (+ `.mmd`) | Architecture spec | Not stated — backfill tracked below | The agent-team operating loop and control-plane shape |
| [CANONICAL-ISSUE-OBSERVATORY.md](CANONICAL-ISSUE-OBSERVATORY.md) | Spec | Not stated — backfill tracked below (doc cites "Implements: #192") | Issue lifecycle evidence plane; GitHub remains the system of record |
| [DETERMINISTIC-DAG-ORCHESTRATION.md](DETERMINISTIC-DAG-ORCHESTRATION.md) | Spec | Stated: reference implementation only | Static dependency-graph planning and dependency admission; plans and classifies, does not execute |
| [SELF-HEALING-ENGINE.md](SELF-HEALING-ENGINE.md) | Design proposal | Stated: Proposed P0 architecture | End-to-end autonomous remediation factory workload (detect → incident → diagnose → dispatch → verify → promote/escalate) |
| [SELF-HEALING-ENGINE-ROADMAP.md](SELF-HEALING-ENGINE-ROADMAP.md) | Delivery roadmap | Stated per slice (implemented / in progress) | P0 delivery slices for the Self-Healing Engine; companion to the proposal above, not a duplicate |
| [termux-agentic-hub.md](termux-agentic-hub.md) | Architecture spec | Not stated — backfill tracked below | Termux Agentic Hub runtime topology on the BLU B160V; capability-envelope execution, no free-form commands |
| [transport-and-identity-decision.md](transport-and-identity-decision.md) | Decision record | Stated: Accepted for version one | Local Termux execution + GitHub-backed structured jobs; direct interactive transport deferred |
| [INFRASTRUCTURE-REGISTRY-DESIGN.md](INFRASTRUCTURE-REGISTRY-DESIGN.md) | Design spec | Stated: design proposal; not a runtime contract | CMDB / IDRR — infrastructure inventory, identity, ownership, health, and reconciliation architecture (issue #1654; landed via PR #1678). Canonical pointer for this domain |
| [INFRASTRUCTURE-CMDB-P0-INVENTORY.md](INFRASTRUCTURE-CMDB-P0-INVENTORY.md) · [INFRASTRUCTURE-CMDB-P1-AUTHORITY-WRITER-MATRIX.md](INFRASTRUCTURE-CMDB-P1-AUTHORITY-WRITER-MATRIX.md) · [infra-cmdb-sweep-manifest.json](infra-cmdb-sweep-manifest.json) | Baseline + matrix + census receipt | Stated per document | Companions to the registry design: P0 tracked-path census and authority map, P1 field-level authority/writer matrix, machine-readable sweep receipt |

**Landed 2026-10-26:** the CMDB / IDRR family (PR #1678, superseding draft PR #1655) — see the residents table above. Issue #1654 closed on landing; the design's implementation phases remain separate decisions under its own phase gates.

## Domain pointers — canonical spec lives elsewhere

| Domain | Canonical source |
|---|---|
| Routing & orchestration | [docs/ops/ROUTING-ORCHESTRATION-MAP.md](../ops/ROUTING-ORCHESTRATION-MAP.md) |
| Evidence projection (read model) | [docs/ops/EVIDENCE-PROJECTION-SURFACE.md](../ops/EVIDENCE-PROJECTION-SURFACE.md) |
| Execution & provenance contract (BIUDL) | [docs/ops/BIUDL-EXECUTION-AND-PROVENANCE.md](../ops/BIUDL-EXECUTION-AND-PROVENANCE.md) |
| Evidence substrate | [docs/ops/AGENT-EVIDENCE-SUBSTRATE.md](../ops/AGENT-EVIDENCE-SUBSTRATE.md) |
| Reconciliation control plane | [docs/ops/RECONCILIATION-CONTROL-PLANE.md](../ops/RECONCILIATION-CONTROL-PLANE.md) · [v2](../ops/RECONCILIATION-CONTROL-PLANE-v2.md) · [index](../ops/RECONCILIATION-CONTROL-PLANE-INDEX.md) — relationship between v1 and v2 unstated; see hygiene backlog |
| Quota registry & entitlement contracts | [docs/ops/QUOTA-REGISTRY.md](../ops/QUOTA-REGISTRY.md) (+ `ops/quota/registry.json`) |
| Provider quota managers | [docs/ops/PROVIDER-QUOTA-MANAGERS.md](../ops/PROVIDER-QUOTA-MANAGERS.md) |
| Provider capabilities | [docs/schemas/provider-capabilities.md](../schemas/provider-capabilities.md) |
| Integration mesh | [docs/ops/INTEGRATION-MESH-MATRIX.md](../ops/INTEGRATION-MESH-MATRIX.md) |
| Web Adapter Foundry | [docs/ops/WEB-ADAPTER-FOUNDRY.md](../ops/WEB-ADAPTER-FOUNDRY.md) (+ `ops/web_adapter_foundry/`) |
| Device pull queue | Spec: [docs/ops/P1-PULL-QUEUE-SPEC.md](../ops/P1-PULL-QUEUE-SPEC.md) · Runbook: [docs/ops/DEVICE-PULL-QUEUE.md](../ops/DEVICE-PULL-QUEUE.md) |
| Reviewer JIT (measured reviewer policy) | [docs/ops/REVIEWER-JIT-DESIGN.md](../ops/REVIEWER-JIT-DESIGN.md) |
| Secrets audit (phantom-secret reconciliation) | [docs/ops/PHANTOM-SECRETS-AUDIT.md](../ops/PHANTOM-SECRETS-AUDIT.md) · Credential inventory of record: Issue #184 (names / last-used only) · Naming: [docs/ops/SECRET-NAMING-CONVENTION.md](../ops/SECRET-NAMING-CONVENTION.md) · Registry: [docs/ops/secrets-and-variables-registry.md](../ops/secrets-and-variables-registry.md) |
| Backend & free-tier architecture | [docs/ops/FREE-TIER-BACKEND-RECON-2026-10-21.md](../ops/FREE-TIER-BACKEND-RECON-2026-10-21.md) · [docs/ops/RESILIENCY-MAP-AND-STACK-PROPOSAL-2026-10-21.md](../ops/RESILIENCY-MAP-AND-STACK-PROPOSAL-2026-10-21.md) |
| Agent coordination & monikers | [docs/ops/AGENT-MONIKERS.md](../ops/AGENT-MONIKERS.md) |

## Conventions for architecture documents

Every architecture-grade document carries a header block directly under its title:

```text
**Status:** canonical | proposal | decision (accepted | superseded by <link>) | roadmap | superseded by <link>
**Owner/lane:** <lane or role that maintains this document>
**Canonical for:** <the one domain this document is the single source for>
**Review record:** <PR / issue link where the current version was reviewed>
```

Rules:

1. **One canonical spec per domain.** If two documents claim the same domain, the conflict is resolved in this index first, then in the documents.
2. **Proposals say what they would replace** and link the incumbent. A merged proposal is a proposal until its status line says otherwise.
3. **Superseded documents are marked, not deleted.** Status line + pointer to the successor; history stays readable.
4. **Decision records are immutable once accepted.** A changed decision is a new record that supersedes the old one.
5. **Generated projections never present as specs.** Anything under a `generated/` path is a projection of a canonical source named in that source's own documentation.
6. **Status changes land with the change they describe** — a status line edited after the fact, without the underlying change, is drift.

## Hygiene backlog (from the 2026-10-26 recon)

- **Status backfill:** 5 of the 10 residents state no status (Agent Evaluation Framework, Blind Evaluation, Agent Team Control Plane, Canonical Issue Observatory, Termux Agentic Hub). Owners to confirm status; this lane will land the header blocks once confirmed — statuses are not invented here.
- **Reconciliation pair:** `RECONCILIATION-CONTROL-PLANE.md` calls itself the "active design contract" while `-v2.md` describes the production observe-only engine, with no stated relationship. Owners to confirm which is canonical for engine behavior; then cross-link and mark accordingly.
- **Evidence architecture is stated in at least four places** (evidence substrate, evidence projection surface, foresight evidence spine, BIUDL provenance). The pointer table above is the interim map; a single consolidated evidence-architecture statement is a candidate future spec.
- **`docs/schemas/` mixes true schemas with registries** (e.g. `agent-roster.yaml`, `model-rotation.yaml` are registries, not schemas). Naming note for a future pass; no moves yet.
- **Architecture strays at the docs root** (`GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md`, `ICM-ARCHITECT-INTEGRATION.md`, `CONSENSUS.md`, `DEPLOYMENT-LANES.md`) are candidates for pointer entries or relocation in a later pass — no file moves without a repo-wide link-breakage check first.
