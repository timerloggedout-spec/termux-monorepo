# termux-monorepo

Termux-oriented monorepo for a unified DeepSeek automation environment: multi-agent orchestration, conversation synthesis, indexing/provenance (ArchWiz), Harmonizer CLI, and supporting tooling.

See also: `_Entry+ReadMe.md` (quick command map) and `termux-ecosystem-architecture.html` (architecture diagram).

---

## Quick entry points

| Goal | Start here |
|------|------------|
| Research a file's history | `archaeo <file>` |
| Check impact before changing | `oracle <file>` |
| Make a change | `dispatch <task>` or `agent-shell run <id>` |
| Validate & promote | `validate_promotion.py` → promote |
| Rebuild indices | `map-build && map-func && fore` |
| DeepSeek chat CLI | `deepcli/` → `./deepcli.py` |
| Multi-agent on Termux | `termux-multi-agent/` → `run.py` / `provision_agent.py` |
| Conversation export / branch / sync | `cli-synthegration/` |
| Indexing, provenance, cockpit | `archwiz/` |

---

## Live project directories (what is in the tree now)

### Core automation & agents

#### `deepcli/`
DeepSeek-oriented CLI (sessions, streaming send, thinking mode, attach, fork, export).

- Entry: `deepcli.py`, `deepapi.py`, `deepseek_proxy.py`
- Supporting: token extraction, PoW solver, WASM (`deepseek.wasm`), patches, `browser-data/`, tests
- Related: `deepcli-tui/` (TUI with conversation tree / fork selection), `.deepcli/`, `deepseek-cli/` (incl. deepterm pointer)

Example usage (from `deepcli/README.md`):

```bash
./deepcli.py new
./deepcli.py send "Explain quantum computing"
./deepcli.py send "Write a Python script" --thinking
./deepcli.py list
./deepcli.py history --session <session_id>
./deepcli.py export --format json --output chat.json
./deepcli.py fork --session <source_id> --message-id <msg_id>
```

#### `termux-multi-agent/`
Multi-agent orchestration for Termux: provision, run, patch, dashboard, Cedar MCP.

| Path | Role |
|------|------|
| `provision_agent.py` | Agent provisioning |
| `run.py` / `run_agent.sh` | Run loop |
| `dashboard.py` | Status / control UI |
| `patch_files.py` / `patch_files_final.py` | Patch application |
| `cedar-mcp-server.js` | CedarScript MCP server |
| `config/`, `templates/`, `src/`, `workspace/` | Config, templates, sources, workspaces |
| `run_history.jsonl` | Run history |
| `sgconfig.yml` | ast-grep / scanner config |

#### `cli-synthegration/`
Conversation synthesis layer: branching, export, account/token management, metrics, Chronos, Cedar bridge.

Notable modules: `branch_manager.py`, `conv_branching.py`, `conv_explorer.py`, `conv_export_cli.py`, `account_manager.py`, `token_provider.py`, `live_export.py`, `live_search.py`, `sync_pipeline.py`, `synthegration_index.py`, `backfill_elo.py`, `sprints.py`, `ONBOARDING_PROMPT.txt` / `LOOP_PROMPT.txt`, `Chronos/`, `workspace/`, `metrics/`, `sync/`.

Related: `synthegration-cli/`, `.synthegration/`.

#### `archwiz/`
ArchWizard — indexing, provenance, recovery indices, automation cockpit.

- Docs: `ARCHWIZARD_TASKS.md`, `CONCEPT_INDEX.md`, `METHODOLOGY_INDEX.md`, `PROCEDURES.md`, `DATA_FLOW_MANIFEST.md`, `REFERENCE_HUB.md`, etc.
- Operational: pointer/staging indices, restore helpers, listener/poller/autoexec style components (see architecture HTML)
- Role in ecosystem: dashboard + pipeline control (listener, poller, AutoExec)

### Harmonizer, multi-AI, swarm

| Directory | Role |
|-----------|------|
| `harmonizer-prod_cli/` | Production Harmonizer CLI (unified DeepSeek automation; sessions, export, search, sync) |
| `harmony_hub/` | Harmony hub integration |
| `multi-ai-cli/` | Multi-model CLI surface |
| `commingle-swarm/` | Swarm / multi-agent commingle setup |
| Root scripts | `setup-comingle-swarm.sh`, `upgrade-commingle-swarm.sh`, `deepseek_harmonizer.sh` |

### Projects, exchanges, applied work

| Directory | Role |
|-----------|------|
| `_1-Projects/` | Project tree (`a/`, `b/`); includes API resources and selective submodule pointers under `b/` |
| `exchanges/` | Exchange / market API related code |
| `appliedSxi/maxc/` | Applied Sxi / Max work |
| `_1-q_f/claude/` | Claude-related workspace |
| `colab-cli/` | Colab CLI tooling |
| `chronos_checkout/export_v1/` | Chronos export artifacts |

### Mapping, workspace, sandbox

| Path | Role |
|------|------|
| `central_mapper_v420.py`, `mapper_graph.py` | Central mapper / graph indexing |
| `workspace/` | Shared workspace (incl. llm_map indices referenced by recovery tooling) |
| `sandbox/` | Experimental / sandbox code |
| `src/`, `bin/`, `config/` | Shared sources, binaries, config |
| `ast_js.json`, `ast_py.json` | AST snapshots |

### Environment, Termux, patches

| Path | Role |
|------|------|
| `.termux/`, `.vnc/`, `.config/` | Termux / VNC / user config |
| `.zshrc*`, `.bashrc*`, `.p10k.zsh` | Shell / prompt config |
| `powerlevel10k` | Submodule (prompt theme) |
| `patches_backup_20260718/` | Patch backups |
| Root `cleanup-main*.sh`, `deploy-phase-*.sh`, `fix-*.py/sh`, `final_runtime_cleanup.py` | Cleanup, deploy, runtime fixes |

---

## Ecosystem picture (from `termux-ecosystem-architecture.html`)

```
Terminal (user)
  ├── ArchWiz          — dashboard / automation cockpit (listener, poller, AutoExec)
  ├── Harmonizer CLI   — unified DeepSeek automation (sessions, export, search, sync)
  ├── DeepSeek CLI/TUI — interactive chat + persistent dashboard
  ├── Central Mapper   — filesystem indexing, AST, bloat detection, provenance
  └── Multi-Agent      — refactoring engine + CedarScript MCP
         ↓
  DeepSeek API · Local storage/session cache · Workspace files
```

---

## Submodules & refTemplates (important)

`.gitmodules` lists a small set of submodules:

- `_1-Projects/b/a_resources/api/bnc/BSC_log`
- `_1-Projects/b/a_resources/api/yobit/Yobit-WebSocket`
- `_1-Projects/b/a_resources/sig-scan/kucoin-buy-detector`
- `_1-Projects/b/eggshell`
- `deepseek-cli/deepterm`
- `powerlevel10k`

**Do not assume** `git submodule update --init --recursive` is the normal path for this monorepo.

Historical **refTemplates** content was managed as **depth-1 selective sparse-checkout of relevant files, with metadata only** — not full recursive submodule checkouts. Full submodule recursion is rare and usually unnecessary. Prefer sparse/depth-1 patterns and the indices under `archwiz/` / `workspace/` when restoring reference material.

---

## Recovery notes (appendix)

An earlier recovery-focused README documented a filesystem incident and restore commits that rehydrated `refTemplates` from backup commit `d5814d9`, plus consolidation that removed some nested subproject pointers. That recovery content is retained only as history:

- Prefer the live directory inventory above for day-to-day navigation.
- For restore work: use `archwiz` pointer/staging indices and existing restore helpers; avoid blanket recursive submodule updates unless you explicitly need one of the listed submodules.
- Secrets (e.g. cookie exports): never commit; keep out of tree / in `.gitignore`.

---

## Safety

- Do not commit API tokens, cookie dumps, or browser session exports.
- Large JSONL indices and `.bak` files may be operational state; back them up before destructive rebuilds.
