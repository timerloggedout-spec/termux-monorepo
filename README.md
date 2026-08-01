# Monorepo Recovery & RefTemplates Restoration

This README documents the filesystem incident, the recovered state from the repository history, and step-by-step recovery & rebuild actions (includes the refTemplates snapshot). It also includes the git-diff consolidation results I performed and concrete recovery commands.

It further documents the **live projects and directories currently in the codebase** so the recovery cockpit and day-to-day navigation share one root README.

---

## TL;DR
- I inspected the repository history, .gitmodules, archwiz, and workspace/llm_map to gather recovery artifacts.
- Option C (git diffs consolidation) was executed first: I examined recent commits and found multiple restore commits that reintroduced `refTemplates` and related submodules.
- I compiled a consolidated recovery plan (Option B) and embedded the `refTemplates` snapshot (Option A) in this README.
- I created this README in the repo root so it is available as the single recovery cockpit.
- **Expansion:** project inventory of directories present on `master` (deepcli, cli-synthegration, termux-multi-agent, archwiz, harmonizer, etc.) is included below so recovery and live code share one map.

---

## What I inspected (actions taken)
- Listed and read archwiz/ and workspace/llm_map/ directories and index files.
- Retrieved recent commits touching `refTemplates` and the repository branch list.
- Read `.gitmodules` to identify submodules referenced by the monorepo.
- Extracted backup indicators (.bak files and large JSONL indices) available for restoration.

This information was used to run git-diff-style consolidation and create the recovery plan below.

---

## Live projects & directories (currently available on master)

Quick entry map (also in `_Entry+ReadMe.md`):

| What you want to do | Where you start |
|---------------------|-----------------|
| Research a file's history | `archaeo <file>` |
| Check impact before changing | `oracle <file>` |
| Make a change | `dispatch <task>` or `agent-shell run <id>` |
| Validate & promote | `validate_promotion.py` → promote |
| Rebuild indices | `map-build && map-func && fore` |

Architecture overview: `termux-ecosystem-architecture.html` (Terminal → ArchWiz / Harmonizer / DeepSeek CLI-TUI / Central Mapper / Multi-Agent → DeepSeek API, local cache, workspace).

### Core automation & agents

#### `deepcli/`
DeepSeek-oriented CLI (sessions, streaming send, thinking mode, attach, fork, export).

- Entry: `deepcli.py`, `deepapi.py`, `deepseek_proxy.py`
- Supporting: token extraction, PoW solver, WASM (`deepseek.wasm`), patches, `browser-data/`, tests
- Related: `deepcli-tui/` (TUI with conversation tree / fork selection), `.deepcli/`, `deepseek-cli/` (incl. deepterm pointer)

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
Conversation synthesis: branching, export, account/token management, metrics, Chronos, Cedar bridge.

Notable modules: `branch_manager.py`, `conv_branching.py`, `conv_explorer.py`, `conv_export_cli.py`, `account_manager.py`, `token_provider.py`, `live_export.py`, `live_search.py`, `sync_pipeline.py`, `synthegration_index.py`, `backfill_elo.py`, `sprints.py`, `ONBOARDING_PROMPT.txt` / `LOOP_PROMPT.txt`, `Chronos/`, `workspace/`, `metrics/`, `sync/`.

Related: `synthegration-cli/`, `.synthegration/`.

#### `archwiz/`
ArchWizard — indexing, provenance, recovery indices, automation cockpit.

- Docs: `ARCHWIZARD_TASKS.md`, `CONCEPT_INDEX.md`, `METHODOLOGY_INDEX.md`, `PROCEDURES.md`, `DATA_FLOW_MANIFEST.md`, `REFERENCE_HUB.md`, etc.
- Operational: pointer/staging indices, restore helpers, listener/poller/autoexec-style components
- Role: dashboard + pipeline control (see architecture HTML)

### Harmonizer, multi-AI, swarm

| Directory | Role |
|-----------|------|
| `harmonizer-prod_cli/` | Production Harmonizer CLI (unified DeepSeek automation: sessions, export, search, sync) |
| `harmony_hub/` | Harmony hub integration |
| `multi-ai-cli/` | Multi-model CLI surface |
| `commingle-swarm/` | Swarm / multi-agent commingle setup |
| Root scripts | `setup-comingle-swarm.sh`, `upgrade-commingle-swarm.sh`, `deepseek_harmonizer.sh` |

### Projects, exchanges, applied work

| Directory | Role |
|-----------|------|
| `_1-Projects/` | Project tree (`a/`, `b/`); API resources and selective submodule pointers under `b/` |
| `exchanges/` | Exchange / market API related code |
| `appliedSxi/maxc/` | Applied Sxi / Max work |
| `_1-q_f/claude/` | Claude-related workspace |
| `colab-cli/` | Colab CLI tooling |
| `chronos_checkout/export_v1/` | Chronos export artifacts |

### Mapping, workspace, sandbox, environment

| Path | Role |
|------|------|
| `central_mapper_v420.py`, `mapper_graph.py` | Central mapper / graph indexing |
| `workspace/` | Shared workspace (incl. llm_map indices) |
| `sandbox/` | Experimental code |
| `src/`, `bin/`, `config/` | Shared sources, binaries, config |
| `.termux/`, `.vnc/`, `.config/` | Termux / VNC / user config |
| `.zshrc*`, `.bashrc*`, `.p10k.zsh`, `powerlevel10k` | Shell / prompt |
| `patches_backup_20260718/` | Patch backups |
| Root `cleanup-main*.sh`, `deploy-phase-*.sh`, `fix-*.py/sh`, `final_runtime_cleanup.py` | Cleanup, deploy, runtime fixes |

---

## refTemplates — last-known directory snapshot (include B)
The following is the last-known top-2-level snapshot of `~/refTemplates/` from the last 30 days. Use this as the authoritative reference for restoration.

```
refTemplates/
  01_Agent_Runtime/
    frankenterm/
    hermes-agent/
    opencode/
    orca/
    pi_agent_rust/
    senpi/
  02_Memory_Session/
    cass_memory_system/
    coding_agent_session_search/
  03_Agent_Communication/
    mcp_agent_mail_rust/
  04_CedarScript/
    cedarscript-ast-parser-python/
    cedarscript-editor-python/
    cedarscript-grammar/
    cedarscript-mcp/
  05_Safety_Observability/
    destructive_command_guard/
    process_triage/
    rano/
    system_resource_protection_script/
  06_Task_Tracking/
    beads_rust/
    beads_viewer/
  07_Prompt_Context/
    markdown_web_browser/
    source_to_prompt_tui/
    toon_rust/
  08_Swarm_References/
    swarm-ecosystem/
    swarms/
    swarms-rs/
  09_Auth_Networking/
    coding_agent_account_manager/
    openclaw-zero-token/
    rust_proxy/
  10_Infrastructure/
    ntm/
    repo_updater/
  11_Evaluation_Quality/
    Approxination-Benchmark/
    Inverse-Arena/
    ultimate_bug_scanner/
  12_External_Agents/
    AiShell/
    YGK-a/
    brenner_bot/
    lazycodex/
    llm_fallbacks/
    oh-my-openagent/
  13_Third_Party_Refs/
    ChapitoAI-main/
    CloudBooter/
    Termux/
    aadc/
    ffa-brackets/
    openskill.lua/
  14_Plain_Files/
    approxination.txt
    ranking_research-concept-_.txt
  Haven/ (Android app workspace + build artifacts + docs)
  Interpreted-Context-Methdology_fork/ (fork workspace with _core and workspaces)
  ...many other subprojects (see repo inventory for full details)
```

Here's the most recent `tree` 'snapshot' shortly before restoration became necessary:
```
❯ tree -L 2 refTemplates                                   refTemplates                                               ├── 01_Agent_Runtime                                       │   ├── frankenterm                                        │   ├── hermes-agent
│   ├── opencode                                           │   ├── orca
│   ├── pi_agent_rust                                      │   └── senpi
├── 02_Memory_Session                                      │   ├── cass_memory_system
│   └── coding_agent_session_search                        ├── 03_Agent_Communication
│   └── mcp_agent_mail_rust                                ├── 04_CedarScript
│   ├── cedarscript-ast-parser-python                      │   ├── cedarscript-editor-python                          │   ├── cedarscript-grammar
│   └── cedarscript-mcp                                    ├── 05_Safety_Observability                                │   ├── destructive_command_guard                          │   ├── process_triage                                     │   ├── rano                                               │   └── system_resource_protection_script
├── 06_Task_Tracking                                       │   ├── beads_rust
│   └── beads_viewer
├── 07_Prompt_Context
│   ├── markdown_web_browser                               │   ├── source_to_prompt_tui
│   └── toon_rust                                          ├── 08_Swarm_References
│   ├── swarm-ecosystem                                    │   ├── swarms
│   └── swarms-rs                                          ├── 09_Auth_Networking
│   ├── coding_agent_account_manager
│   ├── openclaw-zero-token
│   └── rust_proxy
├── 10_Infrastructure
│   ├── ntm                                                │   └── repo_updater
├── 11_Evaluation_Quality                                  │   ├── Approxination-Benchmark
│   ├── Inverse-Arena
│   └── ultimate_bug_scanner
├── 12_External_Agents                                     │   ├── AiShell
│   ├── YGK-a                                              │   ├── brenner_bot
│   ├── lazycodex                                          │   ├── llm_fallbacks
│   └── oh-my-openagent                                    ├── 13_Third_Party_Refs
│   ├── ChapitoAI-main                                     │   ├── CloudBooter
│   ├── My-Jogyo                                           │   ├── Termux
│   ├── TradingAgents                                      │   ├── aadc
│   ├── assistral                                          │   ├── ffa-brackets
│   ├── insane-search                                      │   └── openskill.lua
├── 14_Plain_Files                                         │   ├── approxination.txt
│   └── ranking_research-concept-_.txt
├── Haven
│   ├── CHANGELOG.md                                       │   ├── EMAIL.md
│   ├── LICENSE
│   ├── NOTICE-Fonts.md                                    │   ├── PRIVACY_POLICY.md                                  │   ├── README.md
│   ├── RELEASE.md                                         │   ├── VISION.md
│   ├── app                                                │   ├── build-ffmpeg                                       │   ├── build-proot                                        │   ├── build.gradle.kts                                   │   ├── core                                               │   ├── dev                                                │   ├── docs                                               │   ├── fastlane
│   ├── feature                                            │   ├── gradle
│   ├── gradle.properties                                  │   ├── gradlew
│   ├── gradlew.bat                                        │   ├── integration-tests
│   ├── metadata                                           │   ├── rclone-android
│   ├── rdp-kotlin                                         │   ├── scratch
│   ├── scripts                                            │   ├── settings.gradle.kts
│   └── tools                                              ├── Interpreted-Context-Methdology
│   ├── CLAUDE.md                                          │   ├── LICENSE
│   ├── README.md                                          │   ├── _core
│   └── workspaces
├── Interpreted-Context-Methdology_fork
│   ├── CLAUDE.md
│   ├── LICENSE
│   ├── README.md
│   ├── _core                                              │   └── workspaces                                         ├── OpenWebUI-Monitor                                      │   ├── AGENTS.md                                          │   ├── Dockerfile                                         │   ├── LICENSE                                            │   ├── README.md
│   ├── app                                                │   ├── components
│   ├── components.json                                    │   ├── docker-compose.yml                                 │   ├── drizzle.config.ts                                  │   ├── eslint.config.mjs
│   ├── hooks                                              │   ├── i18n.config.ts
│   ├── locales                                            │   ├── middleware.ts                                      │   ├── next.config.js                                     │   ├── package.json                                       │   ├── pnpm-lock.yaml
│   ├── pnpm-workspace.yaml                                │   ├── postcss.config.js
│   ├── postcss.config.mjs                                 │   ├── resources
│   ├── scripts                                            │   ├── start.sh
│   ├── tailwind.config.ts                                 │   └── tsconfig.json
├── _TOOL_TAXONOMY -> /data/data/com.termux/files/home/workspace/llm_map/_TOOL_TAXONOMY
├── agent-c                                                │   ├── Makefile
│   ├── README.md                                          │   ├── SPEC.md
│   ├── agent.c                                            │   └── preview.webp
├── audio-preprocess
│   ├── LICENSE                                            │   ├── README.md
│   ├── README.zh.md                                       │   ├── fap-complete.zsh                                   │   ├── fish_audio_preprocess
│   ├── pyproject.toml                                     │   └── tools                                              ├── better-clawd                                           │   ├── PERFORMANCE.md                                     │   ├── README.md                                          │   ├── bun.lock
│   ├── package.json                                       │   ├── schemas
│   ├── scripts                                            │   ├── src
│   └── tsconfig.json
├── big-AGI
│   ├── AGENTS.md -> CLAUDE.md
│   ├── CLAUDE.md                                          │   ├── Dockerfile
│   ├── LICENSE
│   ├── README.md
│   ├── app                                                │   ├── docker-compose.yaml
│   ├── docs                                               │   ├── eslint.config.mjs
│   ├── kb                                                 │   ├── middleware_BASIC_AUTH.ts
│   ├── next.config.ts                                     │   ├── package-lock.json                                  │   ├── package.json                                       │   ├── pages
│   ├── public                                             │   ├── src                                                │   ├── tools                                              │   └── tsconfig.json
├── cc-mirror                                              │   ├── AGENTS.md                                          │   ├── CHANGELOG.md
│   ├── CLAUDE.md
│   ├── CONTRIBUTING.md                                    │   ├── DESIGN.md
│   ├── LICENSE
│   ├── README.md                                          │   ├── docs
│   ├── eslint.config.js                                   │   ├── lefthook.yml
│   ├── package-lock.json                                  │   ├── package.json                                       │   ├── scripts                                            │   ├── src
│   └── tsconfig.json                                      ├── ccs
│   ├── AGENTS.md -> CLAUDE.md                             │   ├── CHANGELOG.md
│   ├── CLAUDE.md
│   ├── CONTRIBUTING.md
│   ├── LICENSE                                            │   ├── README.md
│   ├── SECURITY.md                                        │   ├── assets
│   ├── bun.lock                                           │   ├── bunfig.toml
│   ├── commitlint.config.cjs                              │   ├── config
│   ├── docker                                             │   ├── docs
│   ├── eslint-rules                                       │   ├── eslint.config.mjs
│   ├── macos-bar                                          │   ├── package.json
│   ├── scripts                                            │   ├── src
│   ├── tsconfig.json                                      │   └── ui
├── colab-ssh                                              │   ├── CHANGELOG.md
│   ├── CODE_OF_CONDUCT.md
│   ├── CONTRIBUTING.md
│   ├── LICENSE
│   ├── MANIFEST.in                                        │   ├── Makefile                                           │   ├── README.md
│   ├── build.sh
│   ├── colab_ssh
│   ├── docs                                               │   ├── publish.sh
│   ├── requirements.dev.txt
│   ├── requirements.txt                                   │   └── setup.py
├── colabcode                                              │   ├── LICENSE                                            │   ├── Makefile                                           │   ├── README.md                                          │   ├── colab_starter.ipynb
│   ├── colabcode                                          │   ├── requirements.txt
│   ├── scripts
│   └── setup.cfg
├── colabsh
│   ├── CODE_OF_CONDUCT.md
│   ├── CONTRIBUTING.md
│   ├── Dockerfile
│   ├── LICENSE                                            │   ├── README.md                                          │   ├── cliff.toml
│   ├── codecov.yml
│   ├── docs                                               │   ├── info_checks
│   ├── pyproject.toml
│   ├── src
│   ├── uv.lock
│   └── zensical.toml
├── colabtools
│   ├── CONTRIBUTING.md
│   ├── LICENSE
│   ├── MANIFEST.in
│   ├── README.md                                          │   ├── google                                             │   ├── jupyter-config
│   ├── notebooks                                          │   ├── setup.cfg
│   └── setup.py
├── conduit                                                │   ├── AGENTS.md
│   ├── CLAUDE.md -> AGENTS.md                             │   ├── LICENSE                                            │   ├── PRIVACY_POLICY.md                                  │   ├── README.md                                          │   ├── analysis_options.yaml                              │   ├── android
│   ├── assets                                             │   ├── cargokit_options.yaml
│   ├── devtools_options.yaml                              │   ├── docs
│   ├── ios                                                │   ├── l10n.yaml
│   ├── pigeons                                            │   ├── pubspec.lock
│   ├── pubspec.yaml
│   ├── scripts                                            │   └── tool
├── deep_intel.txt                                         ├── deep_recon.sh                                          ├── fast_intel.txt                                         ├── fast_scan.sh
├── final_intel.json                                       ├── fish-audio-python
│   ├── CHANGELOG.md                                       │   ├── CONTRIBUTING.md
│   ├── LICENSE                                            │   ├── README.md                                          │   ├── pyproject.toml
│   ├── release-please-config.json                         │   ├── scripts
│   ├── src                                                │   └── uv.lock
├── flywheel_intel.txt                                     ├── gemini_recon
│   ├── Gemini-API                                         │   ├── gemini-web-to-api
│   ├── gemini-web2api
│   └── reverse_gemini-cli
├── google-colab-cli                                       │   ├── AGENTS.md
│   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md                                    │   ├── LICENSE
│   ├── README.md                                          │   ├── cloudbuild.yaml
│   ├── docs                                               │   ├── integration
│   ├── pyproject.toml                                     │   ├── skills
│   ├── src                                                │   └── uv.lock
├── hermes-agent                                           │   ├── AGENTS.md
│   ├── CONTRIBUTING.es.md                                 │   ├── CONTRIBUTING.md
│   ├── Dockerfile
│   ├── LICENSE
│   ├── MANIFEST.in
│   ├── README.es.md
│   ├── README.md                                          │   ├── README.ur-pk.md
│   ├── README.zh-CN.md                                    │   ├── SECURITY.es.md
│   ├── SECURITY.md                                        │   ├── acp_adapter
│   ├── acp_registry
│   ├── agent                                              │   ├── batch_runner.py
│   ├── cli-config.yaml.example                            │   ├── cli.py                                             │   ├── constraints-termux.txt
│   ├── cron                                               │   ├── datagen-config-examples                            │   ├── docker
│   ├── docker-compose.windows.yml                         │   ├── docker-compose.yml
│   ├── docs                                               │   ├── flake.lock                                         │   ├── flake.nix                                          │   ├── gateway
│   ├── hermes                                             │   ├── hermes-already-has-routines.md
│   ├── hermes_bootstrap.py                                │   ├── hermes_cli
│   ├── hermes_constants.py                                │   ├── hermes_logging.py
│   ├── hermes_state.py                                    │   ├── hermes_time.py
│   ├── locales                                            │   ├── mcp_serve.py
│   ├── mini_swe_runner.py                                 │   ├── model_tools.py
│   ├── nix                                                │   ├── package-lock.json
│   ├── package.json                                       │   ├── packaging
│   ├── plugins
│   ├── providers                                          │   ├── pyproject.toml
│   ├── run_agent.py                                       │   ├── scripts
│   ├── setup-hermes.sh                                    │   ├── setup.py
│   ├── skills                                             │   ├── tools
│   ├── toolset_distributions.py                           │   ├── toolsets.py                                        │   ├── trajectory_compressor.py
│   ├── tui_gateway
│   ├── ui-tui
│   ├── utils.py                                           │   ├── uv.lock
│   └── web                                                ├── hermes-agent-self-evolution
│   ├── PLAN.md                                            │   ├── README.md                                          │   ├── datasets
│   ├── evolution
│   ├── generate_report.py
│   └── pyproject.toml
├── hermes-webui
│   ├── AGENTS.md                                          │   ├── ARCHITECTURE.md
│   ├── BUGS.md                                            │   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md                                    │   ├── CONTRIBUTORS.md                                    │   ├── DESIGN.md                                          │   ├── Dockerfile
│   ├── LICENSE                                            │   ├── README.md
│   ├── ROADMAP.md
│   ├── SPRINTS.md                                         │   ├── TESTING.md
│   ├── THEMES.md                                          │   ├── api                                                │   ├── bootstrap.py
│   ├── ctl.sh                                             │   ├── docker-compose.three-container.yml
│   ├── docker-compose.two-container.yml
│   ├── docker-compose.yml
│   ├── docker_init.bash                                   │   ├── docs                                               │   ├── eslint.runtime-guard.config.mjs                    │   ├── mcp_server.py
│   ├── package.json                                       │   ├── pyproject.toml                                     │   ├── pytest.ini
│   ├── requirements-dev.txt                               │   ├── requirements.txt
│   ├── scripts                                            │   ├── server.py
│   ├── start.ps1                                          │   ├── start.sh
│   ├── static
│   └── uv.lock
├── inventory_deep.py
├── inventory_repos.py                                     ├── move_log.txt
├── openrouter-deep-research-mcp
│   ├── AGENTS.md
│   ├── BEFORE_AFTER.md
│   ├── CHANGELOG.md
│   ├── CLAUDE.md
│   ├── CONTEXT.md                                         │   ├── Dockerfile                                         │   ├── LICENSE
│   ├── PLAN.md                                            │   ├── README.md
│   ├── RESILIENCE_IMPROVEMENTS.md
│   ├── TEST-RESULTS.md
│   ├── THEME_UPDATE.md
│   ├── ZERO.json
│   ├── ZERO.md
│   ├── agents.code-workspace
│   ├── check_db.js                                        │   ├── config.js
│   ├── docs
│   ├── extension
│   ├── find_query.js
│   ├── harnesses                                          │   ├── package.json                                       │   ├── research_outputs
│   ├── scripts
│   ├── skills
│   ├── src
│   ├── templates
│   ├── test-client.js
│   ├── test-input.json                                    │   ├── test-layout.js
│   ├── test-perplexity.js                                 │   ├── test-planning.js                                   │   └── test-resilience.sh                                 ├── openrouter-rs
│   ├── AGENTS.md                                          │   ├── CHANGELOG.md
│   ├── CLAUDE.md                                          │   ├── CONTRIBUTING.md
│   ├── Cargo.lock
│   ├── Cargo.toml
│   ├── LICENSE                                            │   ├── MIGRATION.md
│   ├── README.md
│   ├── SECURITY.md                                        │   ├── SUPPORT.md
│   ├── crates                                             │   ├── docs
│   ├── justfile                                           │   ├── openspec
│   ├── scripts                                            │   ├── specs                                              │   └── src
├── perfect_trunk_cc-mirror
│   ├── HEAD                                               │   ├── config                                             │   ├── description                                        │   ├── hooks
│   └── info                                               ├── pi
│   ├── AGENTS.md
│   ├── CONTRIBUTING.md                                    │   ├── LICENSE
│   ├── README.md                                          │   ├── SECURITY.md
│   ├── biome.json                                         │   ├── package-lock.json                                  │   ├── package.json
│   ├── packages                                           │   ├── pi-test.bat                                        │   ├── pi-test.ps1
│   ├── pi-test.sh                                         │   ├── scripts
│   ├── test.sh                                            │   ├── tsconfig.base.json
│   └── tsconfig.json                                      ├── quick_intel.txt
├── quick_recon.sh                                         ├── recon.py
├── recon.sh                                               ├── recon_lag.py
├── recon_v2.sh                                            ├── repo_intel.txt
├── repo_inventory.json                                    ├── repo_inventory_deep.json
├── reverser_ai                                            │   ├── LICENSE
│   ├── README.md                                          │   ├── __init__.py
│   ├── example_config.toml                                │   ├── plugin.json
│   ├── requirements.txt                                   │   ├── reverser_ai
│   ├── scripts                                            │   └── setup.py                                           ├── revert.sh                                              ├── starship                                               │   ├── AI_POLICY.md                                       │   ├── CHANGELOG.md                                       │   ├── CODE_OF_CONDUCT.md
│   ├── CONTRIBUTING.md                                    │   ├── Cargo.lock
│   ├── Cargo.toml                                         │   ├── LICENSE
│   ├── README.md                                          │   ├── SECURITY.md
│   ├── build.rs                                           │   ├── clippy.toml
│   ├── crowdin.yml                                        │   ├── deny.toml
│   ├── docs                                               │   ├── install
│   ├── media                                              │   ├── release-please-config.json
│   ├── src                                                │   ├── starship.exe.manifest
│   └── typos.toml
├── surgical_intel.txt
├── surgical_recon.sh
└── trunk_builder.py

219 directories, 327 files                                 ~ ❯                                               15:05:53
```

> Note: Many entries above correspond to external git repositories or local workspaces and were sometimes included as submodules or as nested repositories. **Existing refTemplates were depth-1 selective sparse-checkout of relevant files, with metadata only** — not full recursive checkouts.

---

## Results of Option C — Git diffs consolidation (what I found)
I inspected recent commits touching `refTemplates` and surrounding restore commits. Key commits (chronological recent → oldest):

- Commit: b104890bbc0c25c8c152c089cbfb7153e2bddca7
  - Message: Restore refTemplates and codex blobs from d5814d9 (clone method)
  - Changes: Removed a small set of subproject pointers inside `refTemplates` (these were submodule pointers removed in this commit):
    - refTemplates/01_Agent_Runtime/deepcode-cli (subproject removed)
    - refTemplates/01_Agent_Runtime/hermes-agent (subproject removed)
    - refTemplates/07_Prompt_Context/Interpreted-Context-Methdology (removed)
    - refTemplates/07_Prompt_Context/Interpreted-Context-Methdology_fork (removed)
    - refTemplates/13_Third_Party_Refs/assistral (removed)
    - refTemplates/15_Reverse_Engineering/AIStudio2API (removed)
    - refTemplates/15_Reverse_Engineering/AIStudioProxy (removed)
    - refTemplates/15_Reverse_Engineering/AIstudioProxyAPI (removed)
    - refTemplates/15_Reverse_Engineering/gemini-cli-api (removed)
  - Interpretation: A consolidation step removed some submodule commit placeholders (subproject commit lines). It likely converted some nested submodules into direct restored content or intentionally removed stale submodule pointers after restoration.

- Commit: 8a53ffb84fe0e3f8dbce070480b2327946a435c8
  - Message: Restore refTemplates and codex blobs from d5814d9
  - Interpretation: Preceding restore attempt that added files back from a backup or other commit (d5814d9 is referenced as the backup source in commit messages).

- Commit: 416a9cd1fc9ff1c3a46f364f79b23535bf0920ca
  - Message: Complete restore: all files from backup commit d5814d9
  - Interpretation: Earlier full restore from a backup commit.

- Commit: 65c9f81162fd9a080a4a8aea4f6a0b6ecd2dcd72
  - Message: Complete restore: refTemplates, submodules, and powerlevel10k
  - Interpretation: This commit explicitly mentions submodules and powerlevel10k (powerlevel10k is referenced in `.gitmodules`). The reflog of commits suggests the repo author performed staged restores across a short time window to reconstruct the environment.

- `.gitmodules` (current repo content): contains submodule entries for several projects, notably `powerlevel10k` and other project submodules.

Summary: The repo history shows active restoration attempts — multiple commits rehydrated `refTemplates` from a backup commit (d5814d9 referenced). Later consolidation removed some explicit submodule pointers, possibly because content was restored directly or those submodules were intentionally removed. The state on `master` represents the consolidated result of these operations.

---

## .gitmodules & checkout notes
The repo `.gitmodules` lists several submodules. Important entries:
- `_1-Projects/b/a_resources/api/bnc/BSC_log` → https://github.com/ksasemada/BSC_log.git
- `_1-Projects/b/a_resources/api/yobit/Yobit-WebSocket` → https://github.com/ksasemada/Yobit-WebSocket.git
- `_1-Projects/b/a_resources/sig-scan/kucoin-buy-detector` → https://github.com/ksasemada/kucoin-buy-detector.git
- `_1-Projects/b/eggshell` → https://github.com/neoneggplant/eggshell
- `deepseek-cli/deepterm` → https://github.com/karjok/deepterm.git
- `powerlevel10k` → https://github.com/romkatv/powerlevel10k.git

**Clarification (do not treat recursive submodule update as the default path):**  
Existing **refTemplates** material was managed as **depth-1 selective sparse-checkout of relevant files, with metadata only**. Full `git submodule update --init --recursive` is **rare** and usually unnecessary. Prefer sparse/depth-1 patterns and the indices under `archwiz/` / `workspace/` when restoring reference material. Initialize or update an individual submodule only when you explicitly need that project (e.g. powerlevel10k or a listed `_1-Projects/b/...` entry).

---

## Option B — Recovery plan and prioritized actions (executable)
Follow this plan to restore the comprehensive environment. This is actionable and ordered by safety and recovery impact.

1) Snapshot current state
```bash
# from repo root
git status --porcelain
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD > /tmp/repo-head.sha
mkdir -p /tmp/repo-backups && tar -czf /tmp/repo-backups/termux-monorepo-$(date +%Y%m%dT%H%M%S).tgz .
```

2) Submodules — selective only (not recursive by default)
```bash
git submodule status
# Only if you need a specific listed submodule, e.g.:
# git submodule update --init --depth 1 -- powerlevel10k
# Prefer depth-1 / sparse patterns consistent with how refTemplates were checked out.
```

3) Recreate the `refTemplates` tree from git history if needed
```bash
# find commit that contained refTemplates
git log --all --pretty=format:'%H %ad %s' --date=iso -- refTemplates | head -n 50
# checkout the tree from a known good commit (replace <commit> with the commit sha found)
git checkout <commit> -- refTemplates
# commit the restored tree if it looks correct
git add refTemplates
git commit -m "Restore refTemplates from <commit>"
```
If git checkout fails because refTemplates was a submodule pointer, try the backup-restore commits already present (see commits listed above). The repository already contains restore commits; inspect files under refTemplates to confirm content is present. Prefer depth-1 selective sparse-checkout of relevant files (metadata only) rather than full recursive population.

4) Use archwiz and llm_map indices to fill gaps
- Many indices are present in: `archwiz/pointer_index.json`, `archwiz/index_registry.json`, `workspace/llm_map/*_index*.jsonl`.
- These indices can guide file reconstruction and identify missing files.

Example commands:
```bash
# inspect pointer index and staging blocks
jq 'keys | length' archwiz/pointer_index.json || true
less archwiz/staging_blocks.json
# use restore helper
python3 archwiz/restore_version.py --from archwiz/staging_blocks.json --to refTemplates/
```

5) Reinstall dotfiles & environment items broken by pip/zsh reinitialization
- Reinstall `powerlevel10k` only if needed, then re-run dotfile install scripts.
```bash
# selective, depth-1 if you need the theme
git submodule update --init --depth 1 -- powerlevel10k
# follow your dotfiles install (example)
./install-dotfiles.sh  # or the documented dotfile install command in repo
```

6) Rebuild crucial indices after files are restored
- Provenance
```bash
cd cli-synthegration/workspace/provenance
python3 final_provenance.py
python3 comprehensive_fast.py
```
- LLM map (big; may be slow)
```bash
cd workspace/llm_map
python3 build_all.py   # or the smaller targeted build scripts: build_llm_index.py, build_final_all.py
```

7) Validate environment
- Run small smoke tests for each workspace (e.g., deepcli `./deepcli.py send --dry-run`) and run `termux-multi-agent` test runs locally.
- Check that `refTemplates/*` items are present and that scripts referencing them can find paths.

---

## Safety & Secrets
- The repo includes references to `cookies_2.json` and browser cookie exports; DO NOT commit secrets. If `cookies_2.json` is present locally, ensure it is in `.gitignore`.
- Back up large JSONL indices externally before attempting destructive rebuilds.

---

## What I can do next (pick one or more)
1. Run selective submodule / sparse-checkout steps and report results (I can run commands only if you ask me to perform GitHub write operations or environment commands; I can provide exact commands for you to run).
2. Page through archwiz and workspace/llm_map to list every `.bak` file and recommend the highest-confidence restoration candidates.
3. Commit this README into `master` (I am about to do this now). If you want a different branch, tell me.
4. Create an automated PR that applies the recommended recovery script(s) (I can open issues/PRs if you want).

---

## Audit trail of the consolidation I performed (Option C results summary)
- Located and read these recent commits on `master`:
  - b104890bbc0c25c8c152c089cbfb7153e2bddca7 — "Restore refTemplates and codex blobs from d5814d9 (clone method)"
  - 8a53ffb84fe0e3f8dbce070480b2327946a435c8 — "Restore refTemplates and codex blobs from d5814d9"
  - 416a9cd1fc9ff1c3a46f364f79b23535bf0920ca — "Complete restore: all files from backup commit d5814d9"
  - 65c9f81162fd9a080a4a8aea4f6a0b6ecd2dcd72 — "Complete restore: refTemplates, submodules, and powerlevel10k"
  - ee1807049fd93d087bc14055b2ae6cbffb5dbf82 — "Add base configs and dotfiles"
  - ebe3e0ca504cb35ef61832b0b1b1576a1a0d44fb — "Initial monorepo commit..."

- Found `.gitmodules` with multiple submodule URLs — use **selective depth-1** updates only when a listed submodule is needed; refTemplates historically used sparse depth-1 checkout with metadata only.
- Found evidence that some restored content was then consolidated and had submodule pointers removed in the latest commit; verify that removed submodules are intentionally removed (or re-add them via git submodule add if needed).

---

If you confirm, I will push this README into `master` (the repository's default branch) and then proceed to Option B step 2 (list .bak files and large indices and produce a prioritized file-by-file recovery plan). If you prefer to run commands yourself first, I will provide a runnable script you can execute.
