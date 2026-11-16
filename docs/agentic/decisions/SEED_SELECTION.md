# Seed Selection Decisions

**Status:** Recommendations only. No repository dependency, submodule pointer, workflow, or external integration is changed by these records.

## Decision 1 — CAMSHAFT: advisory adapter candidate

| Field | Decision |
|---|---|
| **Disposition** | Adapter candidate after reproducible dependency provenance is established. |
| **Extract** | YAML/JSON bulk plan grammar; stable task IDs; typed dependency links; atomic validation-first import; critical-path and parallel-group advisory results. |
| **Do not extract** | Automatic dispatch, execution authority, completion state, or current local-path dependency layout. |
| **Evidence** | `README.md`, `src/commands/bulk.rs`, `tests/cli_tests.rs`, and `Cargo.toml` in the Camshaft fork. |
| **Blocker** | `gantt_ml = { path = "../GanttML" }`; isolated build/reproducibility is unresolved. |
| **Next evidence gate** | Pin/review GanttML provenance, build in isolation, then pass plan-fixture parity tests. |

## Decision 2 — ICM ARCHITECT and ICM METHODOLOGY: retain as governing reference seeds

| Field | Decision |
|---|---|
| **Disposition** | Continue as shallow pinned reference inputs; no additional runtime use. |
| **Extract** | Explicit stage contracts, human check points, canonical artifacts, output-as-edit-surface, one-way dependencies, and filesystem-visible state. |
| **Do not extract** | Folder existence as implementation completion proof; unbounded folder restructuring. |
| **Evidence** | `SKILL.md` in ICM Architect and `README.md` / conventions in the full methodology fork. |
| **Next evidence gate** | Verify the proposed dependency plan makes every phase’s inputs, outputs, and human evidence clear in a cold-read walk test. |

## Decision 3 — CONTENT-AGENT-ROUTING: phase-envelope policy seed

| Field | Decision |
|---|---|
| **Disposition** | Retain as a pinned context-routing reference. |
| **Extract** | Lean routing files, section-level context loading, canonical sources, and one-way dependency direction. |
| **Do not extract** | Content-operation-specific schemas, broad prompt stuffing, or copied planning state in agent comments. |
| **Evidence** | `README.md`, `CLAUDE.md`, and `CONTEXT.md` in the routing fork. |
| **Next evidence gate** | Review generated phase-dispatch prompt against a context allow-list and plan hash. |

## Decision 4 — GANTT-CLI and GANTTLESS: derived projection patterns only

| Field | gantt-cli | Ganttless |
|---|---|---|
| **Disposition** | Pattern extraction | Pattern extraction |
| **Extract** | Parent-roll-up and schedule projection ideas | Compact deterministic ASCII timeline output |
| **Do not extract** | Numeric position-derived task IDs | Any dependency/eligibility inference |
| **Evidence** | `src/main.rs` | `README.md`, `src/ganttless.rs` |
| **Next evidence gate** | Stable ID adapter preserves phase ID across reorder | Canonical plan renders repeatably without mutation |

## Decision 5 — GANTTY, GANTT-CHART-CODE, MONTT, AND ICM CCTV: retain outside the core path

| Candidate | Disposition | Rationale | Reconsider only when |
|---|---|---|---|
| GanTTY | Reference only | Useful dependency-selection and criticality UI patterns; GPL-3.0, pickle persistence, and interactive terminal loop make it unsuitable for the control plane. | A local non-CI terminal editor is intentionally scoped. |
| Gantt-Chart-Code | Pattern extraction | Hierarchy reconstruction from flat records is useful; no dependency scheduler or mature CLI contract. | A reliable flat import source is chosen. |
| Montt | Defer | Risk/forecast ideas are interesting, but custom DSL and a zero-return sampling stub make it premature. | Core phase flow is stable and forecast accuracy is a verified need. |
| ICM CCTV | Reference only | Good local visual/checkpoint pattern; renderer is optional and localhost-oriented. | A human wants a local visual board after textual reports prove insufficient. |

## Global no-go rules

No selected seed is allowed to determine phase readiness, dispatch an agent, merge a pull request, close a proposal, infer human approval, or update a submodule pointer. The repository-native plan and objective GitHub evidence remain authoritative.
