# ITEMS — langgraph-biudl-integration

| ID | Item | Status | Notes |
|---|---|---|---|
| LGB-001 | Recon Awesome LangGraph, official skills, and current repository architecture | **done** | Existing native orchestration/evidence and Temporal contracts reused |
| LGB-002 | Add repository-native LangGraph orchestration skill | **done** | Official fundamentals/HITL/persistence sources pinned by blob SHA |
| LGB-003 | Document BIUDL integration and adapter boundaries | **done** | No duplicate control plane or mandatory dependency |
| LGB-004 | Implement minimal optional Python StateGraph proof with deterministic stub nodes | backlog | Requires approved plan, dependency placement, and runnable test environment |
| LGB-005 | Implement checkpoint + interrupt/resume + side-effect idempotency proof | backlog | Must select/test backend; no production database implied |
| LGB-006 | Add sanitized LangGraph lifecycle events to OTEL/ATES/evidence adapter | backlog | Reuse canonical schemas; prove privacy by tests |
| LGB-007 | Compare native manager vs LangGraph treatments on same MVT cohort | backlog | Require task fingerprints, equal validation, cost/time/outcome measures |
| LGB-008 | Run current-SHA dual gates and promote verified slice | backlog | Do not equate PR creation or queued checks with validation |
