# ITEMS — langgraph-biudl-integration

| ID | Item | Status | Notes |
|---|---|---|---|
| LGB-001 | Recon Awesome LangGraph, official skills, and current repository architecture | **done** | Existing native orchestration/evidence and Temporal contracts reused |
| LGB-002 | Add repository-native LangGraph orchestration skill | **done** | Official fundamentals/persistence sources pinned by blob SHA |
| LGB-003 | Document BIUDL integration and adapter boundaries | **done** | No duplicate control plane or mandatory dependency |
| LGB-004 | Implement minimal optional Python StateGraph proof with deterministic stub nodes | backlog | Requires approved plan, dependency placement, and runnable test environment |
| LGB-005 | Implement automatic checkpoint recovery + side-effect idempotency proof | backlog | No approval interrupt or human-resume path; must select/test recovery backend |
| LGB-006 | Extend existing OrchestratorTracer / ATES bridge with a versioned graph-event contract | backlog | Current schema has six event kinds and no node identity; add allowlisted fields + privacy tests; do not repurpose ACTION-EFFECT-EVENT |
| LGB-007 | Compare native manager vs LangGraph treatments on same MVT cohort | backlog | Require task fingerprints, equal validation, cost/time/outcome measures |
| LGB-008 | Run current-SHA dual gates and promote verified slice | backlog | Do not equate PR creation or queued checks with validation |
| LGB-009 | Build the competitive orchestration treatment portfolio and benchmark corpus | **specified** | See COMPETITION-MATRIX.md; native control, LangGraph, Deep Agents, Agent Framework, Agents SDK, ADK, LlamaIndex, CrewAI, PydanticAI, swarm/handoff, and hybrid |
| LGB-010 | Synthesize and test hybrid patterns from independently validated strengths | backlog | Preserve attribution, authority boundaries, rollback, and no self-promotion |
| LGB-011 | Define autonomous escalation tiers, triggers, and authority invariants | **specified** | See AUTONOMOUS-ESCALATION-ORCHESTRATION-PLAN.md; no HITL approval/resume flow |
| LGB-012 | Define typed escalation packet, reason taxonomy, counters, and terminal states | **implemented — validation pending** | Added ESCALATION-PACKET.schema.json, ESCALATION-DECISION.schema.json, and AUTONOMOUS-ESCALATION-POLICY.md; validate schemas and align runtime counters in P2 |
| LGB-013 | Implement deterministic escalation policy and budget controller | **implemented — validation pending** | Pure Python controller in she/recovery/escalation.py; 17 deterministic unit cases; no provider calls or side effects |
| LGB-014 | Implement optional LangGraph escalation treatment | backlog | Bounded graph; no approval interrupts; manager policy remains authoritative |
| LGB-015 | Implement automatic crash recovery, persistence, idempotency, and duplicate suppression | backlog | Temporal/checkpointer ownership decision required |
| LGB-016 | Connect live capability roster, health/quota, and specialist adapters | backlog | No route may dispatch without a real eligible adapter |
| LGB-017 | Implement independent verifier, security lane, arbitration, and containment | backlog | Verifiers cannot authorize or expand permissions |
| LGB-018 | Add privacy-safe escalation telemetry and outcome learning | backlog | Version schemas only for demonstrated gaps |
| LGB-019 | Run expanded competitive escalation benchmark | backlog | Same tasks, tool scopes, budgets, and deterministic verifiers |
| LGB-020 | Shadow/canary rollout, rollback drill, and promotion | backlog | Current-SHA dual gates and measured cohort gains |
