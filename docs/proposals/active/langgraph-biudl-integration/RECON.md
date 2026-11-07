# RECON — awesome-LangGraph × termux-monorepo

**Date:** 2026-11-06 (America/Los_Angeles)  
**Initial recon snapshot:** `master` at `94e674c9a334fc1bdda8fe3ec96d7db5bc4b3cb9`  
**PR merge base / current base SHA:** `9376c8bee386022f90dd7a6407ad1664d2c6ecf1` (verified by GitHub compare; branch is 10 commits ahead, 0 behind)  
**External source:** [vonzosten/awesome-LangGraph](https://github.com/vonzosten/awesome-LangGraph)  
**Official skills:** [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills)

## 1. Source characterization

The Awesome list describes itself as a lifecycle index for building, observing, evaluating, and deploying stateful tool-using agents. At inspection it was public, not archived, CC0-1.0, with 2,038 stars / 297 forks; last repository push observed 2026-10-15 (README blob `e54d875ae645a03100346e2997acb8cfc43b0a14`). It includes LangChain, LangGraph, Deep Agents, LangSmith, official packages, community applications, integrations, research projects, security/governance references, and starter templates. Stars/forks are discovery signals, not quality evidence.

LangGraph capabilities surfaced by the source include state persistence/checkpointing, durable graph execution, streaming, interrupts, time travel, memory, subgraphs, testing, and observability. The index is a discovery surface; inclusion is not a production-readiness or security endorsement.

## 2. Best directly relevant SKILL.md files

The official `langchain-ai/langchain-skills` repository contains a directly applicable core trio, plus evaluation and lifecycle companions:

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
- `she/observability/orchestrator_trace.py` and `scripts/ci/bridge_ates_trace_to_events.py` already provide a privacy-preserving trace boundary and a bridge to the six-event ATES schema; the bridge hashes labels and omits raw context.
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


## 7. Additional official skills and version posture

A second pass over the official skills catalog expanded the best-fit set:

- `ecosystem-primer` (blob `88bc543c9a73c850ee507ec4b7fd09653f066d32`) should run first to select between LangChain, LangGraph, Deep Agents, or a hybrid.
- `langgraph-cli` (blob `b63b16e9882e1a2533ddb92a70e4c4cc98415b03`) covers scaffold/dev/build/up/deploy and `langgraph.json`; cloud deployment remains approval-gated and is not part of this slice.
- `langgraph-python-quickstart` (blob `89aab024205b2bdfc6102f5bfd44141a65dd2ba7`) and `langgraph-typescript-quickstart` (blob `9b756b39b3adc67d4d245078b59a97e08ba33de7`) are only for explicitly requested new-project quickstarts.
- `deep-agents-core` (blob `841dbd59b4f0012ccf7d99fec3590ae5c3b119fb`) and `deep-agents-orchestration` (blob `fbd57c8a1f163e8fac73765837d5bc427a4d63e6`) are adjacent alternative-layer skills, not LangGraph core skills.

The upstream skills README identifies the collection as early development and warns that APIs/content may change. The repository-native skill therefore pins source blobs and requires live API inspection before coding.

PyPI reported `langgraph==1.2.20` as the latest stable release on 2026-11-06, MIT licensed, Python `>=3.10`; the release wheel SHA-256 is `2b9fd01c3d5e0652e6c9b436dc0341413788010eb279ac8c46a733cf485d848b`. PyPI showed no provenance attestation for the release files. This is a version observation only: no package was installed and no project dependency was added. Re-verify release metadata and provenance before LGB-004.


## 8. Source-level corrections from candidate README inspection

The initial broad shortlist was refined by reading the selected repositories themselves:

- **Supervisor package:** `langchain-ai/langgraph-supervisor-py` is archived/read-only (2026-09-20) and its README recommends tool-based supervisor patterns for most new use cases; do not adopt it as a dependency.
- **MCP adapters:** `langchain-ai/langchain-mcp-adapters` is archived/read-only (2026-09-17); MCP support moved into `langchain[mcp]` / `langchain.mcp`; do not add the old package.
- **Swarm ledger:** `Mediaeater/swarm-at-ledger` describes SHA-256 hash chaining and independent verification, but states its sample ledger data is synthetic, not real agent interactions. Study integrity mechanics only.
- **Open SWE:** its README labels it actively developing and says correctness, stability, and compatibility are not guaranteed. Treat as architecture research, not production base.
- **Open Deep Research:** its visible README update notes are from 2025; keep as reference pending fresh maintenance and dependency checks.
- **Official swarm:** `langchain-ai/langgraph-swarm-py` is a candidate for handoff patterns, but adoption must be tested against the native manager baseline.
- **APort guardrails:** interesting pre-action authorization approach, but self-reported CTF results are not independent validation. Require adversarial testing before adoption.

These findings materially change selection: prefer direct tool-based supervisor patterns, use the maintained MCP integration path, and keep community security/ledger projects in the research tier.


## 9. Existing telemetry bridge — exact compatibility boundary

The existing `OrchestratorTracer` and `bridge_ates_trace_to_events.py` are a strong starting point, not a blank-slate implementation. The bridge accepts exactly six kinds (`task_started`, `task_completed`, `tool_call`, `tool_retry`, `handoff`, `active_window`), validates timestamps/status/duration/SHA, hashes task/role/tool labels, and omits raw fingerprints and payloads.

The current throughput schema is closed and does not represent graph name/version, node name, transition ID, checkpoint/thread fingerprint, or span parentage. Therefore:
- graph-level task lifecycle and genuine tool/handoff events can be adapted now where semantics match;
- arbitrary node transitions cannot be silently relabeled as tools;
- `ACTION-EFFECT-EVENT.schema.json` is specifically for review/comment-to-commit follow-through and is not a generic graph action ledger;
- graph-specific spans require an explicit schema extension and privacy tests in LGB-006.
