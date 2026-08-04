# Architecture

High-level layout of `timerloggedout-spec/termux-monorepo`.

Visual overview (in-repo): `termux-ecosystem-architecture.html`  
(Terminal → ArchWiz / Harmonizer / DeepSeek CLI-TUI / Central Mapper / Multi-Agent → DeepSeek API, local cache, workspace).

Prefer **TOOL_INDEX** + **CONCEPT_INDEX** under `archwiz/` for tool-level truth.

## Core automation & agents

### deepcli/

DeepSeek-oriented CLI (sessions, streaming send, thinking mode, attach, fork, export).

- Entry: `deepcli.py`, `deepapi.py`, `deepseek_proxy.py`
- Related: `deepcli-tui/`, `.deepcli/`, `deepseek-cli/`

### termux-multi-agent/

Multi-agent orchestration for Termux: provision, run, patch, dashboard, Cedar MCP.

| Path | Role |
|------|------|
| `provision_agent.py` | Agent provisioning |
| `run.py` / `run_agent.sh` | Run loop |
| `dashboard.py` | Status / control UI |
| `patch_files.py` | Patch application |
| `cedar-mcp-server.js` | CedarScript MCP server |

### cli-synthegration/

Conversation synthesis: branching, export, account/token management, metrics, Chronos, Cedar bridge.

### archwiz/

ArchWizard — indexing, provenance, recovery indices, automation cockpit.

- Docs: `TOOL_INDEX.md`, `CONCEPT_INDEX.md`, `REFERENCE_HUB.md`, `METHODOLOGY_INDEX.md`, `PROCEDURES.md`, …
- Role: dashboard + pipeline control

## Harmonizer, multi-AI, swarm

| Directory | Role |
|-----------|------|
| `harmonizer-prod_cli/` | Production Harmonizer CLI |
| `harmony_hub/` | Harmony hub integration |
| `multi-ai-cli/` | Multi-model CLI surface |
| `commingle-swarm/` | Template / scavenge-only external clone |

## Mapping & workspace

- `central_mapper_v420.py`, `mapper_graph.py`
- `workspace/` (incl. llm_map indices)
- `sandbox/`, `src/`, `bin/`, `config/`

## Notes

- `refTemplates/` on `master` is largely a stub; full metadata skeleton lives on `recreate/refTemplates-skeleton`.
- Submodules: prefer selective depth-1 updates; avoid recursive `submodule update` by default.

For recovery history and prioritized actions, see the root README and `docs/RECON.md`.
