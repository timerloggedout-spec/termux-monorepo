---
type: object
cluster: governance
universe: live
status: verified
entity: AGENTS.md
verified_at: 2026-08-17
---

# Change Control

**Change Control** is the monorepo’s governed path from a registered work item through a `master-staging`-based feature branch, required validation, and human-reviewed integration.

## Why this shape

The repository separates implementation from promotion so new work is traceable to a proposal item, checked before merge, and does not silently alter protected baselines or credential-sensitive state.

## Shape

- `AGENTS.md` requires integration work to target `master-staging`, names the repository and Termux smoke gates, and requires item citations in commits or pull requests.
- The proposal process registers work, itemizes it, records review/acceptance, and couples completion to gate evidence.
- Human-only edges include credential rotation, history rewrite, protected-branch rules, device state, and interactive provider login.

Citations: `AGENTS.md:5-29`, `AGENTS.md:37-48`, `docs/proposals/PROCESS.md:1-36`, `docs/proposals/AGENTIC-PERMISSIONS.md:3-27`.

## Connected to

- **owns:** the documented branch, item, evidence, and approval expectations for tracked changes.
- **owned-by:** `AGENTS.md` and `docs/proposals/*`.
- **joins:** a requested edit to a scoped proposal, feature branch, validation run, and reviewable update.
- **looks-like-but-is-not:** permission to force-push, rewrite history, rotate credentials, or change device state without explicit operator approval.

## If you change this

- **Hits:** governance documents, proposal records, branch conventions, and CI/review expectations.
- **Does not hit:** the implementation of an unrelated subsystem unless the approved change explicitly includes it.

## Surfaces

| Surface | Role |
|---|---|
| Operator | Authorizes protected, credential, device, and review edges. |
| Agent or developer | Implements a scoped item on a feature branch and records evidence. |
| Proposal registry | States work status and active item ownership. |
| Gates | Provide required repository and Termux validation evidence. |

## See

- Source: [`AGENTS.md`](../../../../AGENTS.md)
- Source: [`docs/proposals/PROCESS.md`](../../../proposals/PROCESS.md)
- Source: [`docs/proposals/AGENTIC-PERMISSIONS.md`](../../../proposals/AGENTIC-PERMISSIONS.md)
