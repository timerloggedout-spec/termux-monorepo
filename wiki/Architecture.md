# Architecture

High-level layout of `timerloggedout-spec/termux-monorepo`.

Visual overview (in-repo): `termux-ecosystem-architecture.html`
(Terminal → ArchWiz / Harmonizer / DeepSeek CLI-TUI / Central Mapper / Multi-Agent → DeepSeek API, local cache, workspace).

Prefer **TOOL_INDEX** + **CONCEPT_INDEX** under `archwiz/` for tool-level truth, and the **ICM system map** under `docs/icm/` for component/impact truth.

## Governance & system map

- Root `CLAUDE.md` — primary collaborator entry (governance, branch rules, dual-gate validation). Root `AGENTS.md` is deleted/deprecated; the retained Linguist-surface copy is `CLAUDE.hum.md`.
- `docs/icm/` — Interpretable Context Methodology system map: shelves `objects/{governance, knowledge, operations, platform}`, processes, effects (first-order impact). Reading protocol: one card, source wins over card.
- Root `README.md` — navigation ladder and subsystem inventory.

## Fleet automation

- Specialist **GitHub App identities** act on the repo, each with its own token bucket and narrow permissions: Collector, Gate (checks), Lifecycle (issues), Publisher (contents/PRs), Reviewer (reviews), Swarm (workflows), CrossReference, RepoStory.
- **Dual-gate CI:** `agentic termux smoke` + `hygiene + portability gate` check-runs gate merges to master.
- Provider command dispatch workflows route build/review work to model providers (Jules, DeepSeek, Gemini and others) under quota allocations (`ops/quota/`).

## Provider plane

### llm_api_hub/

Canonical local model plane: OpenAI-compatible server (`server/app.py`), provider extensions/protocols, clients, schemas. Routing documented in `llm_api_hub/ROUTING.md`. (Renamed from the former `llm-api-hub/`; that directory no longer exists.)

### Legacy / adjacent CLI surfaces

- `deepcli/` — DeepSeek-oriented CLI (sessions, streaming, fork, export); related `deepcli-tui/`, `.deepcli/`, `deepseek-cli/`.
- `multi-ai-cli/` — multi-model CLI surface (session/cookie backends).
- `termux-multi-agent/` — multi-agent orchestration for Termux (provision, run, dashboard, Cedar MCP).
- `cli-synthegration/` — conversation synthesis: branching, export, metrics, Chronos, Cedar bridge.

### archwiz/

ArchWizard — indexing, provenance, recovery indices, automation cockpit.

- Docs: `TOOL_INDEX.md`, `CONCEPT_INDEX.md`, `REFERENCE_HUB.md`, `METHODOLOGY_INDEX.md`, `PROCEDURES.md`, …
- Role: dashboard + pipeline control

## Operations estate (docs/ops/)

- Quota system: `ops/quota/allocations.json` SSOT, allocation planning + weekly refresh automation.
- Provider/dispatch records, connector inventories and audits; fleet logs and AppID profile records.
- Certifications program of record: `docs/ops/CERTIFICATIONS-PROGRAM.md` (ladder in `guides/`).
- Dated point-in-time snapshots live under `docs/ops/archive/`; undated docs at the estate root are operational/living.

## Programs

- **Competitions & challenges:** challenge entries coordinated as a slate (docs/ops records + dedicated entry repos built by the fleet).
- **Proposals system:** `docs/proposals/` — RFP packages under `active/` registered in `registry.yaml` (directory-level), evaluation records under `passes/` carrying their own PASS status.

## Harmonizer, multi-AI, swarm (legacy trees)

| Directory | Role |
|-----------|------|
| `harmonizer-prod_cli/` | Production Harmonizer CLI |
| `harmony_hub/` | Harmony hub integration |
| `commingle-swarm/` | Template / scavenge-only external clone |

## Mapping & workspace

- `central_mapper_v420.py`, `mapper_graph.py`
- `workspace/` (incl. generated llm_map indices — distinct from the hand-maintained ICM map)
- `sandbox/`, `src/`, `bin/`, `config/`

## Notes

- `refTemplates/` holds reference templates/metadata; treat as input material, not a live implementation path.
- Submodules: prefer selective depth-1 updates; avoid recursive `submodule update` by default.

For recovery history and prioritized actions, see the root README and `docs/RECON.md`.
