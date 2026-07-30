# Caveman Project Ecosystem — Master LLM Entry Point

## Quick Orientation
All paths relative to `/data/data/com.termux/files/home/` (Termux $HOME).
The ecosystem has 8 projects + 5 shared workspaces.

## Project Map

| Project | Purpose | Key Entry |
|---------|---------|-----------|
| `deepcli` | DeepSeek API CLI | `core.py`, `cli.py`, `deepapi.py`, `organizer.py` |
| `deepcli-tui` | Textual TUI | `tui.py` |
| `deepseek-cli` | Browser automation (Puppeteer) | `deepseek.js`, `deepterm-core.js`, `deepseek-stable.js` |
| `cli-synthegration` | Conversation synthesis, indexing, provenance, branching | `conv_explorer.py`, `conv_versioner.py`, `conv_branching.py`, `branch_manager.py`, `synthegration_index.py`, `success_metrics.py`, `loop_optimizer.py`, `cedar_bridge.py` |
| `termux-multi-agent` | Parallel agent refactoring pipeline | `src/orchestrator.py`, `src/parallel_agents.py`, `src/context_collector.py`, `src/db.py`, `src/telemetry.py`, `src/parser.py`, `src/sandbox.py`, `src/tool_registry.py`, `src/git_manager.py`, `src/dashboard.py` |
| `synthegration-cli` | Node.js CLI wrapper | `bin/synthegration`, `lib/index.js`, `lib/cli.js`, `lib/harmonizer.js` |
| `harmonizer-prod_cli` | ETL pipeline (shell+YAML) | `harmonizer.sh`, `config.ini`, `pipelines/*.yaml` |
| `chronos_checkout` | Celery/Redis background worker | `src/main.py`, `src/worker.py` |

## Workspaces (in-process modules)

| Workspace | Purpose | Key Scripts |
|-----------|---------|-------------|
| `cli-synthegration/workspace/provenance/` | File→session time-correlation index | `final_provenance.py`, `comprehensive_fast.py`, `fragment_matcher_fast.py`, `fix_timestamps.py`, `provenance_api.py`, `prov_query.sh` |
| `cli-synthegration/workspace/time_loop_accelerator/` | Session productivity & bottleneck detection | `session_productivity.py`, `accelerator.py`, `accelerator_v2.py`, `integrate_chronos.py` |
| `cli-synthegration/workspace/cedarscript/` | CEDARscript API reference & spec | `CEDARSCRIPT_REFERENCE.md`, `cedarscript_api_spec.json` |
| `cli-synthegration/workspace/account2_expert/` | Second-account token & expert-mode refactor | `auto_refactor.py` (dry-run default, `--execute` flag to run), `token_extractor.py` |
| `cli-synthegration/workspace/caveman_map/` | Ecosystem bloat discovery & map scripts | `map_final_with_watch.sh`, `discover_bloat.sh`, `bloat_exclusions.lst` |

## Key Indices & Data

| File | Purpose |
|------|---------|
| `cli-synthegration/workspace/provenance/comprehensive_provenance.json` | 750 files → 16 sessions, strategies: hash/similarity/time/fragment |
| `cli-synthegration/workspace/provenance/hash_index.json` | 1857 file SHA-256 hashes |
| `cli-synthegration/workspace/provenance/versioned_provenance_full.json` | Multi-version tracking per file |
| `cli-synthegration/workspace/provenance/tight_provenance.json` | Time-window matches (2269 files, broad) |
| `cli-synthegration/workspace/time_loop_accelerator/session_productivity.json` | Per-session batch metrics (16 sessions, 48 batches top session) |
| ``cli-synthegration/workspace/cedarscript/cedarscript_api_spec.json`` | Machine-readable CEDARscript API (2 classes, 37 methods) |

## Available CLI Commands

| Command | Location | Purpose |
|---------|----------|---------|
| `prov --summary` | `~/cli-synthegration/workspace/provenance/prov_query.sh` (symlinked to `$PREFIX/bin/prov`) | Provenance statistics |
| `prov --file <path>` | same | File origin (session, delay, strategy) |
| `prov --search <session_id>` | same | All files from a session |
| `synthegration` | `~/synthegration-cli/bin/synthegration` | Unified DeepSeek automation (chat, sessions, export, refactor, cedar, search, branches, etc.) |
| `ast-grep` | installed | AST pattern search |
| `tree` | installed | Directory tree |
| `cedarscript_editor` | Python package | CEDARScript AST parser and file editor |
| `deepcli` | `~/deepcli/deepcli.py` | DeepSeek API CLI (import, config, send, history, export, fork) |


## CEDARscript Python Usage

    from cedarscript_editor import CEDARScriptEditor, CEDARScriptASTParser

    # Parse CEDARScript commands from a string
    parser = CEDARScriptASTParser()
    commands, errors = parser.parse_script(script_text)

    # Apply commands to a file tree
    editor = CEDARScriptEditor(root_path="/path/to/project")
    editor.apply_commands(commands)

    # Locate an identifier in a file
    boundaries = editor.find_identifier(("file.py", file_content), marker)

    # Get character range for a region
    range_spec = editor.find_index_range_for_region(region, lines, resolver)

Full API:  (machine-readable)
Reference: 

## Python Libraries (pip-installed)

| Library | Purpose |
|---------|---------|
| `cedarscript_editor` | CEDARScript AST parsing, editing, identifier resolution |
| `textual` | TUI framework (used by deepcli-tui) |
| `rich` | Terminal formatting (used in provenance TUI) |

## Authentication
- **Account 1:** `cli-synthegration/token_provider.py` → `get_token()` or `Chronos.accelerator.get_token()` or `deepcli.core.get_token()`
- **Account 2:** `cli-synthegration/workspace/account2_expert/token_extractor.py` → `get_token()` from `cookies_2.json` (Puppeteer cookie array)
- **Existing extraction:** `termux-multi-agent/src/orchestrator.py` lines 21‑41 handles `cookies_2.json` when `--account cookies2` is passed
- **Token format:** Puppeteer export `{cookies: [{name, value, domain, ...}]}`, session cookie named `ds_session_id`
- **Symlink:** `~/deepseek-cli/cookies_2.json` → `~/storage/downloads/_doing/_1-build/DeepSeek/exports/cookies_2.json`

## Rebuild Pipeline

    cd ~/cli-synthegration/workspace/provenance
    python3 final_provenance.py          # hash index (chunked, Termux-safe)
    python3 comprehensive_fast.py        # provenance (checkpointed, resume-safe)
    cd ../time_loop_accelerator
    python3 session_productivity.py       # per-session metrics

## Security
- Tokens never logged or committed.
- All extraction logic in sandboxed workspaces.
- `cookies_2.json` read-only, never modified.
- `auto_refactor.py` defaults to dry-run; requires explicit `--execute` flag.
