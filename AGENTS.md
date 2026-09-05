# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Governance & Process (Read First)

1. **This file** (`AGENTS.md`) - Technical guidance and codebase overview
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-agent)
5. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
6. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — living board
6b. [`docs/ops/ISSUE-175-MATRIX.yaml`](docs/ops/ISSUE-175-MATRIX.yaml) — operator matrix
6c. [`ml_pipelines/`](ml_pipelines/) — observe-mode GitHub ML pipelines
7. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
8. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, merit path, CRDT, optional Raft-strict

After this governance sequence, use [`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md) to route the task to one verified component or process card before loading deeper source.

For any nontrivial code, workflow, consolidation, or documentation change, perform bounded context reconnaissance with [`docs/icm/processes/context-relationship-reconnaissance.md`](docs/icm/processes/context-relationship-reconnaissance.md) and the project-local [context-relationship-graph skill](.agents/skills/context-relationship-graph/SKILL.md). Query `workspace/llm_map/context_relationships/` by an exact file, symbol, PR, issue, label, scope, or direct GitHub issue/comment/review permalink when the index is current; use the file-review timeline for a focused review history. Keep **verified evidence** (including native timeline events) separate from scored **candidates**; candidates prompt review and never justify an asserted fact or an autonomous GitHub write. Do not rebuild or edit the generated index manually—use its trusted workflow or an explicitly authorized operator build.

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## Hard Rules

- Target **`master`** for integration work.
- Both gates must pass before merge:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** wholesale merge of PR #6 (TER-9) or PR #2 (Rust CI) — see disposition comments.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write Review log or DEBATE.md.
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster (not a single-agent monopoly).

## Preferred Execution Loop

```text
registry.yaml → pick todo item → branch from master
  → implement → PR with Implements: ID → gates green → merge
  → update ITEMS.md status
```

## Security

Credential rotation and history rewrite require Operator (human) authorization.
See `docs/SECURITY-REMEDIATION.md`.
---

# Technical Documentation

## Project Overview

This is a **Termux-based multi-agent automation monorepo** running on Android. It orchestrates AI-powered development workflows through multiple specialized CLI tools and autonomous agents. The system integrates with DeepSeek API, manages conversation branching, performs code forensics, and maintains comprehensive knowledge indices.

**Core Technologies:**
- **Language:** Python 3 (primary), Node.js (supporting), Bash, Rust (selective components)
- **Platform:** Termux on Android
- **AI Integration:** DeepSeek API, multi-model support
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
3. **Termux Multi-Agent** - Agent provisioning and orchestration
4. **CLI Synthegration** - Conversation synthesis and branching
5. **Harmonizer** - Unified automation interface
6. **Central Mapper** - AST indexing and dependency graph generation

## Navigation & Documentation

**Primary Navigation (in priority order):**
1. `archwiz/TOOL_INDEX.md` - 28 tools / 7 categories (cockpit, forensic, autonomous, verification)
2. `archwiz/CONCEPT_INDEX.md` - Concepts + status + feature backlog
3. `archwiz/REFERENCE_HUB.md` - Links to data flow, system map, indices
4. `archwiz/METHODOLOGY_INDEX.md` - Approaches tried, failures, successes
5. `archwiz/PROCEDURES.md` - Runbooks and active tasks
6. `docs/RECON.md` - Branch/PR critique and proposals
7. `README.md` - Recovery documentation and project inventory
8. `workspace/llm_map/SYSTEM_MAP.md` - Complete project catalogue (8,239 files indexed)
9. `archwiz/DATA_FLOW_MANIFEST.md` - Complete data flow manifest (1.5MB, 8,400 lines)

**Quick Command Reference:**
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

## Core Projects

### 1. DeepCLI (`deepcli/`)
DeepSeek-oriented CLI with session management, streaming, thinking mode, and export capabilities.

**Entry Points:**
- `deepcli.py` - Main CLI launcher
- `deepapi.py` - API interface
- `deepseek_proxy.py` - Proxy layer
- `ci_mode.py` - CI/CD integration entry point
- `ci_agent.py` - GitHub Actions agent logic

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

**CI/CD Integration:**
- GitHub Actions workflow: `.github/workflows/deepseek-ci.yml`
- Triggers on PR events (opened, synchronize, reopened)
- Uses PoW WASM solver for authentication
- Automated PR review and commenting

**Related:** `deepcli-tui/` (TUI with conversation tree), `.deepcli/` (config), `deepseek-cli/` (includes deepterm)

### 2. Termux Multi-Agent (`termux-multi-agent/`)
Multi-agent orchestration system for provisioning, running, and managing autonomous agents.

**Key Components:**
- `provision_agent.py` - Agent provisioning
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
- `branch_manager.py` - Conversation f0rk management
- `conv_branching.py` - Branch/fork API implementation
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
- `synthegration_exports/` - 3,281 exported session files
- `workspace/correlation/` - Session-to-file correlation index
- `workspace/provenance/` - Version tracking and provenance
- `codex/message_index.json` - Full-text message search index

### 4. ArchWiz (`archwiz/`)
Central automation cockpit with indexing, provenance tracking, and recovery tools.

**Tool Categories (28 tools total):**

**Cockpit & Pipeline:**
- `archwiz.py` - Dashboard with 16 options + 3 mode toggles
- `activity_listener.py` - Auto-executes assistant code blocks
- `live_view.py` - Review panel with /exec, /skip, /send commands
- `debug_daemon.py` - Watches failures, auto-fixes with ruff/shellcheck
- `listener_control.py` - PID-based safe start/stop

**Forensic & Version Control:**
- `forensic_toolchain.py` - Fragment matcher, similarity scan, correlation sc0ut
- `correlation_scout.py` - Traces file-path changes across versions
- `fragment_matcher.py` - Function-level provenance
- `restore_version.py` - Provenance-based code resurrection

**Autonomous Operation:**
- `autonomous_runner.py` - Dispatches pending tasks with memory awareness
- `dispatch_task.py` - Sandboxed execution with Sentinel verification
- `task_builder.py` - Interactive task creation
- `auto_repair.py` - Auto-fixes Sentinel REVIEW issues

**Verification & Testing:**
- `sentinel.py` - 5-gate verification (file integrity, naming, duplicate, pr0b3, shockwave)
- `probe.py` - Syntax/import/test validation
- `mirror.py` - Self-critique for task hygiene, index freshness
- `dangle_detector.py` - Cross-ecosystem broken reference scanner

**Knowledge & Memory:**
- `archivist.py` - Local query engine across all indices
- `tasque_declare.py` - Declares completion to taDone.md
- `timeline_editor.py` - Full DB editor + archaeologist
- `narrative.py` - Chronological feed of pipeline events
- `lexicon_harvest.py` - Session scanning for novel terms
- `name_forge.py` - Gr1m01r3-powered tool naming

**Documentation Pipeline:**
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
- `task_files_index.json` - All task/sprint/todo files
- `file_graph.json` - Dependency graph
- `deps.jsonl` - Dependency relationships

**Build Scripts:**
- `build_all.py` - Complete index rebuild
- `build_llm_index.py` - LLM index generation
- `build_ast_index_from_existing.py` - AST index from existing data
- `build_graph_fast.py` - Fast graph generation

### 6. Harmonizer (`harmonizer-prod_cli/`)
Production Harmonizer CLI providing unified DeepSeek automation: sessions, export, search, sync.

### 7. Supporting Projects
- `harmony_hub/` - Harmony hub integration
- `multi-ai-cli/` - Multi-model CLI surface
- `commingle-swarm/` - Template/scavenge-only (not first-class runtime)
- `colab-cli/` - Colab CLI tooling
- `exchanges/` - Exchange/market API code
- `appliedSxi/maxc/` - Applied Sxi/Max work

## Development Workflow

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

**Run Autonomous Agent:**
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

**Validation Pipeline:**
```bash
# Sentinel 5-gate verification
python3 archwiz/sentinel.py <file>

# Probe syntax/import/test validation
python3 archwiz/probe.py <file>

# Mirror self-critique
python3 archwiz/mirror.py
```

**Agent Test Runs:**
- Test verdicts tracked in `termux-multi-agent/run_history.jsonl`
- Dashboard available via `termux-multi-agent/dashboard.py`

## CI/CD & GitHub Actions

### Active Workflows

**DeepSeek CI (`.github/workflows/deepseek-ci.yml`):**
- Triggers: PR opened, synchronize, reopened, manual dispatch
- Features: Automated PR review, code analysis, comment posting
- Authentication: PoW WASM solver (deepseek.wasm + pow_solver.js)
- Session caching for performance
- Artifact upload for results

**Other Workflows:**
- `agent-continuous-ops.yml` - Continuous agent operations
- `agent-feedback-linear-sync.yml` - Linear issue sync
- `agent-jules-on-issues.yml` - Jules agent for issues
- `agent-review-auto-jules.yml` - Automated Jules reviews
- `gemini-*.yml` - Gemini integration workflows
- `peer-review-orchestrator.yml` - Multi-peer review coordination
- `publish-wiki.yml` - Wiki publishing

### GitHub Actions Best Practices
- Use `OPERATOR_TOKEN` secret for authenticated operations
- Cache session data to reduce API calls
- Fetch WASM files from correct commit hash
- Use metadata-only artifacts for large outputs
- Implement proper error handling and timeouts

## Development Conventions

### Code Style
- **Python:** Follow PEP 8, use `ruff` for linting and auto-fix
- **Shell:** Use `shellcheck` for validation
- **Logging:** Use existing patterns or language standard logging library/facade
- **Performance:** Check performance implications of changes
- **Security:** Review security considerations, especially for API tokens and credentials

### File Organization
- **Indices:** Stored in `workspace/llm_map/`, `archwiz/`, `cli-synthegration/workspace/`
- **Configuration:** Project-specific configs in respective directories
- **Backups:** `.bak` files created automatically, large JSONL indices backed up externally
- **Ignore Patterns:** Respect `.gitignore` and `.bobignore` (see root `.bobignore` for exclusions)

### Commit Practices
- Use feature branches (`feature/*`) for all changes
- Never commit directly to `master` without review
- Reference task IDs in commit messages when applicable
- Keep commits focused and atomic
- Follow conventional commit format when possible

### Security & Secrets
- **Never commit:** API keys, tokens, cookies, session stores
- **Sensitive files:** `cookies_2.json`, `*_api_key`, `*.env`, `*.pem`, `*.key`
- **Session stores:** Must not be tracked in Git (see PR #3 `agent/repository-hygiene`)
- **Backup:** Large JSONL indices externally before destructive rebuilds
- **Browser data:** `deepcli/browser-data*/` and `deepseek-cli/browser-data*/` contain sensitive cookies

### Autonomous Operation
- **Task Sources:** `master_tasks.json`, `TASK_ID` env var, `REFACTOR_GOAL` env var, `current_task.txt`
- **Execution:** Sandboxed with Sentinel verification
- **Memory:** Memory-aware dispatching with crash recovery
- **Validation:** Auto-repair for simple issues, manual review for complex ones

### Index Management
- **Pointer Index:** CID-style bookmarking (`archwiz/pointer_index.json`)
- **Correlation Index:** Session-to-file links (`cli-synthegration/workspace/correlation/`)
- **True Versions:** Version hash tracking (`cli-synthegration/workspace/provenance/true_versions.json`)
- **Message Index:** Full-text session messages (`cli-synthegration/codex/message_index.json`)
- **Task Files:** All task/sprint/todo files (`workspace/llm_map/task_files_index.json`)
- **Data Flow Manifest:** Complete file writer tracking (`archwiz/DATA_FLOW_MANIFEST.md`)

### Forensic Recovery
- **Staged Blocks:** `archwiz/staging_blocks.json`
- **Pipeline:** Extract with forensic toolchain → restore with `restore_version.py`
- **Backups:** Automatic `.bak` creation before modifications
- **Restore Points:** Up to 5 per file (0 = initial state)

## Key Concepts

### Core Abstractions
- **TasQue:** Task completion declaration system (ta'Done)
- **Sentinel:** 5-gate verification (file, naming, duplicate, pr0b3, shockwave)
- **Archivist:** Local-only query engine across all indices
- **Pr0b3:** Syntax/import/test validation
- **Mirror:** Self-critique for task hygiene and index freshness
- **Dangle Detector:** Cross-ecosystem broken reference scanner
- **Pointer Index:** CID-style bookmarking of messages, tables, data
- **Narrative Feed:** Chronological event stream of pipeline events

### Reserved Concepts (Not Yet Implemented)
- **Spellbook:** Library of system abilities
- **Rune:** Short hash pointer (CID-style)
- **Sigil:** Substitution engine for runtime compression
- **Chr0n0:** Time-loop agent with success-only trunks
- **Self-healing Sandbox:** Detect error → request fix → validate → promote

### Methodology Evolution
| Phase | What We Tried → What Stuck |
|-------|---------------------------|
| **Listener lifecycle** | `nohup` → `pkill -f` → `Popen` → `listener_control.py` (PID file) |
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
- **entr** - File watcher
- **tokei** - Code statistics and line counting

## Open Work & Priorities

### Active PRs (as of 2026-08-01)
1. **PR #1 `critical-proposal`** - Critical eval + roadmap (mergeable as docs)
2. **PR #2 `timerloggedout-spec-patch-1`** - GHA Rust (narrow scope before merge)
3. **PR #3 `agent/repository-hygiene`** (draft) - Untrack session stores (**priority security**)

### Active Branches (Critical Evaluation)

**High Priority:**
- `recreate/refTemplates-skeleton` - Full metadata tree (merge to master)
- `agent/repository-hygiene` - Session store security (PR #3, priority)
- `mistral/fixes-config-security` - config.py + security baseline

**Under Review:**
- `feat/gh-actions/deepseek-integrates-itself` - DeepSeek CI workflow (fixed, ready)
- `critical-proposal` - Documentation and architecture critique (PR #1)
- `vibe/mistralai-vibe-code-wrapper-*` - Mistral CLI + h4rv35t3r

**F0rk Health Notes (from RECON.md):**
- `master` @ `6ef0e2f` - Protected, recovery README + live inventory
- Legacy paths (`export_poller.sh`, `activity_listener.py`) are candidates for archive
- Prefer `dispatch_pipeline` on cache write over dual maintenance

### Feature Requests
- Real-time chat feedback from listener
- Cross-session idea h4rv35t3r
- Chr0n0 f0rk UI (visual tree)
- Listener auto-scribe (consolidate notes)
- Multi-account probing with image upload
- Tab completion for /sessions
- Expert-mode session creation

### Known Issues & Technical Debt
1. **Termux path coupling** - Absolute paths in REFERENCE_HUB need portability
2. **Silent `except: pass`** - In dispatch (deepcli + multi-ai-cli)
3. **Broken root symlinks** - Path coupling issues
4. **refTemplates gaps:**
   - Category 15 (Reverse Engineering) removed, needs metadata-only restore
   - Uncategorized: Haven/, Interpreted-Context-Methdology_fork/
5. **Session store hygiene** - PR #3 addresses credential-adjacent risk

## Troubleshooting

### Common Issues

**Listener Hangs:**
- Use `listener_control.py` for safe start/stop
- Check PID file in `.deepcli/`
- Ensure `stdin=DEVNULL` and `start_new_session=True` in subprocess calls

**Index Staleness:**
- Run `mirror.py` to check index freshness
- Rebuild with `map-build && map-func && fore`
- Check backup age before destructive rebuilds

**Task Not Found:**
- Verify `TASK_ID` in `master_tasks.json`
- Check `REFACTOR_GOAL` env var
- Fallback to `current_task.txt` in workspace

**Sentinel Failures:**
- Review 5-gate output (file, naming, duplicate, pr0b3, shockwave)
- Use `auto_repair.py` for simple fixes
- Manual review for complex issues

**Broken References:**
- Run `dangle_detector.py` for cross-ecosystem scan
- Check correlation index for file-path changes
- Use forensic toolchain for recovery

**CI/CD Workflow Failures:**
- Verify `OPERATOR_TOKEN` secret is configured
- Check WASM file paths and commit hash
- Review workflow logs in GitHub Actions
- Ensure session cache is properly configured

## Additional Resources

- **Full Documentation:** See `archwiz/REFERENCE_HUB.md` for comprehensive links
- **Methodology:** `archwiz/METHODOLOGY_INDEX.md` documents what worked and what didn't
- **Procedures:** `archwiz/PROCEDURES.md` contains runbooks
- **Recovery:** `README.md` has detailed recovery procedures and refTemplates snapshot
- **Recon:** `docs/RECON.md` contains branch/PR critique and proposals
- **System Map:** `workspace/llm_map/SYSTEM_MAP.md` - Complete project catalogue
- **Data Flow:** `archwiz/DATA_FLOW_MANIFEST.md` - Complete data flow manifest

## Notes for AI Agents

1. **Always check indices first** - Use `archivist.py` to query existing knowledge before making changes
2. **Respect the verification pipeline** - Run Sentinel and Pr0b3 before promoting changes
3. **Use feature branches** - Never commit directly to master
4. **Maintain provenance** - Update correlation and version indices when modifying files
5. **Check for existing patterns** - Review similar code before implementing new features
6. **Security first** - Never expose tokens, keys, or credentials
7. **Document decisions** - Update relevant indices and documentation
8. **Test incrementally** - Use sandbox for experiments, validate before promoting
9. **Respect ignore patterns** - Honor `.gitignore` and `.bobignore` exclusions
10. **Prefer metadata-only** - For refTemplates, use depth-1 sparse checkout with metadata only
11. **Check RECON.md** - Review f0rk health and known issues before major changes
12. **Use tokei** - Run `tokei --sort code` to understand codebase composition
13. **Follow CI/CD patterns** - Use existing GitHub Actions workflows as templates
14. **Cache aggressively** - Session caching reduces API calls and improves performance
15. **Monitor data flow** - Check DATA_FLOW_MANIFEST.md for file writer relationships
