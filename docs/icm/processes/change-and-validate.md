---
type: process
universe: live
status: verified
consumes:
  - ../objects/governance/change-control.md
  - ../../../CLAUDE.md
  - ../../../docs/proposals/registry.yaml
produces:
  - scoped feature branch
  - exact-delta ICM impact receipt
  - work-item evidence
  - validation evidence
verified_at: 2026-11-16
---

# Change and Validate

A tracked monorepo change moves from an active, itemized request to a `master`-based feature branch, a machine-readable ICM impact receipt, focused implementation, validation evidence, and human-reviewed integration.

## Input → Movement → Output

A request and its work item are the input. The implementer branches from `master`, records the exact pull-request delta and first-order ICM impact in `docs/icm/changes/<change-id>.json`, makes only the scoped change, cites the item ID, and runs the required checks. The output is a reviewable branch or pull request with a validated receipt, evidence, and any known baseline blockers recorded.

## Why this shape

Skipping registration, branching without a registered item, or treating unrelated gate failures as permission to change broad source areas would make ownership, regression risk, and promotion state opaque. Skipping the impact receipt would also allow source, workflow, contract, and operational changes to drift away from the map that routes future work.

## Steps

1. Read the active proposal registry and select or register the item. Cite `docs/proposals/registry.yaml` and `docs/proposals/PROCESS.md:31-36`.
2. Create a feature branch from `master` (a `master-staging` base only when that lane is active). Cite `CLAUDE.md:56` and `CLAUDE.md:72-74`.
3. Before opening the PR, add exactly one `docs/icm/changes/<change-id>.json` receipt. Its `changed_paths` must exactly match the PR delta; `primary_cards` must identify existing ICM cards; `related_updates` must identify related records changed in the same PR; and `disposition` must be `updated` or `no-map-change`. An `updated` receipt must include a changed primary card. A `no-map-change` receipt requires a concrete rationale.
4. Implement only the item scope and record the `Implements: <ITEM-ID>` reference in the commit or pull request. Update the directly affected ICM card/process/effect route and related proposal or architecture records when the change alters their truth.
5. Run `python3 scripts/ci/icm_impact_gate.py --base <base-ref>`, `python3 scripts/ci/repo_gate.py`, and `python3 scripts/ci/termux_smoke.py`; separate pre-existing failures from branch changes. The ICM impact validator runs as the distinct `ICM impact gate` job in `.github/workflows/repo-gate.yml` on every PR. Branch protection must require that exact status check for merge blocking.
6. Present the branch and evidence for review; do not merge, force-push, rotate credentials, or change protected settings without explicit operator authority. Cite `docs/proposals/AGENTIC-PERMISSIONS.md:9-27`.

## Receipt contract

The receipt is JSON with exactly these keys: `schema_version` (1), `change_id`, `disposition`, `changed_paths`, `primary_cards`, `related_updates`, and `rationale`. Paths are repository-relative, unique, and traversal-free. The gate rejects missing, stale, unsafe, unsupported, or incomplete records.

## If you change this

- **Hits:** proposal state, feature branch scope, commit/PR evidence, the impact receipt, and the directly relevant validation surface.
- **Does not hit:** protected baseline history or device-side Termux state without a separately authorized operation.

## Surfaces

| Surface | Role |
|---|---|
| Operator | Authorizes human-only edges and approves review decisions. |
| Implementer | Performs the scoped edit and records evidence. |
| Proposal registry | Provides the item and status record. |
| ICM impact receipt | Records the exact PR delta, primary cards, related updates, and disposition. |
| Repository and smoke gates | Report promotion readiness or specific blockers. |

## See

- Objects: [`../objects/governance/change-control.md`](../objects/governance/change-control.md)
- Source: [`CLAUDE.md`](../../../CLAUDE.md)
- Source: [`docs/proposals/PROCESS.md`](../../proposals/PROCESS.md)
