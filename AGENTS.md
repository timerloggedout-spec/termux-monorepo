<!-- LinguistProjection: generated; source=AGENTS.hum.md; mode=machine-grimoire-seed-v1; structural-exceptions=fenced-code,markdown-link-destinations -->

# §02§.md

This §0b§ provides guidance to §02§ when working with code in this §19§.

## Governance & §17§ (Read First)

1. **This §0b§** (`§02§.md`)
2. [`docs/LINEAR-AGENT-PROTOCOL.md`](docs/LINEAR-AGENT-PROTOCOL.md) — **Linear hooks for every §01§ action**
3. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
4. [`docs/proposals/§17§.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
5. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-agent)
6. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
7. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — living board
8. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges + **§04§ model**
9. [`docs/SENTRY_LINEAR.md`](docs/SENTRY_LINEAR.md) — Sentry multi-project + Linear bridgeture/sentry-linear-integration

Optional: `§05§.md`, `CONTRIBUTING.md`.

## Hard Rules

- Target **`master-staging`**, not raw `master`, for §0f§ work.
- **`master-staging` is a permanent §0f§ spine** — never merge it wholesale into `master`. Promotion to `master` is **selective** (cherry-pick / focused promotion PRs only). Operator: *"master-staging is for selective merge to master meaning master-staging is meant to never merge to master completely."*
- Both gates must pass before merge to staging:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first **and** a Linear `TER-*` issue.
- Cite **`Implements: TER-N`** (and proposal item IDs) on PRs/commits.
- **Linear is mandatory for §01§ actions** — see protocol:
  - Start work → Linear **In Progress**
  - Open PR (base **`master-staging`**) → comment on TER-* with PR URL
  - Merge to **`master-staging`** → Linear **Done** + evidence
  - MCP: `linear___save_issue` / `linear___list_issues`
    CLI: `python3 -m archwiz.linear_client start|done|status|comment TER-N`
- **No** wholesale merge of PR #6 (TER-9) or PR #2 (Rust CI) — see disposition comments.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write §1a§ log or DEBATE.md (and Linear comment if execution-related).
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster (not a single-agent monopoly).

## Debate & close

- Debate: MANIFEST §1a§ log, optional DEBATE.md, linked PR/issue.
- Close: all items terminal + §1a§ log outcome + move `active/` → `closed/` + registry update.
- Close related **Linear TER-*** explicitly (Done / Canceled) — proposal close does not auto-close Linear.
- Full rules: `docs/proposals/§17§.md` §§ consensus / closing · `docs/LINEAR-AGENT-PROTOCOL.md`.

## Preferred execution loop

```text
registry.yaml + Linear list_issues → pick todo
  → linear_client start TER-N (or MCP save_issue In Progress)
  → branch from master-staging (prefer Linear gitBranchName)
  → implement → PR (base master-staging) with Implements: TER-N[, ITEM-ID]
  → comment on Linear issue with PR URL
  → gates green → merge to master-staging
  → linear_client done TER-N --pr <n>
  → update ITEMS.md status
  → (optional, separate) selective promotion of ready commits to master
```

## §1b§

Credential rotation and history rewrite require Operator (§0e§) authorization.
See `docs/SECURITY-REMEDIATION.md`.
---

# Technical §0a§

## §18§ Overview

This is a **Termux-based multi-agent automation monorepo** running on Android. It orchestrates AI-powered development §a7§ through multiple specialized CLI tools and autonomous §02§. The §1c§ integrates with DeepSeek API, manages conversation branching, performs code forensics, and maintains comprehensive knowledge indices.

**Core Technologies:**
- **§10§:** Python 3 (primary), Node.js (supporting), Bash, Rust (selective components)
- **Platform:** Termux on Android
- **AI §0f§:** DeepSeek API, multi-model support
- **Architecture:** Microservices-style with shared workspace and indices

**Codebase Statistics (via tokei):**
```
Total: 7,248 files | 2.1M lines
- Code: 1.83M lines (87.4%)
- Comments: 132K lines (6.3%)
- Blanks: 133K lines (6.3%)

Top Languages:
- Rust: 1.2M lines (1,096K code + 98K blanks)
- JSON: 575K lines (data/config)
- Python: 96K lines (81K code, 775 files)
- Shell: 19K lines (16K code, 243 files)
- Zsh: 22K lines (15K code, 14 files)
- TypeScript: 10K lines (5K code, 655 files)
- JavaScript: 7K lines (6K code, 59 files)
```

**Key Architectural Components:**
1. **ArchWiz** - Central automation cockpit with 28 tools across 7 categories
2. **DeepCLI** - DeepSeek-oriented CLI for session management and streaming
3. **Termux Multi-Agent** - §01§ provisioning and orchestration
4. **CLI Synthegration** - Conversation synthesis and branching
5. **Harmonizer** - Unified automation interface
6. **Central Mapper** - AST indexing and dependency graph generation

## Navigation & §0a§

**Primary Navigation (in priority order):**
1. `archwiz/TOOL_INDEX.md` - 28 tools / 7 categories (cockpit, forensic, autonomous, verification)
2. `archwiz/CONCEPT_INDEX.md` - Concepts + status + feature backlog
3. `archwiz/REFERENCE_HUB.md` - Links to data flow, §1c§ map, indices
4. `archwiz/METHODOLOGY_INDEX.md` - Approaches tried, failures, successes
5. `archwiz/PROCEDURES.md` - Runbooks and active tasks
6. `docs/RECON.md` - §04§/PR critique and proposals
7. `README.md` - Recovery §0a§ and §18§ inventory
8. `workspace/llm_map/SYSTEM_MAP.md` - Complete §18§ catalogue (8,239 §a1§ indexed)
9. `archwiz/DATA_FLOW_MANIFEST.md` - Complete data flow manifest (1.5MB, 8,400 lines)

**Quick §06§ Reference:**
```bash
# Research file history
archaeo <file>

# Check impact before changing
oracle <file>

# Make a change
dispatch <task>

# Validate & promote
validate_promotion.py

# Rebuild indices
map-build && map-func && fore

# Open cockpit
python3 archwiz/archwiz.py
```

## Core §a5§

### 1. DeepCLI (`deepcli/`)
DeepSeek-oriented CLI with session management, streaming, thinking mode, and export capabilities.

**Entry Points:**
- `deepcli.py` - Main CLI launcher
- `deepapi.py` - API interface
- `deepseek_proxy.py` - Proxy layer
- `ci_mode.py` - CI/CD §0f§ entry point
- `ci_agent.py` - GitHub Actions §01§ logic

**Key Commands:**
```bash
./deepcli.py new                                    # Create new session
./deepcli.py send "Your prompt"                     # Send message
./deepcli.py send "Complex task" --thinking         # Enable thinking mode
./deepcli.py list                                   # List sessions
./deepcli.py history --session <session_id>         # View history
./deepcli.py export --format json --output chat.json # Export session
./deepcli.py fork --session <id> --message-id <msg> # Fork conversation
```

**CI/CD §0f§:**
- GitHub Actions §20§: `.github/§a7§/deepseek-ci.yml`
- Triggers on PR events (opened, synchronize, reopened)
- Uses PoW WASM solver for authentication
- Automated PR §1a§ and commenting

**Related:** `deepcli-tui/` (TUI with conversation tree), `.deepcli/` (config), `deepseek-cli/` (includes deepterm)

### 2. Termux Multi-Agent (`termux-multi-agent/`)
Multi-agent orchestration §1c§ for provisioning, running, and managing autonomous §02§.

**Key Components:**
- `provision_agent.py` - §01§ provisioning
- `run.py` - Main run loop
- `dashboard.py` - Status/control UI
- `patch_files.py` / `patch_files_final.py` - Patch application
- `cedar-mcp-server.js` - CedarScript MCP server
- `run_history.jsonl` - Run history tracking

**Task Management:**
- Tasks loaded from `~/workspace/llm_map/master_tasks.json`
- Environment variables: `TASK_ID`, `REFACTOR_GOAL`, `TARGET_FILE`, `TASK_WORKSPACE`
- Fallback: `current_task.txt` in workspace

### 3. CLI Synthegration (`cli-synthegration/`)
Conversation synthesis with branching, export, account/token management, and metrics.

**Notable Modules:**
- `branch_manager.py` - Conversation §0c§ management
- `conv_branching.py` - §04§/§0c§ API implementation
- `conv_explorer.py` - Conversation exploration
- `conv_export_cli.py` - Export functionality
- `account_manager.py` - Multi-account support
- `token_provider.py` - Token management
- `live_export.py` / `live_search.py` - Real-time operations
- `sync_pipeline.py` - Synchronization
- `Chronos/` - Time-loop acceleration
- `workspace/` - Working directories
- `metrics/` - Performance tracking

**Data Storage:**
- `synthegration_exports/` - 3,281 exported session §a1§
- `workspace/correlation/` - Session-to-file correlation index
- `workspace/provenance/` - Version tracking and provenance
- `codex/message_index.json` - Full-text message search index

### 4. ArchWiz (`archwiz/`)
Central automation cockpit with indexing, provenance tracking, and recovery tools.

**Tool Categories (28 tools total):**

**Cockpit & Pipeline:**
- `archwiz.py` - Dashboard with 16 options + 3 mode toggles
- `activity_listener.py` - Auto-executes assistant code blocks
- `live_view.py` - §1a§ panel with /exec, /skip, /send commands
- `debug_daemon.py` - Watches failures, auto-fixes with ruff/shellcheck
- `listener_control.py` - PID-based safe start/stop

**Forensic & Version Control:**
- `forensic_toolchain.py` - Fragment matcher, similarity scan, correlation scout
- `correlation_scout.py` - Traces file-path changes across versions
- `fragment_matcher.py` - Function-level provenance
- `restore_version.py` - Provenance-based code resurrection

**Autonomous Operation:**
- `autonomous_runner.py` - Dispatches pending tasks with memory awareness
- `dispatch_task.py` - Sandboxed execution with Sentinel verification
- `task_builder.py` - Interactive task creation
- `auto_repair.py` - Auto-fixes Sentinel §1a§ issues

**Verification & Testing:**
- `sentinel.py` - 5-gate verification (§0b§ integrity, naming, duplicate, §16§, shockwave)
- `§16§.py` - Syntax/import/test §1d§
- `mirror.py` - Self-critique for task hygiene, index freshness
- `dangle_detector.py` - Cross-ecosystem broken reference scanner

**Knowledge & Memory:**
- `archivist.py` - Local query engine across all indices
- `tasque_declare.py` - Declares completion to taDone.md
- `timeline_editor.py` - Full DB editor + archaeologist
- `narrative.py` - Chronological feed of pipeline events
- `lexicon_harvest.py` - Session scanning for novel terms
- `name_forge.py` - Grimoire-powered tool naming

**§0a§ Pipeline:**
- `session_digest.py` - Scans exported sessions for structured features
- `structural_scanner.py` - Fast chunked-correlation scanner
- `export_status.py` - Shows cached vs exported sessions
- `pointer_index.py` - Builds hash→location map of code blocks

### 5. Central Mapper (`central_mapper_v420.py`, `workspace/llm_map/`)
Comprehensive codebase indexing and dependency analysis.

**Key Indices:**
- `llm_index.jsonl` - Full LLM-optimized index
- `llm_index_compact.jsonl` - Compact version (1.99MB)
- `func_index.jsonl` - Function-level index (287KB)
- `central_enriched.jsonl` - Enriched central index
- `task_files_index.json` - All task/sprint/todo §a1§
- `file_graph.json` - Dependency graph
- `deps.jsonl` - Dependency relationships

**Build Scripts:**
- `build_all.py` - Complete index rebuild
- `build_llm_index.py` - LLM index generation
- `build_ast_index_from_existing.py` - AST index from existing data
- `build_graph_fast.py` - Fast graph generation

### 6. Harmonizer (`harmonizer-prod_cli/`)
Production Harmonizer CLI providing unified DeepSeek automation: sessions, export, search, sync.

### 7. Supporting §a5§
- `harmony_hub/` - Harmony hub §0f§
- `multi-ai-cli/` - Multi-model CLI surface
- `commingle-swarm/` - Template/scavenge-only (not first-class runtime)
- `colab-cli/` - Colab CLI tooling
- `exchanges/` - Exchange/market API code
- `appliedSxi/maxc/` - Applied Sxi/Max work

## Development §20§

### Building and Running

**Prerequisites:**
```bash
# Install base requirements
pip install -r requirements-base.txt

# Core dependencies: curl-cffi, requests, websockets
```

**Initialize Database:**
```bash
cd termux-multi-agent
python run.py  # First run creates workspace and dummy files
```

**Start ArchWiz Cockpit:**
```bash
python3 archwiz/archwiz.py
```

**Run Autonomous §01§:**
```bash
cd termux-multi-agent
export TASK_ID="your-task-id"  # Or set REFACTOR_GOAL
./run_agent.sh
```

**Rebuild Indices:**
```bash
# Central mapper
python3 central_mapper_v420.py

# Provenance indices
cd cli-synthegration/workspace/provenance
python3 final_provenance.py
python3 comprehensive_fast.py

# LLM map (large, may be slow)
cd workspace/llm_map
python3 build_all.py
```

### Testing

**§1d§ Pipeline:**
```bash
# Sentinel 5-gate verification
python3 archwiz/sentinel.py <file>

# Probe syntax/import/test validation
python3 archwiz/probe.py <file>

# Mirror self-critique
python3 archwiz/mirror.py
```

**§01§ Test Runs:**
- Test verdicts tracked in `termux-multi-agent/run_history.jsonl`
- Dashboard available via `termux-multi-agent/dashboard.py`

## CI/CD & GitHub Actions

### Active §a7§

**DeepSeek CI (`.github/§a7§/deepseek-ci.yml`):**
- Triggers: PR opened, synchronize, reopened, manual dispatch
- Features: Automated PR §1a§, code analysis, comment posting
- Authentication: PoW WASM solver (deepseek.wasm + pow_solver.js)
- Session caching for performance
- Artifact upload for results

**Other §a7§:**
- `agent-continuous-ops.yml` - Continuous §01§ operations
- `agent-feedback-linear-sync.yml` - Linear issue sync
- `agent-jules-on-issues.yml` - Jules §01§ for issues
- `agent-review-auto-jules.yml` - Automated Jules reviews
- `gemini-*.yml` - Gemini §0f§ §a7§
- `peer-review-orchestrator.yml` - Multi-peer §1a§ coordination
- `publish-wiki.yml` - Wiki publishing

### GitHub Actions Best Practices
- Use `OPERATOR_TOKEN` secret for authenticated operations
- Cache session data to reduce API calls
- Fetch WASM §a1§ from correct commit hash
- Use metadata-only artifacts for large outputs
- Implement proper error handling and timeouts

## Development Conventions

### Code Style
- **Python:** Follow PEP 8, use `ruff` for linting and auto-fix
- **Shell:** Use `shellcheck` for §1d§
- **Logging:** Use existing patterns or §10§ standard logging library/facade
- **Performance:** Check performance implications of changes
- **§1b§:** §1a§ §1b§ considerations, especially for API tokens and credentials

### §0b§ Organization
- **Indices:** Stored in `workspace/llm_map/`, `archwiz/`, `cli-synthegration/workspace/`
- **Configuration:** Project-specific configs in respective directories
- **Backups:** `.bak` §a1§ created automatically, large JSONL indices backed up externally
- **Ignore Patterns:** Respect `.gitignore` and `.bobignore` (see root `.bobignore` for exclusions)

### Commit Practices
- Use feature branches (`feature/*`) for all changes
- Never commit directly to `master` without §1a§
- Reference task IDs in commit messages when applicable
- Keep commits focused and atomic
- Follow conventional commit format when possible

### §1b§ & Secrets
- **Never commit:** API keys, tokens, cookies, session stores
- **Sensitive §a1§:** `cookies_2.json`, `*_api_key`, `*.env`, `*.pem`, `*.key`
- **Session stores:** Must not be tracked in Git (see PR #3 `§01§/repository-hygiene`)
- **Backup:** Large JSONL indices externally before destructive rebuilds
- **Browser data:** `deepcli/browser-data*/` and `deepseek-cli/browser-data*/` contain sensitive cookies

### Autonomous Operation
- **Task Sources:** `master_tasks.json`, `TASK_ID` env var, `REFACTOR_GOAL` env var, `current_task.txt`
- **Execution:** Sandboxed with Sentinel verification
- **Memory:** Memory-aware dispatching with crash recovery
- **§1d§:** Auto-repair for simple issues, manual §1a§ for complex ones

### Index Management
- **§15§ Index:** CID-style bookmarking (`archwiz/pointer_index.json`)
- **Correlation Index:** Session-to-file links (`cli-synthegration/workspace/correlation/`)
- **True Versions:** Version hash tracking (`cli-synthegration/workspace/provenance/true_versions.json`)
- **Message Index:** Full-text session messages (`cli-synthegration/codex/message_index.json`)
- **Task §a1§:** All task/sprint/todo §a1§ (`workspace/llm_map/task_files_index.json`)
- **Data Flow Manifest:** Complete §0b§ writer tracking (`archwiz/DATA_FLOW_MANIFEST.md`)

### Forensic Recovery
- **Staged Blocks:** `archwiz/staging_blocks.json`
- **Pipeline:** Extract with forensic toolchain → restore with `restore_version.py`
- **Backups:** Automatic `.bak` creation before modifications
- **Restore Points:** Up to 5 per §0b§ (0 = initial state)

## Key Concepts

### Core Abstractions
- **TasQue:** Task completion declaration §1c§ (ta'Done)
- **Sentinel:** 5-gate verification (§0b§, naming, duplicate, §16§, shockwave)
- **Archivist:** Local-only query engine across all indices
- **§16§:** Syntax/import/test §1d§
- **Mirror:** Self-critique for task hygiene and index freshness
- **Dangle Detector:** Cross-ecosystem broken reference scanner
- **§15§ Index:** CID-style bookmarking of messages, tables, data
- **Narrative Feed:** Chronological event stream of pipeline events

### Reserved Concepts (Not Yet Implemented)
- **Spellbook:** Library of §1c§ abilities
- **Rune:** Short hash §15§ (CID-style)
- **Sigil:** Substitution engine for runtime §07§
- **Chronomancer:** Time-loop §01§ with success-only trunks
- **Self-healing Sandbox:** Detect error → request fix → validate → promote

### Methodology Evolution
| Phase | What We Tried → What Stuck |
|-------|---------------------------|
| **Listener lifecycle** | `nohup` → `pkill -f` → `Popen` → `listener_control.py` (PID §0b§) |
| **Chat feedback** | `deepcli_send.py` (new session) → `send_message` (missing fields) → `stream_completion` (TUI pipe) |
| **Session cache** | `synthegration export` → `manifest.json` → `get_history()` direct |
| **Block tracking** | Message-ID → per-block hash (MD5 first 12 chars) |
| **Live View** | Curses → text loop → throttled redraw + `/send` single-line |
| **Hang avoidance** | `stdin=DEVNULL` + `start_new_session=True` + PID-file controller |

## Workspace Structure

```
~/
├── archwiz/              # Central automation cockpit (28 tools)
├── deepcli/              # DeepSeek CLI (205 files)
├── termux-multi-agent/   # Agent orchestration (40 files)
├── cli-synthegration/    # Conversation synthesis (1,355 files)
├── harmonizer-prod_cli/  # Production harmonizer
├── workspace/            # Shared workspace
│   └── llm_map/         # LLM indices (8,239 files indexed)
├── refTemplates/         # Reference templates (metadata-only)
├── _1-Projects/          # Project tree (222 files)
│   ├── a/               # Arbitrage projects (54 files)
│   └── b/               # BSC, Yobit, eggshell (168 files)
├── exchanges/            # Exchange APIs
├── sandbox/              # Experimental code
├── src/                  # Shared sources
├── bin/                  # Binaries
├── config/               # Configuration
├── synthegration_exports/ # 3,281 exported sessions
├── deepseek_harvest_work/ # 1,417 harvested code files
└── deepseek-cli/         # 1,463 files (includes browser data)
```

## Installed Tools

- **ruff** - Python linter + auto-fix
- **shellcheck** - Shell script analysis
- **ripgrep (rg)** - Fast recursive search
- **fd** - Fast `find` alternative
- **jq** - JSON processor
- **entr** - §0b§ watcher
- **tokei** - Code statistics and line counting

## Open Work & Priorities

### Active PRs (as of 2026-08-01)
1. **PR #1 `critical-proposal`** - Critical eval + roadmap (mergeable as docs)
2. **PR #2 `timerloggedout-spec-patch-1`** - GHA Rust (narrow scope before merge)
3. **PR #3 `§01§/repository-hygiene`** (draft) - Untrack session stores (**priority §1b§**)

### Active Branches (Critical Evaluation)

**High Priority:**
- `recreate/refTemplates-skeleton` - Full metadata tree (merge to master)
- `§01§/repository-hygiene` - Session store §1b§ (PR #3, priority)
- `mistral/fixes-config-security` - config.py + §1b§ baseline

**Under §1a§:**
- `feat/gh-actions/deepseek-integrates-itself` - DeepSeek CI §20§ (fixed, ready)
- `critical-proposal` - §0a§ and architecture critique (PR #1)
- `vibe/mistralai-vibe-code-wrapper-*` - Mistral CLI + harvester

**§0c§ Health Notes (from RECON.md):**
- `master` @ `6ef0e2f` - Protected, recovery README + live inventory
- Legacy §a3§ (`export_poller.sh`, `activity_listener.py`) are candidates for archive
- Prefer `dispatch_pipeline` on cache write over dual maintenance

### Feature Requests
- Real-time chat feedback from listener
- Cross-session idea harvester
- Chronomancer §0c§ UI (visual tree)
- Listener auto-scribe (consolidate notes)
- Multi-account probing with image upload
- Tab completion for /sessions
- Expert-mode session creation

### Known Issues & Technical Debt
1. **Termux §14§ coupling** - Absolute §a3§ in REFERENCE_HUB need portability
2. **Silent `except: pass`** - In dispatch (deepcli + multi-ai-cli)
3. **Broken root symlinks** - §14§ coupling issues
4. **refTemplates gaps:**
   - Category 15 (Reverse Engineering) removed, needs metadata-only restore
   - Uncategorized: Haven/, Interpreted-Context-Methdology_fork/
5. **Session store hygiene** - PR #3 addresses credential-adjacent risk

## Troubleshooting

### Common Issues

**Listener Hangs:**
- Use `listener_control.py` for safe start/stop
- Check PID §0b§ in `.deepcli/`
- Ensure `stdin=DEVNULL` and `start_new_session=True` in subprocess calls

**Index Staleness:**
- Run `mirror.py` to check index freshness
- Rebuild with `map-build && map-func && fore`
- Check backup age before destructive rebuilds

**Task Not Found:**
- §1f§ `TASK_ID` in `master_tasks.json`
- Check `REFACTOR_GOAL` env var
- Fallback to `current_task.txt` in workspace

**Sentinel Failures:**
- §1a§ 5-gate output (§0b§, naming, duplicate, §16§, shockwave)
- Use `auto_repair.py` for simple fixes
- Manual §1a§ for complex issues

**Broken References:**
- Run `dangle_detector.py` for cross-ecosystem scan
- Check correlation index for file-path changes
- Use forensic toolchain for recovery

**CI/CD §20§ Failures:**
- §1f§ `OPERATOR_TOKEN` secret is configured
- Check WASM §0b§ §a3§ and commit hash
- §1a§ §20§ logs in GitHub Actions
- Ensure session cache is properly configured

## Additional Resources

- **Full §0a§:** See `archwiz/REFERENCE_HUB.md` for comprehensive links
- **Methodology:** `archwiz/METHODOLOGY_INDEX.md` documents what worked and what didn't
- **Procedures:** `archwiz/PROCEDURES.md` contains runbooks
- **Recovery:** `README.md` has detailed recovery procedures and refTemplates snapshot
- **Recon:** `docs/RECON.md` contains §04§/PR critique and proposals
- **§1c§ Map:** `workspace/llm_map/SYSTEM_MAP.md` - Complete §18§ catalogue
- **Data Flow:** `archwiz/DATA_FLOW_MANIFEST.md` - Complete data flow manifest

## Notes for AI §02§

1. **Always check indices first** - Use `archivist.py` to query existing knowledge before making changes
2. **Respect the verification pipeline** - Run Sentinel and §16§ before promoting changes
3. **Use feature branches** - Never commit directly to master
4. **Maintain provenance** - Update correlation and version indices when modifying §a1§
5. **Check for existing patterns** - §1a§ similar code before implementing new features
6. **§1b§ first** - Never expose tokens, keys, or credentials
7. **Document decisions** - Update relevant indices and §0a§
8. **Test incrementally** - Use sandbox for experiments, validate before promoting
9. **Respect ignore patterns** - Honor `.gitignore` and `.bobignore` exclusions
10. **Prefer metadata-only** - For refTemplates, use depth-1 sparse checkout with metadata only
11. **Check RECON.md** - §1a§ §0c§ health and known issues before major changes
12. **Use tokei** - Run `tokei --sort code` to understand codebase composition
13. **Follow CI/CD patterns** - Use existing GitHub Actions §a7§ as templates
14. **Cache aggressively** - Session caching reduces API calls and improves performance
15. **Monitor data flow** - Check DATA_FLOW_MANIFEST.md for §0b§ writer relationships
