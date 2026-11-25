# ChatGPT Capability Inventory

**Snapshot:** 2026-11-25  
**Machine entry:** [`ops/capabilities/chatgpt/current.json`](../../ops/capabilities/chatgpt/current.json)  
**Manifest:** [`ops/capabilities/chatgpt/manifest.json`](../../ops/capabilities/chatgpt/manifest.json)  
**Schema:** [`ops/capabilities/chatgpt/session-export.schema.json`](../../ops/capabilities/chatgpt/session-export.schema.json)

## Scope and observed counts

The current ChatGPT session catalog yielded:

| Surface | Count | Evidence |
|---|---:|---|
| Skill descriptors | 571 | `skills__list` |
| Skill source groups | 78 | Distinct source identifiers in skill URIs |
| Callable tool definitions | 4,897 | `ALL_TOOLS` |
| Tool namespaces | 128 | 125 MCP provider namespaces + 3 native host namespaces |

The snapshot stores complete exposed tool descriptions, including argument/output contracts where the host supplies them. Skill entries store exact URI + description metadata; resolve full skill bodies on demand through their listed URIs.

The inventory is session-scoped. Tool exposure records discoverability in this session; account authentication, paid entitlement, provider health, CI availability, Termux availability, and production readiness remain separate evidence dimensions. Plugin-directory search is relevance-based, so this export represents the complete current-session tool surface rather than a global plugin directory census.

## Repository mapping

| External surface | Canonical repository authority | Integration rule |
|---|---|---|
| Skills | `SKILLS.md`, `docs/ops/SKILLS-INVENTORY.md`, `docs/ops/SKILL-DISCOVERY-MATRIX.md`, `.agents/skills/`, `.github/skills/` | Treat the ChatGPT catalog as discovery metadata; repository-local skill files remain policy authority |
| Plugins and connectors | `docs/integrations/registry.json`, `docs/integrations/INTEGRATION-REGISTRY.md` | Register provider observations and lifecycle separately |
| Adapter behavior | `docs/integrations/ADAPTER-CONTRACT.md` | Use bounded provider adapters, read-only defaults, explicit scopes, idempotency, redaction and provenance |
| Normalized observations | `docs/integrations/schemas/integration-event.schema.json` | Emit canonical event envelopes; preserve source IDs and validation status |
| Provider capability vocabulary | `docs/schemas/provider-capabilities.md`, `hub_mcp/policy.py` | Map selected external operations to named local capabilities; preserve approval levels |
| Admission | `docs/security/AGENT-HARNESS-ADMISSION.md` | Record source, version, SHA-256, requested authority, policy rules, admission state and evidence |
| Orchestration | `docs/ops/ORCHESTRATION-CONTRACTS.md`, `docs/ops/ORCHESTRATION-TREATMENT.schema.json`, `docs/ops/ORCHESTRATION-RECEIPT.schema.json` | Treat providers and managers as comparable treatments; keep state, outcome and promotion separate |
| DoE and measurement | `docs/ops/DOE-FAMILY.md`, `docs/ops/DOE-COMPONENT-REGISTRY.md`, `ops/doe/component-registry.json`, `docs/ops/AGENT-THROUGHPUT-METRICS.md`, `she/metrics/agent_throughput.py` | Use selected capability combinations as experimental factors; measure actual task outcomes through existing evidence contracts |
| Historical context | `workspace/llm_map/context_relationships/` | Store exact source references and verified/candidate relationships; keep private discussion bodies out of the graph |

The existing DoE component registry remains focused on repository algorithmic components. This capability inventory is a provider/skill/tool discovery surface, so its factor candidates flow through the existing orchestration-treatment and DoE experiment contracts rather than being misclassified as an algorithmic component.

## DoE mixing candidates

Candidate treatment dimensions for future controlled experiments:

1. Provider namespace / connector family.
2. Skill selection and skill composition.
3. Tool selection and tool-call sequence.
4. Manager/orchestration treatment.
5. Context strategy and evidence-ingestion depth.
6. Approval tier and operation scope.
7. Wait, retry and handoff policy.

Pin the snapshot date, manifest SHA-256, tool/skill IDs, adapter version, task cohort, complexity evidence, budget and execution environment for every experiment. Randomize or block comparable tasks by complexity and task class. Record execution through the canonical event and action/effect contracts; calculate ATES/WTCV/3L0 from observed outcomes. Catalog size, tool availability and model claims remain descriptive metadata, quality scores derive from observed outcomes only.


Each namespace record also maps to the umbrella integration-registry entry, adapter contract and local capability policy. The namespace mapping state is `discovery_indexed`; execution-adapter state remains `unverified` until a named adapter passes admission and runtime validation.

## Lifecycle and authority

`DISCOVERED → MAPPED → ADMISSION_REVIEW → ADAPTER_IMPLEMENTED → TESTED → VALIDATED → PROMOTED`

Current snapshot state: **DISCOVERED + MAPPED**. Individual tools remain candidates until their source/version, permissions, adapter, redaction, idempotency, validation and runtime evidence are recorded. Inventory presence alone grants discovery only.

Use the existing approval policy for external writes, paid inference, deployments, publication, communications and physical-world operations. Keep credential values, prompts, completions, session transcripts and private account records outside the export.

## User-supplied source mapping

| Source | Current mapping | Disposition |
|---|---|---|
| `termux-mcp-project-steward.skill` | `.agents/skills/termux-mcp-project-steward/SKILL.md` | Existing repository skill is authoritative |
| `context-relationship-graph_2.skill` | `.agents/skills/context-relationship-graph/SKILL.md` | Mapped to current repository contract |
| Older `context-relationship-graph.skill` | Same repository skill | Reference-only duplicate |
| Loopy API skill export | Adaptive-wait, adaptive-feedback-cycle and orchestration-treatment skills | Bounded-loop pattern adapted; source remains reference |
| Jules workflow PDF | `docs/ops/AGENT-TEAM-ORCHESTRATION.md` | Candidate research; verify upstream references before adoption |
| Routing, GitLab sync and notation notes | Existing routing, integration and Linguist/Siglary contracts | Source inputs; reconcile against current repository evidence |

SHA-256 values, byte sizes and source dispositions are recorded in the dated machine manifest. The source files themselves remain user-provided inputs.

## Snapshot refresh

1. Capture the current skill catalog and complete tool definitions from the active session.
2. Create a new immutable dated snapshot directory.
3. Recompute SHA-256 values and verify unique skill URIs, unique tool names, namespace counts and chunk totals.
4. Validate the manifest against `session-export.schema.json`.
5. Update `current.json` and the integration registry in the same reviewed change.
6. Re-fetch the final branch SHA and every artifact before classifying the export as validated.

The 2026-11-25 snapshot preserves its original capture identity. Future refreshes create new dated snapshots and retain prior evidence.
