# Project Remote Sandbox Workspace Setup Considerations:
```Gemini-GoogleSearch
To run a Termux environment on an Ubuntu/Linux desktop or server for sandbox testing, you cannot run the exact Termux Android app natively. You must instead replicate its specific Android-based Linux environment (environment variables, paths, and package manager) using containerization, virtualization, or architectural simulation tools.
Here are the best ways to achieve this, ranked from the most lightweight to the most authentic.
## Docker Container (Most Lightweight)
You can run a Docker container that simulates the Termux environment by mirroring its unique paths and packaging layout.

* Official Termux Docker Image: The Termux project provides an official [termux/termux-docker](https://github.com/termux/termux-docker) repository.
* The Architecture: It runs an Ubuntu base but sets up the /data/data/com.termux/files/usr prefix to match an Android installation.
* The Command:

docker run -it termux/termux-docker

* Pros: Starts instantly, uses minimal resources, and matches the file hierarchy perfectly.
* Cons: Runs on your host CPU architecture (usually x86_64). If your target device is an ARM-based phone, compiled binaries won't behave exactly the same way unless you run Docker through qemu-user-static.

## Anbox / Waydroid (Native Android Containerization)
If you want to run the actual Termux .apk file natively on Linux without a full emulator, use a container-based Android runtime.

* Waydroid: This is the modern, highly recommended standard for Linux. It runs a full Android system image inside a Linux container (LXC) directly on your kernel.
* Installation: Install Waydroid via your package manager, initialize the Android image, and drop the Termux APK right into it.
* Pros: Near-native performance, zero virtualization overhead, and behaves exactly like a real Android device.
* Cons: Requires a Wayland desktop environment (or a nested Wayland compositor like Weston if you are on X11).

## Android Studio Emulator (Most Accurate)
If you need to test Android 14+ permissions, background restrictions, awake locks, or severe device constraints, use the official Android Virtual Device (AVD).

* Setup: Install Android Studio on Ubuntu, open the Device Manager, and create a system image (preferably with Google Play Store to easily install tools, or download the F-Droid Termux APK).
* Pros: Perfect hardware emulation, accurate API lifecycle testing, and complete control over battery, thermal, and network states.
* Cons: Very heavy on RAM and CPU, requires KVM acceleration enabled on Ubuntu.

## Quick Comparison for Sandbox Testing

* Choose Docker if you just need to test scripts, compilation pipelines, or CLI tools using Termux prefixes.
* Choose Waydroid if you need to test inter-app interactions on Linux with high performance.
* Choose Android Studio AVD if you need to debug low-level Android system constraints, lifecycle crashes, or awake lock stability.

Which aspect of your Termux workspace are you looking to test first: CLI script compatibility, network listeners, or Android-specific background constraints?
```
° Termux specific considerations.
° Termux is the Target Environment 🥇
-->> Mobile 🥇 Priority
  -->> _THEN_ other environments.
## Check all existing code PR's merged since initialization against the Termux Environment.

## PRIORITY - Establish Baselines; Standards (use Termux Official Docs as well); Reconciliation of potential drift (like: hardcoded PATHS).

## Develop Workflow for the `termux-smoke`, perpetual branch; and, or delegate to Agents with code spaces or access to them (like @Jules 'Render' Workspaces access; others have access to the same or similar ++>> Add to Roster Considerations).

## _***HIGH PRIORITY***_ INTIALIZE: `https://github.com/marketplace/render`
Already Installed!

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
- **Navigation:** prefer ArchWiz indices over a two-link “Entry + HTML” pair — see **Navigation SSOT** below and `docs/RECON.md` on `feature/recon-intel-and-nav`.

---

## Navigation SSOT (better than Entry + HTML alone)

Use this ladder when orienting in the tree. `_Entry+ReadMe.md` and `termux-ecosystem-architecture.html` remain useful but are **not** the primary map.

| Priority | Start here | What you get |
|----------|------------|--------------|
| 1 | `archwiz/TOOL_INDEX.md` | 28 tools / 7 categories — cockpit, forensic, autonomous, verification |
| 2 | `archwiz/CONCEPT_INDEX.md` | Concepts + status (built / reserved / not built) + feature backlog |
| 3 | `archwiz/REFERENCE_HUB.md` | Links to DATA_FLOW_MANIFEST, SYSTEM_MAP, func/llm indices |
| 4 | `archwiz/METHODOLOGY_INDEX.md` | Approaches tried, failures, what stuck |
| 5 | `archwiz/PROCEDURES.md`, `ARCHWIZARD_TASKS.md` | Runbooks and active tasks |
| 6 | `docs/RECON.md` (this RECON) | Branch/PR critique, refTemplates nesting gaps, prioritized proposals |
| 7 | `replit.md` on branch `critical-proposal` (PR #1) | Critical path/config issues and optimization proposals |
| 8 | `_Entry+ReadMe.md` | One-line command → entry table |
| 9 | `termux-ecosystem-architecture.html` | Visual ecosystem diagram |
| 10 | `refTemplates/README_RECOVERY.md` on `recreate/refTemplates-skeleton` | Metadata-only restore policy for refs |
| 0.1 | `workspace/*.md` `workspace/CAVEMAN_INDEX.md` `workspace/SYSTEM_MAP.md` `workspace/llm_map/{*.md,*.txt,*.json,*.jsonl}` | Full Ecosystem Mapping |

Quick command table (also in `_Entry+ReadMe.md`):

| What you want to do | Where you start |
|---------------------|-----------------|
| Research a file's history | `archaeo <file>` |
| Check impact before changing | `oracle <file>` |
| Make a change | `dispatch <task>` or `agent-shell run <id>` |
| Validate & promote | `validate_promotion.py` → promote |
| Rebuild indices | `map-build && map-func && fore` |
| Open cockpit | `python3 archwiz/archwiz.py` |

---

## What I inspected (actions taken)
- Listed and read archwiz/ and workspace/llm_map/ directories and index files.
- Retrieved recent commits touching `refTemplates` and the repository branch list.
- Read `.gitmodules` to identify submodules referenced by the monorepo.
- Extracted backup indicators (.bak files and large JSONL indices) available for restoration.

This information was used to run git-diff-style consolidation and create the recovery plan below.

---

## Live projects & directories (currently available on master)

Architecture overview: `termux-ecosystem-architecture.html` (Terminal → ArchWiz / Harmonizer / DeepSeek CLI-TUI / Central Mapper / Multi-Agent → DeepSeek API, local cache, workspace). Prefer **TOOL_INDEX** + **CONCEPT_INDEX** for tool-level truth.

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

- Docs: `ARCHWIZARD_TASKS.md`, `CONCEPT_INDEX.md`, `METHODOLOGY_INDEX.md`, `PROCEDURES.md`, `DATA_FLOW_MANIFEST.md`, `REFERENCE_HUB.md`, `TOOL_INDEX.md`, etc.
- Operational: pointer/staging indices, restore helpers, listener/poller/autoexec-style components (**poller/listener = legacy**; canonical path is cache-write → `dispatch_pipeline` — see PR #1 / `replit.md`)
- Role: dashboard + pipeline control

### Harmonizer, multi-AI, swarm

| Directory | Role |
|-----------|------|
| `harmonizer-prod_cli/` | Production Harmonizer CLI (unified DeepSeek automation: sessions, export, search, sync) |
| `harmony_hub/` | Harmony hub integration |
| `multi-ai-cli/` | Multi-model CLI surface |
| `commingle-swarm/` | **Template / scavenge-only** external clone — not first-class runtime |
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
❯ ls                                                       01_Agent_Runtime         final_intel.json
02_Memory_Session        flywheel_intel.txt
03_Agent_Communication   inventory_deep.py                 04_CedarScript           inventory_repos.py
05_Safety_Observability  meta_intel.txt
06_Task_Tracking         move_log.txt                      07_Prompt_Context        quick_intel.txt                   08_Swarm_References      quick_recon.sh                    09_Auth_Networking       recon.py
10_Infrastructure        recon.sh                          11_Evaluation_Quality    recon_lag.py                      12_External_Agents       recon_v2.sh                       13_Third_Party_Refs      repo_intel.txt
14_Plain_Files           repo_inventory.json               15_Reverse_Engineering   repo_inventory_deep.json          README.md                revert.sh
_TOOL_TAXONOMY           scavenge.sh                       deep_intel.txt           sparse_report.txt
deep_recon.sh            surgical_intel.txt                fast_intel.txt           surgical_recon.sh                 fast_scan.sh             trunk_builder.py                  ❯ tree -L 3
.                                                          ├── 01_Agent_Runtime                                       │   ├── agent-c
│   │   ├── Dockerfile                                     │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── pyproject.toml                                 │   │   └── requirements.txt
│   ├── better-clawd
│   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── bun.lock
│   │   ├── package.json                                   │   │   └── schemas
│   ├── big-AGI
│   │   ├── AGENTS.md -> CLAUDE.md                         │   │   ├── CLAUDE.md                                      │   │   ├── Dockerfile
│   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── kb                                             │   │   ├── package-lock.json                              │   │   ├── package.json                                   │   │   ├── pages                                          │   │   ├── public
│   │   └── tools                                          │   ├── cc-mirror                                          │   │   ├── AGENTS.md                                      │   │   ├── CLAUDE.md
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── package-lock.json                              │   │   └── package.json                                   │   ├── ccs                                                │   │   ├── AGENTS.md -> CLAUDE.md                         │   │   ├── CLAUDE.md                                      │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── assets                                         │   │   ├── bun.lock                                       │   │   ├── config                                         │   │   ├── docker                                         │   │   ├── eslint-rules                                   │   │   ├── macos-bar                                      │   │   ├── package.json                                   │   │   └── ui                                             │   ├── frankenterm
│   │   ├── AGENTS.md                                      │   │   ├── Cargo.lock                                     │   │   ├── Cargo.toml
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── assets                                         │   │   ├── crates
│   │   ├── evidence
│   │   ├── frankenterm                                    │   │   ├── fuzz                                           │   │   ├── lints
│   │   ├── rules                                          │   │   ├── rust-toolchain.toml                            │   │   └── scratch                                        │   ├── hermes-agent                                       │   │   ├── AGENTS.md                                      │   │   ├── CONTRIBUTING.es.md                             │   │   ├── CONTRIBUTING.md                                │   │   ├── Dockerfile
│   │   ├── LICENSE                                        │   │   ├── README.es.md                                   │   │   ├── README.md                                      │   │   ├── README.ur-pk.md
│   │   ├── README.zh-CN.md                                │   │   ├── REPO_INFO                                      │   │   ├── SECURITY.es.md                                 │   │   ├── SECURITY.md                                    │   │   ├── TAGS.txt                                       │   │   ├── agent                                          │   │   ├── apps                                           │   │   ├── cli.py                                         │   │   ├── docker-compose.windows.yml                     │   │   ├── docker-compose.yml
│   │   ├── hermes_cli
│   │   ├── hermes_state.py                                │   │   ├── model_tools.py                                 │   │   ├── optional-skills
│   │   ├── package-lock.json                              │   │   ├── package.json                                   │   │   ├── packaging                                      │   │   ├── plugins                                        │   │   ├── providers
│   │   ├── pyproject.toml                                 │   │   ├── run_agent.py
│   │   ├── setup.py
│   │   ├── skills                                         │   │   ├── toolsets.py
│   │   ├── ui-tui                                         │   │   ├── web
│   │   └── website                                        │   ├── hermes-agent_new
│   │   ├── AGENTS.md                                      │   │   ├── Dockerfile                                     │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── acp_adapter
│   │   ├── acp_registry                                   │   │   ├── agent
│   │   ├── cron                                           │   │   ├── datagen-config-examples                        │   │   ├── docker                                         │   │   ├── docker-compose.yml
│   │   ├── gateway                                        │   │   ├── hermes_cli                                     │   │   ├── locales                                        │   │   ├── nix                                            │   │   ├── package-lock.json                              │   │   ├── package.json
│   │   ├── packaging                                      │   │   ├── plugins                                        │   │   ├── providers                                      │   │   ├── pyproject.toml                                 │   │   ├── setup.py                                       │   │   ├── skills                                         │   │   ├── tools
│   │   ├── tui_gateway
│   │   ├── ui-tui
│   │   └── web                                            │   ├── hermes-webui
│   │   ├── AGENTS.md                                      │   │   ├── ARCHITECTURE.md
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── api                                            │   │   ├── docker-compose.yml                             │   │   ├── package.json                                   │   │   ├── pyproject.toml                                 │   │   ├── requirements-dev.txt                           │   │   ├── requirements.txt                               │   │   └── static                                         │   ├── opencode
│   │   ├── AGENTS.md                                      │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── bun.lock                                       │   │   ├── github                                         │   │   ├── infra                                          │   │   ├── nix                                            │   │   ├── package.json                                   │   │   ├── patches
│   │   ├── perf                                           │   │   ├── script                                         │   │   ├── sdks                                           │   │   └── specs                                          │   ├── openrouter-deep-research-mcp
│   │   ├── AGENTS.md                                      │   │   ├── CLAUDE.md                                      │   │   ├── Dockerfile                                     │   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── extension                                      │   │   ├── harnesses
│   │   ├── package.json                                   │   │   ├── research_outputs                               │   │   ├── skills
│   │   └── templates                                      │   ├── orca                                               │   │   ├── AGENTS.md                                      │   │   ├── CLAUDE.md
│   │   ├── Casks                                          │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   ├── config                                         │   │   ├── mobile
│   │   ├── native                                         │   │   ├── notes
│   │   ├── package.json                                   │   │   ├── pnpm-lock.yaml
│   │   ├── previews                                       │   │   ├── resources                                      │   │   ├── skills                                         │   │   └── tools
│   ├── pi                                                 │   │   ├── AGENTS.md                                      │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   ├── package-lock.json
│   │   └── package.json                                   │   ├── pi_agent_rust
│   │   ├── AGENTS.md
│   │   ├── Cargo.lock                                     │   │   ├── Cargo.toml
│   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── benches                                        │   │   ├── fuzz                                           │   │   ├── legacy_pi_mono_code                            │   │   ├── proptest-regressions                           │   │   ├── rust-toolchain.toml
│   │   └── themes                                         │   └── senpi
│       ├── AGENTS.md                                      │       ├── Cargo.lock
│       ├── Cargo.toml
│       ├── README.md                                      │       ├── REPO_INFO
│       ├── TAGS.txt                                       │       ├── bench                                          │       ├── package-lock.json
│       ├── package.json
│       └── rust-toolchain.toml                            ├── 02_Memory_Session
│   ├── cass_memory_system                                 │   │   ├── AGENTS.md                                      │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── SKILL.md                                       │   │   ├── TAGS.txt
│   │   ├── bun.lock                                       │   │   ├── competing_proposal_plans                       │   │   ├── package-lock.json                              │   │   └── package.json                                   │   └── coding_agent_session_search                        │       ├── AGENTS.md                                      │       ├── Cargo.lock                                     │       ├── Cargo.toml                                     │       ├── README.md                                      │       ├── REPO_INFO
│       ├── SKILL.md                                       │       ├── TAGS.txt
│       ├── benches                                        │       ├── fuzz
│       ├── packaging                                      │       └── rust-toolchain.toml
├── 03_Agent_Communication
│   └── mcp_agent_mail_rust                                │       ├── AGENTS.md
│       ├── Cargo.lock                                     │       ├── Cargo.toml                                     │       ├── Dockerfile
│       ├── README.md                                      │       ├── REPO_INFO                                      │       ├── TAGS.txt                                       │       ├── benches
│       ├── crates                                         │       ├── experimental
│       ├── refactor                                       │       └── rust-toolchain.toml
├── 04_CedarScript
│   ├── cedarscript-ast-parser-python                      │   │   ├── Makefile
│   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   └── pyproject.toml                                 │   ├── cedarscript-editor-python
│   │   ├── Makefile                                       │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   └── pyproject.toml                                 │   ├── cedarscript-grammar
│   │   ├── Dockerfile                                     │   │   ├── Makefile
│   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── package.json
│   │   ├── proposals                                      │   │   └── pyproject.toml                                 │   └── cedarscript-mcp                                    │       ├── README.md                                      │       ├── REPO_INFO
│       ├── TAGS.txt                                       │       ├── package-lock.json                              │       ├── package.json                                   │       └── queries
├── 05_Safety_Observability                                │   ├── destructive_command_guard                          │   │   ├── AGENTS.md                                      │   │   ├── Cargo.lock
│   │   ├── Cargo.toml                                     │   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── SKILL.md                                       │   │   ├── TAGS.txt                                       │   │   ├── action                                         │   │   ├── agent_baseline
│   │   ├── benches
│   │   ├── fuzz                                           │   │   ├── patches
│   │   ├── perf
│   │   └── rust-toolchain.toml                            │   ├── process_triage
│   │   ├── AGENTS.md
│   │   ├── Cargo.lock
│   │   ├── Cargo.toml
│   │   ├── Dockerfile
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── completions                                    │   │   ├── crates                                         │   │   ├── fuzz                                           │   │   ├── rust-toolchain.toml                            │   │   ├── specs
│   │   └── sql
│   ├── rano                                               │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   └── logs
│   └── system_resource_protection_script
│       ├── Dockerfile                                     │       ├── HomebrewFormula
│       ├── README.md                                      │       ├── REPO_INFO                                      │       ├── TAGS.txt                                       │       ├── cmd
│       ├── go.mod                                         │       ├── go.sum
│       └── internal                                       ├── 06_Task_Tracking                                       │   ├── beads_rust                                         │   │   ├── AGENTS.md
│   │   ├── Cargo.lock
│   │   ├── Cargo.toml                                     │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── agent_baseline
│   │   ├── benches                                        │   │   ├── fuzz
│   │   ├── packaging
│   │   ├── refactor                                       │   │   ├── rust-toolchain.toml
│   │   ├── skills                                         │   │   ├── temp_test
│   │   └── temp_test_2                                    │   └── beads_viewer                                       │       ├── AGENTS.md
│       ├── Makefile
│       ├── README.md                                      │       ├── REPO_INFO
│       ├── SKILL.md
│       ├── TAGS.txt                                       │       ├── bv-graph-wasm                                  │       ├── cmd                                            │       ├── go.mod
│       ├── go.sum
│       ├── internal
│       ├── screenshots                                    │       └── testdata
├── 07_Prompt_Context                                      │   ├── Interpreted-Context-Methdology                     │   │   ├── CLAUDE.md
│   │   ├── LICENSE
│   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── fast_intel.txt
│   │   └── workspaces                                     │   ├── Interpreted-Context-Methdology_fork
│   │   ├── CLAUDE.md
│   │   ├── LICENSE
│   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── fast_intel.txt
│   │   └── workspaces                                     │   ├── _TOOL_TAXONOMY -> /data/data/com.termux/files/home/workspace/llm_map/_TOOL_TAXONOMY
│   ├── markdown_web_browser                               │   │   ├── AGENTS.md                                      │   │   ├── Dockerfile                                     │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   ├── config                                         │   │   ├── docker-compose.yml
│   │   ├── k8s
│   │   ├── ops                                            │   │   ├── playwright
│   │   ├── pyproject.toml
│   │   └── web                                            │   ├── source_to_prompt_tui
│   │   ├── AGENTS.md
│   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   ├── bun.lock                                       │   │   └── package.json
│   └── toon_rust                                          │       ├── Cargo.toml                                     │       ├── README.md                                      │       ├── REPO_INFO                                      │       ├── TAGS.txt                                       │       └── benches
├── 08_Swarm_References
│   ├── swarm-ecosystem                                    │   │   ├── README.md
│   │   ├── REPO_INFO
│   │   └── TAGS.txt                                       │   ├── swarms
│   │   ├── CLAUDE.md
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── images                                         │   │   ├── pyproject.toml                                 │   │   ├── requirements.txt                               │   │   └── swarms                                         │   └── swarms-rs                                          │       ├── README.md -> swarms-rs/README.md               │       ├── REPO_INFO
│       ├── TAGS.txt                                       │       ├── swarms-macro                                   │       └── swarms-rs                                      ├── 09_Auth_Networking                                     │   ├── coding_agent_account_manager                       │   │   ├── AGENTS.md
│   │   ├── Makefile                                       │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── cmd                                            │   │   ├── go.mod
│   │   ├── go.sum                                         │   │   ├── internal
│   │   └── web                                            │   ├── openclaw-zero-token                                │   │   ├── AGENTS.md                                      │   │   ├── ARCHITECTURE.md                                │   │   ├── CLAUDE.md -> AGENTS.md                         │   │   ├── Dockerfile                                     │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── Swabble                                        │   │   ├── TAGS.txt                                       │   │   ├── apps                                           │   │   ├── assets                                         │   │   ├── auto-reply                                     │   │   ├── bindings                                       │   │   ├── bluebubbles                                    │   │   ├── bootstrap                                      │   │   ├── brave                                          │   │   ├── browser                                        │   │   ├── canvas-host                                    │   │   ├── channels
│   │   ├── chat                                           │   │   ├── chutes                                         │   │   ├── cli
│   │   ├── cloudflare-ai-gateway                          │   │   ├── commands
│   │   ├── compat                                         │   │   ├── config
│   │   ├── context-engine                                 │   │   ├── copilot-proxy
│   │   ├── cron                                           │   │   ├── daemon                                         │   │   ├── deepgram                                       │   │   ├── device-pair                                    │   │   ├── diagnostics-otel
│   │   ├── diffs                                          │   │   ├── discord
│   │   ├── docker-compose.yml                             │   │   ├── duckduckgo                                     │   │   ├── elevenlabs                                     │   │   ├── exa                                            │   │   ├── extensions                                     │   │   ├── fal
│   │   ├── firecrawl                                      │   │   ├── flows                                          │   │   ├── gateway                                        │   │   ├── generated
│   │   ├── git-hooks                                      │   │   ├── github-copilot
│   │   ├── helpers                                        │   │   ├── hooks                                          │   │   ├── i18n                                           │   │   ├── image-generation
│   │   ├── image-generation-core                          │   │   ├── infra
│   │   ├── interactive                                    │   │   ├── irc
│   │   ├── link-understanding                             │   │   ├── llm-task                                       │   │   ├── logging                                        │   │   ├── markdown                                       │   │   ├── mcp
│   │   ├── media                                          │   │   ├── media-understanding
│   │   ├── media-understanding-core                       │   │   ├── minimax
│   │   ├── mocks                                          │   │   ├── msteams
│   │   ├── nextcloud-talk                                 │   │   ├── node-host
│   │   ├── nostr                                          │   │   ├── nvidia
│   │   ├── ollama                                         │   │   ├── open-prose
│   │   ├── openai                                         │   │   ├── opencode                                       │   │   ├── opencode-go                                    │   │   ├── openrouter                                     │   │   ├── openshell                                      │   │   ├── package.json
│   │   ├── pairing                                        │   │   ├── patches
│   │   ├── perplexity                                     │   │   ├── phone-control
│   │   ├── plugin-sdk                                     │   │   ├── plugins                                        │   │   ├── pnpm-lock.yaml                                 │   │   ├── process                                        │   │   ├── public                                         │   │   ├── pyproject.toml                                 │   │   ├── qianfan                                        │   │   ├── routing
│   │   ├── secrets                                        │   │   ├── security
│   │   ├── sessions
│   │   ├── sglang                                         │   │   ├── shared
│   │   ├── signal
│   │   ├── skills
│   │   ├── slack
│   │   ├── speech-core                                    │   │   ├── synology-chat
│   │   ├── synthetic
│   │   ├── talk-voice                                     │   │   ├── tavily
│   │   ├── telegram
│   │   ├── terminal
│   │   ├── test-fixtures                                  │   │   ├── test-helpers
│   │   ├── test-utils
│   │   ├── thread-ownership                               │   │   ├── tlon
│   │   ├── together
│   │   ├── tts                                            │   │   ├── tui                                            │   │   ├── twitch
│   │   ├── types
│   │   ├── ui
│   │   ├── utils
│   │   ├── venice                                         │   │   ├── vercel-ai-gateway                              │   │   ├── vllm                                           │   │   ├── voice-call                                     │   │   ├── volcengine                                     │   │   ├── web-search
│   │   ├── whatsapp
│   │   ├── wizard
│   │   ├── xai                                            │   │   ├── xiaomi                                         │   │   ├── zai                                            │   │   ├── zalo                                           │   │   └── zalouser                                       │   └── rust_proxy                                         │       ├── Cargo.toml                                     │       ├── README.md                                      │       ├── REPO_INFO
│       └── TAGS.txt                                       ├── 10_Infrastructure                                      │   ├── Artifacts
│   │   └── perfect_trunk_cc-mirror
│   ├── Haven                                              │   │   ├── README.md
│   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   ├── build-ffmpeg                                   │   │   ├── build-proot
│   │   ├── core                                           │   │   ├── dev
│   │   ├── fastlane                                       │   │   ├── feature
│   │   ├── gradle                                         │   │   ├── integration-tests                              │   │   ├── metadata                                       │   │   ├── rclone-android
│   │   ├── rdp-kotlin                                     │   │   ├── scratch                                        │   │   └── tools                                          │   ├── conduit                                            │   │   ├── AGENTS.md
│   │   ├── CLAUDE.md -> AGENTS.md                         │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   ├── android                                        │   │   ├── assets                                         │   │   ├── ios
│   │   ├── pigeons
│   │   └── tool                                           │   ├── ntm                                                │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── cmd                                            │   │   ├── e2e                                            │   │   ├── internal                                       │   │   ├── references                                     │   │   ├── testdata                                       │   │   ├── third_party                                    │   │   ├── vscode                                         │   │   └── web                                            │   └── repo_updater                                       │       ├── README.md                                      │       ├── REPO_INFO
│       ├── TAGS.txt                                       │       └── pyproject.toml                                 ├── 11_Evaluation_Quality                                  │   ├── Approxination-Benchmark
│   │   ├── README.md
│   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   └── tasks
│   ├── Inverse-Arena
│   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── inverse_arena_eval
│   │   └── pyproject.toml
│   ├── OpenWebUI-Monitor                                  │   │   ├── AGENTS.md
│   │   ├── Dockerfile
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── components
│   │   ├── docker-compose.yml
│   │   ├── hooks                                          │   │   ├── locales
│   │   ├── package.json                                   │   │   ├── pnpm-lock.yaml
│   │   └── resources                                      │   ├── hermes-agent-self-evolution
│   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── datasets                                       │   │   ├── evolution
│   │   └── pyproject.toml                                 │   └── ultimate_bug_scanner                               │       ├── AGENTS.md                                      │       ├── Dockerfile                                     │       ├── README.md
│       ├── REPO_INFO                                      │       ├── SKILL.md
│       ├── TAGS.txt
│       ├── modules
│       ├── notes                                          │       ├── pyproject.toml
│       └── test-suite
├── 12_External_Agents
│   ├── AiShell                                            │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   └── aishell                                        │   ├── YGK-a
│   │   ├── README.md
│   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── pyproject.toml                                 │   │   └── ygka                                           │   ├── brenner_bot
│   │   ├── AGENTS.md                                      │   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── apps                                           │   │   ├── artifacts                                      │   │   ├── bun.lock                                       │   │   ├── gemini_3_deep_think_responses
│   │   ├── gpt_pro_extended_reasoning_responses           │   │   ├── internal_notes_and_plans
│   │   ├── opus_45_responses                              │   │   ├── package.json
│   │   └── specs                                          │   ├── lazycodex
│   │   ├── README.md
│   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── package-lock.json
│   │   ├── package.json                                   │   │   └── plugins
│   ├── llm_fallbacks                                      │   │   ├── AGENTS.md
│   │   ├── README.md
│   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── configs                                        │   │   ├── pyproject.toml                                 │   │   ├── requirements-dev.txt                           │   │   ├── requirements.txt                               │   │   └── setup.py
│   └── oh-my-openagent                                    │       ├── AGENTS.md
│       ├── CLAUDE.md -> AGENTS.md                         │       ├── README.md                                      │       ├── REPO_INFO
│       ├── TAGS.txt
│       ├── assets                                         │       ├── bun.lock
│       ├── package.json                                   │       ├── script
│       ├── signatures                                     │       └── test-support
├── 13_Third_Party_Refs                                    │   ├── ChapitoAI-main                                     │   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── chapito
│   │   └── pyproject.toml                                 │   ├── CloudBooter                                        │   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── cloud
│   │   └── helper_scripts                                 │   ├── My-Jogyo                                           │   │   ├── AGENTS.md                                      │   │   ├── ARCHITECTURE.md
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── agents                                         │   │   ├── commands                                       │   │   ├── config                                         │   │   ├── package.json                                   │   │   ├── plans
│   │   ├── pyproject.toml                                 │   │   └── skills                                         │   ├── README.md
│   ├── REPO_INFO                                          │   ├── TAGS.txt                                           │   ├── Termux                                             │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   └── TAGS.txt                                       │   ├── TradingAgents                                      │   │   ├── Dockerfile
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── cli
│   │   ├── docker-compose.yml                             │   │   ├── pyproject.toml                                 │   │   ├── requirements.txt                               │   │   └── tradingagents
│   ├── aadc
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   └── benches
│   ├── assistral                                          │   │   ├── CLAUDE.md
│   │   ├── LICENSE
│   │   ├── Makefile                                       │   │   ├── README.md                                      │   │   ├── RELEASES.md
│   │   ├── REPO_INFO
│   │   ├── TAGS.txt
│   │   ├── build.gradle                                   │   │   ├── gradle.properties                              │   │   ├── gradlew
│   │   ├── gradlew.bat                                    │   │   └── settings.gradle                                │   ├── audio-preprocess                                   │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── fish_audio_preprocess                          │   │   ├── pyproject.toml
│   │   └── tools                                          │   ├── colab-ssh                                          │   │   ├── Makefile
│   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── colab_ssh                                      │   │   ├── requirements.txt
│   │   └── setup.py                                       │   ├── colabcode
│   │   ├── Makefile                                       │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── colabcode                                      │   │   ├── requirements.txt                               │   │   └── setup.cfg                                      │   ├── colabsh                                            │   │   ├── Dockerfile                                     │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── info_checks                                    │   │   └── pyproject.toml
│   ├── colabtools                                         │   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── google
│   │   ├── jupyter-config
│   │   ├── notebooks
│   │   ├── setup.cfg                                      │   │   └── setup.py                                       │   ├── ffa-brackets
│   │   ├── Cargo.lock
│   │   ├── Cargo.toml
│   │   ├── REPO_INFO
│   │   └── TAGS.txt                                       │   ├── fish-audio-python
│   │   ├── README.md                                      │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   └── pyproject.toml
│   ├── google-colab-cli                                   │   │   ├── AGENTS.md
│   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── integration
│   │   ├── pyproject.toml                                 │   │   └── skills
│   ├── insane-search                                      │   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── setup                                          │   │   └── skills                                         │   ├── openrouter-rs                                      │   │   ├── AGENTS.md                                      │   │   ├── CLAUDE.md                                      │   │   ├── Cargo.lock
│   │   ├── Cargo.toml                                     │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt                                       │   │   ├── crates                                         │   │   ├── openspec
│   │   └── specs                                          │   ├── openskill.lua
│   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   └── TAGS.txt
│   └── starship                                           │       ├── Cargo.lock                                     │       ├── Cargo.toml
│       ├── README.md
│       ├── REPO_INFO
│       ├── TAGS.txt
│       ├── install
│       └── media
├── 14_Plain_Files                                         │   ├── approxination.txt                                  │   └── ranking_research-concept-_.txt                     ├── 15_Reverse_Engineering                                 │   ├── AIStudio2API                                       │   │   ├── README.md
│   │   ├── README_en.md                                   │   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── docker
│   │   └── pyproject.toml                                 │   ├── AIStudioProxy
│   │   ├── LICENSE                                        │   │   ├── README.md                                      │   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── configs                                        │   │   ├── docker
│   │   ├── docker-compose.dev.yml                         │   │   ├── docker-compose.yml
│   │   ├── poetry.lock                                    │   │   └── pyproject.toml
│   ├── AIstudioProxyAPI                                   │   │   ├── CONTRIBUTING.md
│   │   ├── LICENSE                                        │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── api_utils                                      │   │   ├── auth_profiles
│   │   ├── browser_utils
│   │   ├── certs
│   │   ├── config                                         │   │   ├── docker
│   │   ├── excluded_models.txt
│   │   ├── gui
│   │   ├── launch_camoufox.py                             │   │   ├── launcher
│   │   ├── logging_utils
│   │   ├── models
│   │   ├── monkeytype_config.py
│   │   ├── poetry.lock
│   │   ├── pyproject.toml                                 │   │   ├── pyrightconfig.json                             │   │   ├── server.py                                      │   │   ├── simple_launcher.py
│   │   ├── simple_start.sh                                │   │   ├── static
│   │   ├── stream
│   │   ├── supervisord.conf                               │   │   └── support_author.jpg
│   ├── README.md                                          │   ├── gemini-cli-api
│   │   ├── LICENSE
│   │   ├── README.ja-JP.md                                │   │   ├── README.md
│   │   ├── README.zh-CN.md
│   │   ├── REPO_INFO                                      │   │   ├── SYSTEM_DESIGN.md
│   │   ├── TAGS.txt                                       │   │   ├── env.example
│   │   ├── output_comparison.py                           │   │   ├── pyproject.toml
│   │   ├── requirements.txt                               │   │   ├── start_server.sh
│   │   └── uv.lock                                        │   ├── gemini_recon
│   │   ├── Gemini-API                                     │   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── gemini-web-to-api
│   │   ├── gemini-web2api                                 │   │   ├── requirements.txt
│   │   └── reverse_gemini-cli
│   ├── reverser_ai
│   │   ├── README.md
│   │   ├── REPO_INFO                                      │   │   ├── TAGS.txt
│   │   ├── requirements.txt
│   │   ├── reverser_ai                                    │   │   └── setup.py
│   ├── userscripts
│   │   ├── README.md
│   │   ├── REPO_INFO
│   │   ├── TAGS.txt                                       │   │   ├── package-lock.json
│   │   └── package.json                                   │   └── userscripts_new
│       ├── README.md                                      │       ├── REPO_INFO
│       ├── TAGS.txt                                       │       ├── package-lock.json                              │       └── package.json
├── README.md                                              ├── _TOOL_TAXONOMY -> /data/data/com.termux/files/home/workspace/llm_map/_TOOL_TAXONOMY                               ├── deep_intel.txt
├── deep_recon.sh                                          ├── fast_intel.txt
├── fast_scan.sh                                           ├── final_intel.json
├── flywheel_intel.txt                                     ├── inventory_deep.py
├── inventory_repos.py                                     ├── meta_intel.txt
├── move_log.txt                                           ├── quick_intel.txt
├── quick_recon.sh                                         ├── recon.py
├── recon.sh                                               ├── recon_lag.py
├── recon_v2.sh                                            ├── repo_intel.txt                                         ├── repo_inventory.json
├── repo_inventory_deep.json
├── revert.sh
├── scavenge.sh
├── sparse_report.txt                                      ├── surgical_intel.txt
├── surgical_recon.sh
└── trunk_builder.py

450 directories, 539 files
~/refTemplates ❯                                  14:18:28
```

**On `master` today:** only a stub under `refTemplates/01_Agent_Runtime/`.  
**Full metadata skeleton:** branch `recreate/refTemplates-skeleton` (README.md + SOURCE.txt per entry; depth-1 sparse style). See `refTemplates/README_RECOVERY.md` on that branch.

```
refTemplates/
  01_Agent_Runtime/
    frankenterm/
    hermes-agent/
    opencode/
    orca/
    pi_agent_rust/
    senpi/
    # also historically: deepcode-cli (pointer removed in consolidation)
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
    # nest here: Interpreted-Context-Methdology_fork (currently uncategorized at tree -L 1)
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
    # also historically: assistral (pointer removed)
  14_Plain_Files/
    approxination.txt
    ranking_research-concept-_.txt
  15_Reverse_Engineering/   # MISSING as category — pointers removed in consolidation; recreate as metadata-only
    # AIStudio2API, AIStudioProxy, AIstudioProxyAPI, gemini-cli-api
```

**Uncategorized at tree -L 1 (need nesting):**

- `Haven/` → propose 15_Android_Workspaces or 16_Product_Workspaces
- `Interpreted-Context-Methdology_fork/` → propose under 07_Prompt_Context

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

Summary: The repo history shows active restoration attempts — multiple commits rehydrated `refTemplates` from a backup commit (d5814d9 referenced). Later consolidation removed some explicit submodule pointers, possibly because content was restored directly or those submodules were intentionally removed. The state on `master` represents the consolidated result of these operations. **Category 15 and several L1 names remain debt** — see `docs/RECON.md` §5.

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

**Primary (preferred):** restore metadata-only skeleton from `recreate/refTemplates-skeleton`:

```bash
git fetch origin recreate/refTemplates-skeleton
git restore --source=origin/recreate/refTemplates-skeleton -- refTemplates
git add refTemplates
git commit -m "Restore refTemplates metadata from recreate/refTemplates-skeleton"
```

**Fallback (if skeleton branch is unavailable):** checkout from a known restore commit:

```bash
git log --all --pretty=format:'%H %ad %s' --date=iso -- refTemplates | head -n 50
git checkout <commit> -- refTemplates
git add refTemplates
git commit -m "Restore refTemplates from <commit>"
```

Prefer depth-1 selective sparse-checkout of relevant files (metadata only) rather than full recursive population. Nest uncategorized L1 entries (Haven, ICM_fork) and restore **15_Reverse_Engineering** as metadata slots.

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
- Session stores must not be tracked in Git (see open PR #3 `agent/repository-hygiene`).
- Back up large JSONL indices externally before attempting destructive rebuilds.

---

## Open branches & PRs (snapshot 2026-08-01)

| Item | Note |
|------|------|
| PR #1 `critical-proposal` | Docs: critical eval + roadmap — mergeable |
| PR #2 `timerloggedout-spec-patch-1` | GHA Rust — narrow scope before merge |
| PR #3 `agent/repository-hygiene` (draft) | Untrack session stores — **priority** |
| `recreate/refTemplates-skeleton` | Full metadata tree; merge to master |
| `mistral/fixes-config-security` | config.py + security baseline |
| `vibe/mistralai-vibe-code-wrapper-*` | Mistral CLI + harvester; fix silent dispatch |

Detail and ranked proposals: **`docs/RECON.md`**.

---

## What I can do next (pick one or more)
1. Run selective submodule / sparse-checkout steps and report results (I can run commands only if you ask me to perform GitHub write operations or environment commands; I can provide exact commands for you to run).
2. Page through archwiz and workspace/llm_map to list every `.bak` file and recommend the highest-confidence restoration candidates.
3. Land refTemplates skeleton + category 15 nesting on a dedicated `feature/*` branch.
4. Create follow-up PRs for P0 items in `docs/RECON.md` (dispatch logging, PR #3 hygiene).

---

## Audit trail of the consolidation I performed (Option C results summary)
- Located and read these recent commits on `master`:
  - b104890bbc0c25c8c152c089cbfb7153e2bddca7 — "Restore refTemplates and codex blobs from d5814d9 (clone method)"
  - 8a53ffb84fe0e3f8dbce070480b2327946a435c8 — "Restore refTemplates and codex blobs from d5814d9"
  - 416a9cd1fc9ff1c3a46f364f79b23535bf0920ca — "Complete restore: all files from backup commit d5814d9"
  - 65c9f81162fd9a080a4a8aea4f6a0b6ecd2dcd72 — "Complete restore: refTemplates, submodules, and powerlevel10k"
  - ee1807049fd93d087bc14055b2ae6cbffb5dbf82 — "Add base configs and dotfiles"
  - ebe3e0ca504cb35ef61832b0b1b1576a1a0d44fb — "Initial monorepo commit..."
  - f19716e / 5c6e5e2 / 6ef0e2f — README expand + refTemplates stub restore

- Found `.gitmodules` with multiple submodule URLs — use **selective depth-1** updates only when a listed submodule is needed; refTemplates historically used sparse depth-1 checkout with metadata only.
- Found evidence that some restored content was then consolidated and had submodule pointers removed in the latest commit; verify that removed submodules are intentionally removed (or re-add them via git submodule add if needed).

---

If you confirm further implementation work, use **`feature/*` branches only** (never commit recovery or nav changes straight to `master` without review). See `docs/RECON.md` for the full proposal table.
