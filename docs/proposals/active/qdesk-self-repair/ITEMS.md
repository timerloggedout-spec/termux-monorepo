# ITEMS — qdesk-self-repair

| ID | Item | Executor | Status |
| --- | --- | --- | --- |
| QSR-1 | Registry entry (#5214) | Hark | executing |
| QSR-2 | Kill switch QDESK_LOOP_ENABLED | Hark | executing |
| QSR-3 | Metrics publish path ops/que/self-repair/metrics.json | Hark | queued |

## Branch reconciliation (BRR) items

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| QSR-BRR-001 | P1 | executing | Build a paginated, read-only branch and PR census with Git ancestry classification. | Every API branch is represented; missing local refs are explicitly unresolved; JSON and Markdown inventories are deterministic and schema-versioned. |
| QSR-BRR-002 | P1 | executing | Project actionable BRR dispositions into the existing QUE self-repair intake. | Idempotency key includes branch, tip SHA and disposition; existing QUE labels and task-plane behavior are reused; malformed inventory fails closed. |
| QSR-BRR-003 | P1 | executing | Run BRR inside the existing scheduled QDesk cycle. | No manual dispatch or duplicate BRR schedule; census precedes intake; 90-day artifact upload is required. |
| QSR-BRR-004 | P1 | executing | Preserve independent review and promotion authority. | No branch mutation APIs are called; claim is not promotion; CI, DoE, Desk/QDesk, branch-protection and owner gates remain intact. |
| QSR-BRR-005 | P1 | executing | Validate exact-head behavior and runtime evidence. | Regression tests pass; QDesk scheduled cycle completes census, QUE intake and artifact upload; failures and deferred items are retained as evidence. |
