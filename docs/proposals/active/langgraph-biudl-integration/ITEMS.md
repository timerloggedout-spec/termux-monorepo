# ITEMS — langgraph-biudl-integration

| ID | Item | Status | Notes |
|---|---|---|---|
| LGB-001 | Recon Awesome LangGraph, official skills, and current repository architecture | **done** | Existing native orchestration/evidence and Temporal contracts reused |
| LGB-002 | Add repository-native LangGraph orchestration skill | **done** | Official fundamentals/HITL/persistence sources pinned by blob SHA |
| LGB-003 | Document BIUDL integration and adapter boundaries | **done** | No duplicate control plane or mandatory dependency |
| LGB-004 | Implement minimal optional Python StateGraph proof with deterministic stub nodes | backlog | Requires approved plan, dependency placement, and runnable test environment |
| LGB-005 | Implement checkpoint + interrupt/resume + side-effect idempotency proof | backlog | Must select/test backend; no production database implied |
| LGB-006 | Extend existing OrchestratorTracer / ATES bridge with a versioned graph-event contract | backlog | Current schema has six event kinds and no node identity; add allowlisted fields + privacy tests; do not repurpose ACTION-EFFECT-EVENT |
| LGB-007 | Compare native manager vs LangGraph treatments on same MVT cohort | backlog | Require task fingerprints, equal validation, cost/time/outcome measures |
| LGB-008 | Run current-SHA dual gates and promote verified slice | backlog | Do not equate PR creation or queued checks with validation |
| LGB-009 | Build the competitive orchestration treatment portfolio and benchmark corpus | **specified** | See COMPETITION-MATRIX.md; native control, LangGraph, Deep Agents, swarm/handoff, supervisor pattern, and hybrid |
| LGB-010 | Synthesize and test hybrid patterns from independently validated strengths | backlog | Preserve attribution, authority boundaries, rollback, and no self-promotion |
