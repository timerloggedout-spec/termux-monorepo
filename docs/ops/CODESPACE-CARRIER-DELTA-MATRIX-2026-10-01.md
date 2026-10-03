# Integration Carrier Delta Matrix — 2026-10-01

**Canonical base:** `master`  
**Purpose:** machine-reviewable consolidation ledger for historical Codespace, Bifrost, Hindsight, Gravitee, and Temporal carriers.

## Disposition vocabulary

- **LANDED** — equivalent functionality is already on current `master`; preserve carrier as provenance only.
- **SUPERSEDED** — current tree replaces the carrier's implementation shape.
- **RE-EXTRACT** — inspect and port only validated unique intent.
- **PROVENANCE** — retain for historical traceability; not a merge source.
- **UNKNOWN** — insufficient evidence for a stronger claim.
- **ACTIVE/PROTECTED** — do not clean up until current development state is explicitly reconciled.

## Matrix

| Carrier | Ahead | Behind | Unique files | Disposition | Protection |
|---|---:|---:|---:|---|---|
| codespaces-multi-lane-agent-roles | 4 | 980 | 8 | SUPERSEDED / PROVENANCE | No |
| docs/proposals/codespaces-enablement | 10 | 902 | 3 | RE-EXTRACT | No |
| feat/codespace-agent-devcontainer | 2 | 1006 | 2 | RE-EXTRACT | No |
| feat/codespace-production-lane | 2 | 1005 | 2 | RE-EXTRACT | No |
| gaps-opps/add-devcontainer-codespaces | 1 | 1041 | 1 | SUPERSEDED | No |
| ops/codespace-create-secret-chain | 0 | 689 | 0 | LANDED / STALE | No |
| ops/codespace-create-use-archwiz-token | 3 | 689 | 1 | LANDED / STALE CARRIER | No |
| ops/codespace-create-workflow-dispatch | 1 | 691 | 2 | LANDED / STALE CARRIER | No |
| ops/codespace-start-existing | 2 | 683 | 2 | RE-EXTRACT IF REQUIRED | No |
| docs/codespace-bifrost-006-run | 1 | 857 | 2 | LANDED / PROVENANCE | No |
| ops/bifrost-006-evidence-and-codespace-ssot | 2 | 686 | 6 | LANDED / PROVENANCE | No |
| docs/bifrost-006-benchmark-runbook | 1 | 914 | 2 | LANDED / PROVENANCE | No |
| docs/bifrost-gateway-recon-reconcile | 3 | 922 | 7 | RE-EXTRACT SELECTIVELY | No |
| hindsight-wire | 24 | 1838 | 10 | PROVENANCE / RE-EXTRACT SELECTIVELY | No |
| fix/hindsight-tool-envelope | 0 | 214 | 0 | LANDED / STALE | No |
| lane1/deadcode-hindsight-finish | 1 | 246 | 1 | RE-EXTRACT ONE FILE | Protect if work resumes |
| feat/gravitee-repository-observatory | 5 | 790 | 5 | RETAIN SEED / RE-EXTRACT | No |
| bolt-temporal-lag-index-optimization-7092498872592714131 | 1 | 1083 | 3 | RE-EXTRACT AFTER VALIDATION | No |
| feat/temporal-langsmith-adapter | 5 | 564 | 14 | LANDED / PROVENANCE | No |
| ops/fa-ade-claude-temporal-smoke | 4 | 558 | 3 | LANDED / PROVENANCE | No |
| ops/fa-ade-claude-temporal-smoke-e2757801 | 0 | 557 | 0 | LANDED / STALE | No |
| ops/temporal-langsmith-matrix-residual-20261001 | 3 | 128 | 3 | LANDED / PROVENANCE | No |

## Recovered Codespaces

| Identifier | State claim | Evidence confidence | Consolidation rule |
|---|---|---|---|
| glorious-capybara-wrq7vrqj7xqjh995p | Shutdown observed; development candidate recovered | Observed historical + user recovery | PROTECTED until reconciled |
| agent-bifrost-006-5g7qvg7pqjggh4jqv | Provisioning → Available observed | Observed | Preserve as BIFROST-006 evidence |
| list-only-probe-v6jvp6j7v75xfxxv9 | Probe identity recovered | User recovery only | Preserve as probe; no promotion |
| congenial-space-doodle-5g7q7pqpw92q7v | Unknown | User recovery only | Inventory first |
| hindsight-1552-4jp7qjp975j73q9qj | Development identity recovered | User recovery only | PROTECTED until reconciled |

## Execution rule

`compare(master, carrier) → enumerate unique files → inspect intent → classify → re-root validated delta → validate → record`.

No carrier is a production source of truth merely because it exists as a Git branch.
