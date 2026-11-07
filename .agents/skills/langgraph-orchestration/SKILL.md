---
name: langgraph-orchestration
description: "Design, implement, test, and evaluate LangGraph workflows in termux-monorepo. Use when building stateful graph orchestration, multi-agent fan-out, routing, resumable approvals, graph persistence, streaming, or LangGraph-to-Temporal/ATES adapters."
---

# LangGraph Orchestration — BIUDL integration skill

Use this skill when a task genuinely benefits from explicit graph control flow. It adapts official LangChain/LangGraph guidance to the repository's BIUDL, FA-ADE, proposal, evidence, and security contracts.

## Required repository context

Load, in order and only as needed:

1. `CLAUDE.md` — BIUDL, proposal authorization, dual gates, promotion.
2. `docs/proposals/registry.yaml` and `docs/proposals/active/langgraph-biudl-integration/ITEMS.md` — authorized scope.
3. `docs/ops/ORCHESTRATION-CONTRACTS.md` — canonical orchestration identity, state, receipt, and adapter boundaries.
4. `docs/ops/AGENT-TEAM-ORCHESTRATION.md` — manager/team optimization.
5. `.agents/skills/adaptive-wait/SKILL.md`, `.agents/skills/adaptive-feedback-cycle/SKILL.md`, `.agents/skills/context-relationship-graph/SKILL.md`, and `.github/skills/production-reconciliation/SKILL.md` when the task touches their domains.
6. The upstream layer-specific LangGraph skill below before writing LangGraph code.

## BIUDL execution

| BIUDL phase | LangGraph work | Required evidence |
|---|---|---|
| **Broad** | Recon the existing manager, task, workflow, provider, memory, and telemetry surfaces. Select graph use only where explicit branching, fan-out, state, or pause/resume is valuable. | Current source paths, proposal item, alternatives considered |
| **Integrate** | Design state schema, nodes, edges, reducers, persistence, interrupt points, and adapter seams. Keep provider calls behind existing interfaces. | Graph diagram, state contract, treatment descriptor |
| **Validate** | Test node behavior, routing, reducers, fan-out aggregation, checkpoint/resume, idempotency, and failure classes. Run the graph under a deterministic fixture. | Focused tests, graph run receipt, expected/observed transition set |
| **Develop** | Integrate only the validated slice. Preserve repository dual gates and current-SHA evidence. | PR, checks, tests, action/effect evidence |
| **Learn** | Record outcomes, latency, retries, tool delay, context cost, useful parallel yield, and attribution in existing ATES / evidence contracts. Compare orchestration treatments on equivalent cohorts. | Receipt, outcome classification, longitudinal evidence |

## When to use LangGraph

Prefer LangGraph when the workflow needs one or more of:

- explicit conditional or cyclic control flow;
- parallel fan-out and deterministic aggregation;
- a state machine spanning multiple agent/tool steps;
- checkpointed pause/resume or state inspection;
- streaming intermediate state or progress;
- composable subgraphs with separately testable contracts.

Prefer the existing direct CLI/tool path for simple linear tasks. Prefer Deep Agents when the primary need is a ready-made planning, filesystem, skills, or subagent harness. Prefer Temporal when the primary requirement is durable cross-process / cross-worker execution, scheduling, and replay across worker failure. LangGraph can run inside a Temporal Activity; it does not replace Temporal's durable execution boundary.

## Official upstream skill set

The canonical upstream source is [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills). Its README currently labels the collection early-development and warns that APIs and skill content may change. Pin source blobs and re-check before implementation.

### Framework selection and core graph implementation

| Skill | Load when | Pinned source blob |
|---|---|---|
| `ecosystem-primer` | **First** for any LangChain/LangGraph/Deep Agents project; choose the correct layer and next skill | `88bc543c9a73c850ee507ec4b7fd09653f066d32` |
| `langgraph-fundamentals` | Any LangGraph code: StateGraph, state, nodes, edges, Command, Send, invoke, streaming, errors | `adf7bff81897aa99d9505195a1196fced6047b97` |
| `langgraph-human-in-the-loop` | Interrupts, approval, validation, pause/resume, recoverable errors | `d762f2a170c30310b5641642af3e19ce7866a28a` |
| `langgraph-persistence` | Checkpointers, thread identity, cross-thread Store, history/time travel, subgraph checkpoint scope | `bbcf0ea77bf2b374a99e5d08cae147c12da03e82` |

### Optional project lifecycle skills

| Skill | Load when | Pinned source blob |
|---|---|---|
| `langgraph-python-quickstart` | A minimal new Python graph project is explicitly requested | `89aab024205b2bdfc6102f5bfd44141a65dd2ba7` |
| `langgraph-typescript-quickstart` | A minimal new TypeScript graph project is explicitly requested | `9b756b39b3adc67d4d245078b59a97e08ba33de7` |
| `langgraph-cli` | Scaffold, local dev, build, Docker Compose, or deployment lifecycle | `b63b16e9882e1a2533ddb92a70e4c4cc98415b03` |

### Evaluation skill for BIUDL / MVT

| Skill | Load when | Pinned source blob |
|---|---|---|
| `eval-engineering` | Design/audit agent benchmark tasks, harnesses, verifiers, controlled runs, calibration, or continuous benchmark maintenance | `c62557a7250cd2c3cf1ef5a8ea50fe97ddfcac3b` |

This is not a LangGraph runtime skill. Use it as a companion to the repository's existing MVT/DoE and ATES contracts; retain independent deterministic verifiers and do not replace repository-specific experiment governance.

### Adjacent alternative: Deep Agents

| Skill | Load when | Pinned source blob |
|---|---|---|
| `deep-agents-core` | Planning, filesystem context, skills, memory, and subagent harness are more valuable than hand-authored graph control flow | `841dbd59b4f0012ccf7d99fec3590ae5c3b119fb` |
| `deep-agents-orchestration` | Deep Agents subagent delegation, task planning, or HITL is selected | `fbd57c8a1f163e8fac73765837d5bc427a4d63e6` |

Read the source SKILL.md and its language reference from the pinned upstream repository before code changes. Do not copy an entire upstream skill into this repository; retain provenance and adapt only the invariants needed by this project.

- Ecosystem primer: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/ecosystem-primer
- Fundamentals: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-fundamentals
- Human-in-the-loop: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-human-in-the-loop
- Persistence: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-persistence
- CLI: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-cli
- Python quickstart: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-python-quickstart
- TypeScript quickstart: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-typescript-quickstart
- Evaluation engineering: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/eval-engineering
- Deep Agents core: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/deep-agents-core
- Deep Agents orchestration: https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/deep-agents-orchestration
- Upstream catalog: https://github.com/langchain-ai/langchain-skills

## Graph design contract

1. Draw the graph before implementation. Every node must have a single responsibility and explicit inputs/outputs.
2. Define a typed state schema. Return partial state updates; do not mutate the shared state object in place.
3. Define reducers for accumulated fields. In fan-out graphs, parallel result fields must have an explicit reducer and stable task identity; never rely on last-write-wins for concurrent results.
4. Use static edges for deterministic transitions, conditional edges for routing, `Command` when a node must update state and route, and `Send` for dynamic fan-out.
5. Treat `Command` routing and static edges as additive: if both are configured from a node, both paths may execute. Test the actual transition set.
6. Every cycle must have a named continuation/termination condition, bounded iteration or a provable exit, and an observable terminal state.
7. Compile the builder before invocation. Pin library/API versions in the owning dependency manifest when a runtime dependency is approved; inspect the installed API rather than relying on remembered signatures.
8. Use the project's established model/provider adapters. A graph is an orchestration strategy, not a new credential or provider-routing authority.

## Persistence and replay

- Use a stable, opaque `thread_id` for every checkpointed execution; do not derive it from secrets or expose user-identifying content.
- In-memory checkpointers are for tests/development only. Select a production backend through an explicit proposal and data-retention/security review; PostgreSQL is a candidate, not an automatic dependency.
- Keep graph checkpoint state separate from canonical repository evidence. Checkpoints may contain prompts, messages, tool arguments, or user data and are therefore not eligible for Git, ordinary artifacts, ATES JSONL, or public receipts.
- Use LangGraph checkpoint history for graph-local debugging/replay. Use GitHub SHA, workflow run/job/step/artifact IDs, and the repository evidence envelope for project provenance.
- If Temporal is present, use Temporal workflow history as the durable cross-worker execution record and map only sanitized identifiers/events into the repository evidence plane.

## Human approval and side effects

- Use `interrupt()` only with a checkpointer and the same stable `thread_id` on resume.
- Resume with `Command(resume=...)`; do not substitute a normal input dict for a resume command.
- The node restarts from its beginning on resume. Place side effects after the interrupt where possible; otherwise make them idempotent (upsert / check-before-create) and test duplicate prevention.
- Human approval is not a generic escape hatch. Follow `docs/proposals/AGENTIC-PERMISSIONS.md` for credential, production, financial, privacy, and destructive edges.
- Never infer approval from a graph reaching an approval node, a model response, a timeout, or a missing interrupt result.

## Error, retry, and loop policy

Classify errors before retrying:

| Class | Treatment |
|---|---|
| Transient network / rate limit | Bounded retry with backoff and attempt evidence |
| Tool failure recoverable by agent | Return a typed tool error and allow one policy-bounded recovery route |
| Missing human input / approval | Interrupt and wait; preserve checkpoint identity |
| Validation / contract failure | Fail closed; route to repair or terminal failure |
| Unexpected exception | Surface failure with traceback reference in restricted logs; do not silently convert to success |

Retries must be informative, bounded, idempotent, and represented as distinct attempts. Do not hide failures behind graph loops. A loop that makes no measurable progress becomes `stagnated`, not success.

## Observability and ATES adapter

Start from the existing `she/observability/orchestrator_trace.py` and `scripts/ci/bridge_ates_trace_to_events.py`; do not create a competing trace pipeline.

The current bridge accepts only these ATES event kinds: `task_started`, `task_completed`, `tool_call`, `tool_retry`, `handoff`, and `active_window`. It hashes free-text task/role/tool labels and omits raw context and fingerprints. Preserve those privacy semantics.

Current contract boundaries:

- `AGENT-THROUGHPUT-EVENT.schema.json` is closed (`additionalProperties: false`) and has no graph/node/transition fields. Map graph-run start/completion and actual tool/handoff events only when their semantics match an allowed event. Do not mislabel every graph node as a `tool_call`.
- `ORCHESTRATION-RECEIPT.schema.json` and `EVIDENCE-ENVELOPE.schema.json` can carry sanitized graph-run-level state/outcome and SHA-bound provenance using their existing fields.
- `ACTION-EFFECT-EVENT.schema.json` currently models issue comments/reviews and their later commit follow-through. It is not a generic graph-node event ledger; do not repurpose it.
- Graph/node-level spans (graph version, node identity, transition, trace/span parentage, checkpoint/thread fingerprint) require an explicit versioned schema extension and privacy tests under LGB-006 before export.

Never export prompts, completions, message bodies, arbitrary graph state, tool payloads, secrets, tokens, checkpoint blobs, or raw user content. Do not invent a second trace schema or score.

For parallel work, record fan-out count, completed/failed workers, useful accepted outputs, merge conflicts, duplicate effort, and integration outcome only when the current schema can represent them. Extend the schema before emitting unrepresentable dimensions. `parallel yield` is not simply worker count.

## Testing contract

At minimum, cover:

- graph compiles and completes the happy path;
- every conditional route and terminal branch;
- reducer behavior under multiple parallel updates;
- duplicate / missing / out-of-order event handling;
- bounded loop termination and retry ceilings;
- interrupt pause + same-thread resume;
- side-effect idempotency across resume/replay;
- persistence behavior under the selected checkpointer;
- sanitized telemetry schema and absence of raw state;
- failure classification and non-success terminal states.

Use deterministic stub nodes and fixtures for structural tests. Keep provider/model calls out of unit tests. Run the focused suite, then the repository gates:

```bash
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

Report commands actually run; never claim a gate passed from its existence or queued status.

## External ecosystem shortlist

The source index [vonzosten/awesome-LangGraph](https://github.com/vonzosten/awesome-LangGraph) is a discovery catalogue, not an endorsement or dependency manifest. Highest-value candidates to evaluate selectively:

- `langgraph-swarm-py`: official handoff/swarm implementation; evaluate only as a bounded treatment against the native manager, with explicit attribution and useful-yield measurements.
- `langgraph-supervisor-py`: **archived/read-only since 2026-09-20; do not adopt**. Its README recommends the supervisor pattern directly via tools for most new use cases.
- `langchain-mcp-adapters`: **archived/read-only since 2026-09-17; do not adopt**. MCP support moved into `langchain[mcp]` / `langchain.mcp`. Reconcile with the existing MCP adapter/foundry boundary before using the replacement.
- `deepagents`: higher-level harness for planning, context/filesystem, subagents, skills, and memory; use only where built-ins solve a demonstrated gap.
- `open-swe`: Deep Agents-based software factory reference, but its README explicitly warns it is under active development and correctness/stability/compatibility are not guaranteed.
- `open_deep_research`: research workflow reference; its README's visible update notes are from 2025, so verify maintenance and provider compatibility before reuse.
- `Mediaeater/swarm-at-ledger`: hash-chain/audit pattern worth studying, but its README says its ledger records are synthetic seed data, not real agent interactions. Do not treat it as external fleet evidence.
- `aporthq/aport-agent-guardrails`: promising pre-action authorization research; independently verify threat model, bypass resistance, enforcement placement, test corpus, maintenance, and license before integration.
- `ac12644/langgraph-starter-kit`: community starter-kit reference only; inspect current dependencies, test coverage, and security before extraction.

No repository forks, vendoring, submodules, dependencies, provider credentials, or deployments are created by reading this shortlist.

## Completion and promotion

Use the existing lifecycle:

`RECON → PLAN → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

Keep `COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` independent. LangGraph cannot self-approve, self-merge, or override repository promotion policy.

## Competitive evaluation and pattern synthesis

For comparative or best-approach work, load `docs/proposals/active/langgraph-biudl-integration/COMPETITION-MATRIX.md` before selecting a framework. Treat the native manager as the control and LangGraph, Deep Agents, swarm/handoff, supervisor-style routing, and hybrid compositions as separate treatments.

- Freeze the task corpus, verifier, permissions, model/provider configuration, and resource budget before comparing treatments.
- Compare equivalent tasks and report quality, reliability, latency, cost, governance, operability, and maintainability separately; do not rank on one blended score.
- Any hard safety, privacy, authorization, or evidence-integrity failure disqualifies a treatment regardless of speed.
- Extract patterns as keep / adapt / combine / defer / reject. Combine only independently validated patterns with compatible state and authority boundaries.
- Preserve source attribution, adaptation rationale, benchmark evidence, rollback path, and upgrade watch for every adopted pattern.
- The manager retains treatment-selection authority. A candidate cannot approve, score, or promote itself.
- An inconclusive experiment retains the native control; a single successful demo is not promotion evidence.