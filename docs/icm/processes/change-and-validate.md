---
type: process
universe: live
status: verified
consumes:
  - ../objects/governance/change-control.md
  - ../../../AGENTS.md
  - ../../../docs/proposals/registry.yaml
produces:
  - scoped feature branch
  - work-item evidence
  - validation evidence
verified_at: 2026-08-17
---

# Change and Validate

A tracked monorepo change moves from an active, itemized request to a `master-staging`-based feature branch, focused implementation, validation evidence, and human-reviewed integration.

## Input → Movement → Output

A request and its work item are the input. The implementer branches from `master-staging`, makes only the scoped change, cites the item ID, and runs the required checks. The output is a reviewable branch or pull request with evidence and any known baseline blockers recorded.

## Why this shape

Skipping registration, using raw `master`, or treating unrelated gate failures as permission to change broad source areas would make ownership, regression risk, and promotion state opaque.

## Steps

1. Read the active proposal registry and select or register the item. Cite `docs/proposals/registry.yaml` and `docs/proposals/PROCESS.md:31-36`.
2. Create a feature branch from `master-staging`, not raw `master`. Cite `AGENTS.md:18-29`.
3. Implement only the item scope and record the `Implements: <ITEM-ID>` reference in the commit or pull request. Cite `AGENTS.md:20-29`.
4. Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`; separate pre-existing failures from branch changes. Cite `AGENTS.md:20-24`.
5. Present the branch and evidence for review; do not merge, force-push, rotate credentials, or change protected settings without explicit operator authority. Cite `docs/proposals/AGENTIC-PERMISSIONS.md:9-27`.

## If you change this

- **Hits:** proposal state, feature branch scope, commit/PR evidence, and the directly relevant validation surface.
- **Does not hit:** protected baseline history or device-side Termux state without a separately authorized operation.

## Surfaces

| Surface | Role |
|---|---|
| Operator | Authorizes human-only edges and approves review decisions. |
| Implementer | Performs the scoped edit and records evidence. |
| Proposal registry | Provides the item and status record. |
| Repository and smoke gates | Report promotion readiness or specific blockers. |

## See

- Objects: [`../objects/governance/change-control.md`](../objects/governance/change-control.md)
- Source: [`AGENTS.md`](../../../AGENTS.md)
- Source: [`docs/proposals/PROCESS.md`](../../proposals/PROCESS.md)
