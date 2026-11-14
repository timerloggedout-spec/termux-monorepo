# ITEMS — que-sie-pipeline-integration

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| QSI-001 | P0 | in_review | Define the SIE lifecycle contract and typed stage transitions. | Versioned schema; deterministic transition validator; idempotent event identity; transition and terminal-state tests. |
| QSI-002 | P0 | in_review | Connect workflow failure, queue stall, watchdog and feed-freshness signals to SIE intake. | Workflow failure and feed freshness reuse QDesk intake; dispatch-state escalation and stall receipts produce stable, deduplicated SIE groups with issue evidence; verify live producer parity before acceptance. |
| QSI-003 | P0 | in_review | Generate evidence-bounded research packets and Oracle Method briefs from admitted SIE items. | Validate the SIE receipt; verify evidence-item hashes and freshness; separate confirmed facts from stale/missing claims; emit deterministic package digest and Oracle Method brief; preserve replay, baseline, risks and acceptance tests. |
| QSI-004 | P0 | todo | Bind Delphi awards to complete RFP package digest and verify award at the consumer. | QD-039 and issue #5156 acceptance; independent reviewer identity; stale package disposition held. |
| QSI-005 | P1 | todo | Register DoE designs and competing candidate implementation arms. | Frozen task/base SHA/evaluator/tools/instance identity; pre-registered factors, assignment, sample and stopping rules. |
| QSI-006 | P1 | todo | Wire QUE rank, claim class, lease and reclaim receipts into the SIE stage machine. | Rank-ordered claim, typed claim routing, idempotent lease lifecycle and explicit exception escalation. |
| QSI-007 | P1 | todo | Define gated adapters for SWE reference evaluation, DSPy DoE design and Lean/Batteries pre-proofing research. | Pin workload, runtime maturity, toolchain and provenance; preserve manual/reference/design-only boundaries; common task/evidence envelope; quality-first outcomes and resource costs. |
| QSI-008 | P1 | todo | Publish Observatory stage and performance projections from canonical feeds. | Current stage/owner/age/evidence freshness/current SHA; source parity; stale and unknown states explicit. |
| QSI-009 | P1 | todo | Run shadow routing and bounded DoE pilot. | Frozen baseline, independent verifier, comparison against live QUE decisions, uncertainty and cost reporting. |
| QSI-010 | P1 | todo | Promote verified SIE learning into existing ranking/role weights. | Append-only receipts, idempotent updates, regression retention, sensitivity review and rollback path. |

## Disposition

QSI-001 is the lifecycle contract slice. QSI-002 has an initial queue/watchdog adapter in review; verify live producer parity and CI before acceptance. QSI-003 has an initial evidence-bounded packet builder in review; Oracle Method remains the canonical renderer. QSI-004–QSI-010 remain queued behind their dependencies and existing owner/domain gates. This proposal composes existing QDesk RFP #5145 and QD-039/#5156 rather than replacing them.
