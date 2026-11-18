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
  - work-item evidence
  - validation evidence
verified_at: 2026-11-01
---

# Change and Validate

A tracked monorepo change moves from an active, itemized request to a `master`-based feature branch, focused implementation, automated dual-gate evidence, adaptive WAIT, and FA-ADE promotion when the outcome is verified.

## Input → Movement → Output

A request and its work item are the input. The agent branches from `master` (or `master-staging` only when root policy says that lane is active), makes only the scoped change, cites the item ID, runs both required gates, watches current-head CI to terminal state, and verifies the task outcome. The output is promoted when FA-ADE conditions pass, or remains a reviewable blocked branch/PR with exact evidence.

## Why this shape

Skipping registration, branching without a registered item, or treating unrelated gate failures as permission to change broad source areas would make ownership, regression risk, and promotion state opaque.

## Steps

1. Read the active proposal registry and select or register the item. Cite `docs/proposals/registry.yaml` and `docs/proposals/PROCESS.md:31-36`.
2. Create a feature branch from `master` (a `master-staging` base only when that lane is active). Cite `CLAUDE.md:56` and `CLAUDE.md:72-74`.
3. Implement only the item scope and record the `Implements: <ITEM-ID>` reference in the commit or pull request. Cite `CLAUDE.md:60-61`.
4. Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`; separate pre-existing failures from branch changes. Cite `CLAUDE.md:57-59`.
5. Re-fetch the exact head SHA and inspect checks, jobs, steps, logs, and artifacts. Auto-promote when both required gates are green and the task outcome is verified, subject to configured repository protections. Stop for explicit authorization only at the human-only edges in `docs/proposals/AGENTIC-PERMISSIONS.md`; do not force-push, rotate credentials, or change protected settings without that authority.

## If you change this

- **Hits:** proposal state, feature branch scope, commit/PR evidence, and the directly relevant validation surface.
- **Does not hit:** protected baseline history or device-side Termux state without a separately authorized operation.

## Surfaces

| Surface | Role |
|---|---|
| Operator | Authorizes only the human-only edges reserved by repository policy. |
| Implementer | Performs the scoped edit and records evidence. |
| Proposal registry | Provides the item and status record. |
| Repository and smoke gates | Provide automated promotion evidence and specific blockers. |

## See

- Objects: [`../objects/governance/change-control.md`](../objects/governance/change-control.md)
- Source: [`CLAUDE.md`](../../../CLAUDE.md)
- Source: [`docs/proposals/PROCESS.md`](../../proposals/PROCESS.md)
