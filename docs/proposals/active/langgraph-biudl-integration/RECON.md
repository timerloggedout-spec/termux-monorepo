# RECON — awesome-LangGraph × termux-monorepo

**Date:** 2026-11-06 (America/Los_Angeles)  
**Repository base observed:** `master` at `94e674c9a334fc1bdda8fe3ec96d7db5bc4b3cb9`  
**External source:** [vonzosten/awesome-LangGraph](https://github.com/vonzosten/awesome-LangGraph)  
**Official skills:** [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills)

## 1. Source characterization

The Awesome list describes itself as a lifecycle index for building, observing, evaluating, and deploying stateful tool-using agents. It includes LangChain, LangGraph, Deep Agents, LangSmith, official packages, community applications, integrations, research projects, security/governance references, and starter templates.

LangGraph capabilities surfaced by the source include state persistence/checkpointing, durable graph execution, streaming, interrupts, time travel, memory, subgraphs, testing, and observability. The index is a discovery surface; inclusion is not a production-readiness or security endorsement.

## 2. Best directly relevant SKILL.md files

The official `langchain-ai/langchain-skills` repository contains a directly applicable trio:

| Rank | Skill | Why it is useful | Integration rule |
|---|---|---|---|
| 1 | `langgraph-fundamentals` | StateGraph, typed state, nodes/edges, reducers, Command, Send, invoke/stream, errors | Mandatory before any LangGraph code |
| 2 | `langgraph-human-in-the-loop` | interrupt/resume, approval flow, checkpoint requirements, node re-execution/idempotency | Mandatory for approval or pause/resume |
| 3 | `langgraph-persistence` | Checkpointers, thread IDs, Store, state history, subgraph checkpoint scope | Mandatory for persistence/memory/history |

Source files and immutable blob SHAs are recorded in the repository-native LangGraph skill. We adapt rather than wholesale-copy upstream material.

The upstream skill README also distinguishes LangGraph from Deep Agents: LangGraph is the fine-grained graph runtime; Deep Agents is the higher-level harness for planning, filesystem context, subagents, skills, and memory. This distinction informs framework selection.

## 3. High-value projects from the Awesome index

| Candidate | Potential value | Disposition |
|---|---|---|
| Official `langgraph-supervisor` / `langgraph-swarm` | Hierarchical and swarm coordination patterns | Compare as treatments; do not replace native manager policy |
| `langchain-mcp-adapters` | MCP tool interoperability | Evaluate against existing MCP catalog/foundry adapters |
| `deepagents` | Planning, context/filesystem, subagents, skills, long-term memory | Use when higher-level harness features close a demonstrated gap |
| `open_deep_research` | Multi-source research workflow | Reference for research-lane architecture and evaluation |
| `open-swe` | Asynchronous coding-agent pattern | Reference for long-running software engineering task orchestration |
| `langgraph-cli` | Local development/scaffolding/deployment lifecycle | Optional developer tool; not a runtime dependency |
| `aport-agent-guardrails`, `sidclawhq/platform`, `pic-standard` | Pre-action authorization and provenance patterns | Security research only pending independent threat-model, license, and enforcement review |

The initial integration does not clone, fork, vendor, submodule, install, or deploy any candidate.

## 4. Existing repository fit

Live repository search and source reads found:

- `CLAUDE.md` defines BIUDL = Broad → Integrate → Validate → Develop → Learn, FA-ADE, proposal scope, dual gates, adaptive WAIT, and promotion policy.
- `docs/ops/ORCHESTRATION-CONTRACTS.md` already defines four layers, canonical lifecycle, identity, treatments, receipts, adapters, and security boundaries.
- `ORCHESTRATION-TREATMENT.schema.json` and `ORCHESTRATION-RECEIPT.schema.json` already provide the comparison and receipt contracts.
- `docs/ops/TEMPORAL-LANGSMITH-ADAPTER.md` already documents optional Temporal self-host + LangSmith trajectories, with OTEL/ATES remaining canonical.
- `docs/ops/SKILLS-INVENTORY.md`, `SKILLS.md`, and `docs/ops/SKILL-DISCOVERY-MATRIX.md` are the skill discovery/index surfaces.
- Existing adaptive-wait, adaptive-feedback-cycle, evidence-led, review, context-relationship, and production-reconciliation skills already cover lifecycle and evidence operations.

Therefore the right integration is a thin optional LangGraph treatment/adapter and project-specific skill, not a second orchestration or observability system.

## 5. Architectural distinctions

- LangGraph checkpoint state is graph-local execution state; it is not canonical project evidence.
- Temporal remains the cross-worker durable execution substrate when needed.
- GitHub remains authoritative for repository refs, PRs, checks, workflow runs, jobs, and artifacts.
- OTEL/ATES/evidence envelope/action-effect records remain the sanitized measurement/provenance plane.
- Existing provider and MCP adapters remain the credential and tool authority.
- LangGraph interrupt approval must follow repository human-only permission boundaries; a graph node is not an approval grant.

## 6. Open questions for the runtime slice

- Python-only first, or dual Python/TypeScript support?
- Where should the optional dependency be declared without burdening Termux core?
- Which checkpointer backend can be exercised in CI and Termux without persistent secret-bearing state?
- Which graph lifecycle events can be emitted without raw prompts, completions, tool payloads, or checkpoint data?
- What existing manager treatment is the baseline for an equivalent cohort?

These are explicitly assigned to LGB-004 through LGB-007 rather than silently answered by this documentation slice.
