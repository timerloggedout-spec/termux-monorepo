
# Harmony Hub — System Map & Versioning Architecture
*Generated from live exploration of the Termux ecosystem — $(date)*

## 1. Projects & Their Roles

| Project | Purpose | Key Files |
|---------|---------|-----------|
| `deepcli` | Python DeepSeek API CLI | `deepcli.py`, `core.py`, `organizer.py` |
| `deepcli-tui` | Textual TUI dashboard | `tui.py` (function‑based, 🌿 branch icon) |
| `deepseek-cli` | Puppeteer browser automation | `deepseek.js`, `upload-api.json` (token) |
| `cli-synthegration` | Conversation synthesis, provenance, branching | `conv_explorer.py`, `branch_manager.py`, `cedar_bridge.py` |
| `termux-multi-agent` | Parallel agent refactoring pipeline | `src/orchestrator.py`, `run.py`, `local_repo.db` |
| `synthegration-cli` | Node.js CLI wrapper | `bin/synthegration` (offline‑search, export, etc.) |
| `harmonizer-prod_cli` | Rust ETL project (early) | `src/main.rs`, `workspace/reference/` (Python libs) |
| `harmony_hub` | **Unification sandbox** (this project) | `bin/`, `workspace/`, `src/token_provider_v2.py` |
| `cedar_forge` | Capture, compression, LLM client | `capture/recorder.py`, `core/compression.py` |

## 2. Backup & Fallback Mechanisms

### File Backups
- `~/deepcli-tui/tui.py.bak` — previous working TUI version.
- `~/deepcli-tui/workspace/reference/tui.py` — reference copy.
- `~/harmony_hub/workspace/tui_repair/` — sandboxed copies of all three TUI versions.

### Token Backups
- `~/deepseek-cli/upload-api.json` — primary bearer token (nested in `uploadRequest.headers.authorization`).
- `~/deepseek-cli/cookies_2.json` — secondary account Puppeteer cookies.
- `~/.deepseek_api_key` — plain key (fallback).

### Provenance & Versioning
- `~/cli-synthegration/workspace/provenance/hash_index.json` — 1857 SHA‑256 file hashes (exact + norm).
- `~/cli-synthegration/workspace/provenance/comprehensive_provenance.json` — file → session mapping.
- `~/cli-synthegration/workspace/provenance/.comprehensive_checkpoint.json` — resume point for incremental runs.

### Database
- `~/termux-multi-agent/local_repo.db` — tables: `sessions`, `messages`, `messages_fts`, `run_history`, `nodes`, `edges`.
- `~/harmony_hub/registry.db` — tool/command registry with FTS.

### Restoration Process
1. Restore file from backup: `cp ~/deepcli-tui/tui.py.bak ~/deepcli-tui/tui.py`
2. Rebuild hash index: `cd ~/cli-synthegration/workspace/provenance && python3 final_provenance.py`
3. Re‑run comprehensive provenance: `python3 comprehensive_fast.py` (checkpointed, resumable)
4. Re‑index sessions for FTS: `python3 ~/harmony_hub/workspace/incremental_indexer_v2.py`
5. Rebuild FTS: `sqlite3 ~/termux-multi-agent/local_repo.db \"INSERT INTO messages_fts(messages_fts) VALUES('rebuild')\"`

## 3. Workspace & Sandbox Protocol

### Rule: Never modify originals.
- Active development: `~/harmony_hub/workspace/<feature>/`
- Released modules: `~/harmony_hub/src/`
- Agent workspace: `~/termux-multi-agent/workspace/` (sandbox)
- Agent writes **only** to `refactor_target.py` inside its workspace.
- Promotion to original requires manual `cp` after validation.

### Current Sandboxes
| Sandbox | Purpose |
|---------|---------|
| `harmony_hub/workspace/tui_repair/` | TUI field‑adapter fix & branch icon |
| `harmony_hub/workspace/elo/` | ELO updater & ratings |
| `harmony_hub/workspace/prompts/` | L33T prompt engine with randomisation |
| `harmony_hub/workspace/agent/` | Task wrappers (`task_with_context.py`, `direct_task.py`) |
| `termux-multi-agent/workspace/` | Agent runtime sandbox (`refactor_target.py`, `test_script.py`) |

## 4. Agent Pipeline (Actual Flow)

### Entry Points
- **Original**: `~/termux-multi-agent/run.py` (hardcoded goal, used as fallback)
- **Wrapper**: `~/harmony_hub/workspace/agent/run_with_elo.py` (adds ELO update after run)
- **Direct**: `~/harmony_hub/workspace/agent/direct_task.py` (bypasses run.py, imports orchestrator directly)

### Core Orchestrator
- `~/termux-multi-agent/src/orchestrator.py`
  - Class: `TermuxAgentOrchestrator`
  - Method: `run_refactor_pipeline(target_file, request_instruction, test_command, language)`
  - Uses `ast-grep` to scan functions
  - Calls DeepSeek API via `chat_completion()`
  - Applies patch via `parse_and_apply_cedar_diff()`
  - Now logs to `run_history` table (verdict, patch_content)
  - Now strips ANSI escape codes from LLM output
  - Model: `deepseek-chat` (logged as "DeepSeek API (try N, model=deepseek-chat)")

### ELO System
- `~/harmony_hub/workspace/elo/elo_updater.py` — reads `run_history.verdict`, updates `elo_ratings.json`
- `~/cli-synthegration/metrics/elo_ratings.json` — historical ELO data
- ELO history tracks every success/failure with old/new scores

### Fragment Matcher
- `~/cli-synthegration/workspace/provenance/fragment_matcher.py`
- Matches local functions/defs to code blocks from conversation exports
- Uses `difflib.SequenceMatcher` with threshold `SIMILARITY_FRAG = 0.7`
- Produces `fragment_provenance.json` linking code blocks to files
- Confirmed match for `patch_tui_branch.py` at similarity 0.57 against export

## 5. Chat‑as‑VCS Pipeline

    Export JSON (conversations.json)
        │
        ├── comprehensive_fast.py  →  hash_index.json
        │                           →  comprehensive_provenance.json
        │
        ├── incremental_indexer_v2.py  →  sessions table
        │                               →  messages table
        │                               →  messages_fts (FTS5)
        │
        ├── fragment_matcher.py  →  function‑level provenance
        │
        └── synthegration search "term"  →  FTS5 query (fast)

## 6. Investigator Patches

Location: `~/deepcli/investigator/` (35 Python scripts)
- Each is a code artifact generated during TUI refactoring sessions.
- They represent the **version history** of `tui.py`.
- Fragment matcher can link them back to their origin conversation sessions (similarity ≥ 0.57 confirmed).

## 7. Time Loop Accelerator

Location: `~/cli-synthegration/workspace/time_loop_accelerator/`
- Measures session productivity (batch metrics).
- `session_productivity.py` — per‑session batch data.
- `accelerator.py`, `accelerator_v2.py` — acceleration logic.
- **Proposed extension**: integrate with agentic roles to adaptively speed up or slow down task assignment based on success rates.

## 8. Manager Agent (Concept)

A meta‑agent that:
- Monitors `run_history` for success/failure patterns.
- Adjusts prompts based on high‑ELO session code blocks.
- Proposes improvements via fragment matcher diffing.
- Bids on tasks using ELO scores to assign the best agent.
- Can inject the 🌿 branch icon or other proven fixes into new TUI tasks automatically.

## 9. Quick Commands

| Command | Action |
|---------|--------|
| `synthegration search "term"` | Search conversations (FTS5) |
| `synthegration offline-search <dir> "term"` | Search local exports |
| `synthegration export <id>` | Export code blocks |
| `python3 ~/harmony_hub/workspace/agent/direct_task.py "goal" <file> <context_dir>` | Run agent |
| `python3 ~/harmony_hub/workspace/elo/elo_updater.py` | Update ELO ratings |
| `sqlite3 ~/termux-multi-agent/local_repo.db \"SELECT * FROM run_history\"` | View agent history |
| `python3 ~/harmony_hub/workspace/incremental_indexer_v2.py` | Index new sessions |
| `prov --summary` | Provenance statistics |
