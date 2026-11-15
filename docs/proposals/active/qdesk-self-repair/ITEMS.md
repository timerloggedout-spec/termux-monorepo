# Items — QDesk self-repair loop

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| QSR-001 | P1 | queued | Register the proposal and map existing SIE/QUE machinery to the lifecycle. | Proposal registry, manifest and item list agree; all referenced paths exist; no duplicate scheduler or ledger is introduced. |
| QSR-002 | P1 | queued | Verify intake coverage for failing master runs, stale feeds and open Desk issues. | Each intake class has a source, dedupe key, receipt, and tested failure behavior. |
| QSR-003 | P1 | queued | Verify diagnosis/RFP artifact generation and source-SHA/run-URL provenance. | Every diagnosis is tied to a failing run and source revision; no unsupported root-cause claims. |
| QSR-004 | P1 | queued | Verify independent DoE evaluation and promotion guard. | Builder cannot self-verify; CI replay and independent review are required; auto-merge is not enabled by this proposal. |
| QSR-005 | P1 | queued | Verify learn-ledger updates and regression handling. | Outcomes are evidence-backed, idempotent and traceable by failure class/role. |

## Execution state

All items remain queued until current-master evidence establishes their acceptance criteria. The existence of `scripts/que/self_repair.py` and its workflow is not proof that every lifecycle stage is operating.
