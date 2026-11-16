---
type: object
cluster: governance
universe: live
status: verified
entity: CLAUDE.md
verified_at: 2026-11-16
---

# Change Control

**Change Control** is the monorepo’s governed path from a registered work item through a `master`-based feature branch, an exact-delta ICM impact receipt, required validation, and human-reviewed integration.

## Why this shape

The repository separates implementation from promotion so new work is traceable to a proposal item, checked before merge, and does not silently alter protected baselines or credential-sensitive state. The impact receipt makes the first-order documentation decision part of the same pull request as the source change.

## Shape

- Root `CLAUDE.md` requires integration work to target `master`, cites work items, and requires an ICM impact receipt for every pull request.
- The receipt under `docs/icm/changes/` enumerates the exact PR delta, existing primary ICM cards, related records changed in the PR, and either an `updated` or justified `no-map-change` disposition.
- `.github/workflows/repo-gate.yml` runs `scripts/ci/icm_impact_gate.py` on pull requests; the standard repo gate and Termux smoke checks remain separate required validation evidence.
- The proposal process registers work, itemizes it, records review/acceptance, and couples completion to gate evidence.
- Human-only edges include credential rotation, history rewrite, protected-branch rules, device state, and interactive provider login.

Citations: `CLAUDE.md`, `docs/proposals/PROCESS.md:1-36`, `docs/proposals/AGENTIC-PERMISSIONS.md:3-27`, `.github/workflows/repo-gate.yml`.

## Connected to

- **owns:** the documented branch, item, evidence, impact-receipt, and approval expectations for tracked changes.
- **owned-by:** root `CLAUDE.md`, `docs/proposals/*`, and the repo-gate workflow.
- **joins:** a requested edit to a scoped proposal, feature branch, impact receipt, validation run, and reviewable update.
- **looks-like-but-is-not:** permission to force-push, rewrite history, rotate credentials, or change device state without explicit operator approval.

## If you change this

- **Hits:** governance documents, proposal records, branch conventions, ICM impact receipts, and CI/review expectations.
- **Does not hit:** the implementation of an unrelated subsystem unless the approved change explicitly includes it.

## Surfaces

| Surface | Role |
|---|---|
| Operator | Authorizes protected, credential, device, and review edges. |
| Agent or developer | Implements a scoped item on a feature branch and records evidence. |
| Proposal registry | States work status and active item ownership. |
| ICM impact receipt | Provides machine-checked first-order impact and related-update evidence. |
| Gates | Provide required repository and Termux validation evidence. |

## See

- Source: [`CLAUDE.md`](../../../../CLAUDE.md)
- Source: [`docs/proposals/PROCESS.md`](../../../proposals/PROCESS.md)
- Source: [`docs/proposals/AGENTIC-PERMISSIONS.md`](../../../proposals/AGENTIC-PERMISSIONS.md)
