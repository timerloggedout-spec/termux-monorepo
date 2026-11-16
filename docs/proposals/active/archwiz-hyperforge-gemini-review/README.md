# ArchWiz Hyper-Forge — Gemini Review Package

This directory is the **canonical collaborative review package** for the Gemini-derived Hyper-Forge proposal.

## Artifact separation

| Artifact | Purpose |
|---|---|
| `GEMINI-PLAN.md` | Preserve the proposal's source intent and terminology. |
| `IMPLEMENTATION-MATRIX.md` | Reconcile source items against actual repository implementation/evidence. |
| `ENGINEERING-CONSIDERATIONS.md` | Record engineering interpretation, constraints, safety boundaries, and unresolved decisions. |
| `MILESTONES.yaml` | Derived milestone/task decomposition and current state. |

## GitHub collaboration

- Parent review hub: #943
- M0: #951
- M1: #952
- M2: #944
- M3: #945
- M4: #946
- M5: #947
- M6: #948
- M7: #949
- M8: #950
- Implementation baseline: PR #937 (merged)

## Review invariant

`source requirement` ≠ `implementation` ≠ `engineering interpretation` ≠ `evidence` ≠ `promotion`

A milestone can be implemented in code while still remaining open for review. A proposal item is not complete merely because a related UI surface exists.

## Current state

- **M0 governance:** implemented/documented on this branch.
- **M1 Termux cockpit:** implemented on `master` through PR #937.
- **M2–M4:** partial; follow-up issues open.
- **M5:** planned native Android surface.
- **M6:** partial agent/workflow parity.
- **M7:** planned research/environment lane.
- **M8:** review/promotion gate.

Promotion remains an explicit operator decision.
