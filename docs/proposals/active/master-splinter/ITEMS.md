# ITEMS — AppID control plane (Registrar)

This is a specification/index ledger, not an implementation authorization. Item status records the state of the supplied proposal documents only.

| ID | Work / deliverable | Source | Status | Boundary |
|---|---|---|---|---|
| MS-01 | Reconcile the proposed control plane with the existing eight-AppID family | `EVALUATION.md` §1–2 | specified | ADAPT disposition; no App consolidation or ninth App |
| MS-02 | Define read-only inventory, permission snapshots, replay lineage, and usage join | `SPEC.md` §1–2 | specified | Existing stores remain authoritative |
| MS-03 | Define the database/read-model schema | `SPEC.md` §3 | specified | `usage_events` is a view/join, not a new store |
| MS-04 | Define the dry-run migration replay contract | `SPEC.md` §5 | specified | Simulation only; no write tokens or state mutation |
| MS-05 | Any deployment, repository/App provisioning, or credential movement | `INTAKE.md` and `EVALUATION.md` | owner-gated | Not authorized by this proposal record |

## Completion criteria

The scoped specification is recorded in `SPEC.md`; no implementation or production rollout is represented as complete. Changes to owner-gated items require a separate explicit authorization and evidence-backed proposal update.
