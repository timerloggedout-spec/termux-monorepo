
# Synthegration Ecosystem – Unified Plan

## 1. Full Inventory (what we have)

### Projects (top-level)
- **deepcli** – Python DeepSeek API CLI.
- **deepcli-tui** – Textual TUI.
- **deepseek-cli** – Node.js Puppeteer automation; holds upload-api.json (token) and cookies_2.json.
- **cli-synthegration** – Conversation synthesis, provenance, branching, token_provider, cedar_bridge.
- **termux-multi-agent** – Parallel agent pipeline with local_repo.db (nodes, edges, run_history).
- **synthegration-cli** – Node.js CLI wrapper.
- **harmonizer-prod_cli** – Rust project (early); workspace/reference/ holds many Python libs.
- **chronos_checkout** – Celery/Redis worker (not yet active).
- **cedar_forge** – new: capture/recorder.py, core/compression.py, core/executor.py, llm/client.py, tui/.

### Workspaces
- `cli-synthegration/workspace/provenance/` – file→session time correlation.
- `cli-synthegration/workspace/time_loop_accelerator/` – session productivity metrics (not true bottleneck detection; see §6).
- `cli-synthegration/workspace/cedarscript/` – CEDARscript API reference.
- `cli-synthegration/workspace/account2_expert/` – second account token & expert refactor.
- `cli-synthegration/workspace/caveman_map/` – ecosystem mapping & bloat scripts.
- `harmonizer-prod_cli/workspace/reference/` – extensive Python libs (branch_manager, conv_explorer, synthegration_index.py, etc.).

### Data Stores
- `local_repo.db` (termux-multi-agent) – nodes, edges, run_history.
- `hash_index.json` – 1857 SHA-256 file hashes.
- `comprehensive_provenance.json` – 750 files → 16 sessions.
- `session_productivity.json` – batch metrics.
- Test reports: `deepseek-cli/test-reports/report-*.json`.
- `cookies_2.json` – Puppeteer cookie array.

### Token Flow
- primary: deepcli.core.get_token() → upload-api.json bearer token.
- secondary: cookies_2.json → Puppeteer scripts.
- multi-agent imports token_provider from cli-synthegration.

### CEDARscript
- Installed: cedarscript_editor, cedarscript_ast_parser.
- Used in termux-multi-agent/src/orchestrator.py (parse_and_apply_cedar_diff).
- Template: config/templates/cedar_diff.txt.

---

## 2. Project Placement
All unification logic lives in **~/harmony_hub/** as a new top-level project.
It will not duplicate existing code; instead symlink stable tools, import from other projects, and contain only the glue layer, dynamic registry, and versioning pipeline.
Active development in ~/harmony_hub/workspace/; released modules move to ~/harmony_hub/src/.

---

## 3. Dynamic Command Registry
Goal: continuously updated, searchable map of all tools, sub-commands, and paths.

**Schema** (new DB ~/harmony_hub/registry.db):
CREATE TABLE tools (
    tool_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    path TEXT,
    project TEXT,
    description TEXT,
    commands TEXT,
    last_seen REAL
);
CREATE VIRTUAL TABLE tools_fts USING fts5(name, description, commands, content=tools, content_rowid=tool_id);

Population: bootstrap from existing CAVEMAN_INDEX.md, bin/ symlinks, argparse scans. Update nightly or on demand.

Usage: synthegrate map search "provenance"

---

4. Unified Versioning Pipeline
Integrates:
· Hash index → incremental file change detection.
· Provenance → which session produced which files.
· Run history → agent refactoring actions (success/fail).
· Exports → full conversation content (search & replay).

New tables (extend local_repo.db):
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    source_file TEXT,
    title TEXT,
    created_at REAL,
    content_hash TEXT
);
CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(session_id),
    role TEXT,
    content TEXT,
    timestamp REAL,
    content_hash TEXT
);
CREATE VIRTUAL TABLE messages_fts USING fts5(content, content=messages, content_rowid=rowid);

Deduplication via content_hash; unchanged exports skip reprocessing.

Success/Failure Tracking (extend existing run_history):
ALTER TABLE run_history ADD COLUMN input_hash TEXT;
ALTER TABLE run_history ADD COLUMN output_hash TEXT;
ALTER TABLE run_history ADD COLUMN verdict TEXT;

This enables pruning failed branches and reconstructing successful chains.

---

5. Immediate Termux-Agent Activation
1. Ensure run.py works with current token.
2. Give it a real refactoring task (e.g., apply a CEDARscript patch).
3. Observe output in run_history.
4. Parallelize more agents, feeding them from the session index.

---

6. Bottleneck Detection Protocol (Revised)
The time_loop_accelerator workspace currently measures session productivity (batch metrics). True bottleneck detection for agentic automation requires:

· Agent Contention Analysis: monitor run_history for overlapping tasks, timeouts, and resource limits.
· Failure Pattern Clustering: group failed runs by error signature.
· Throughput per Agent: successful patches per hour per role bracket.
· Bidding latency: time from task submission to agent assignment.

New module to be built in harmony_hub/workspace/bottleneck/.

---

7. ELO / Bidding System (design)
· Agents have bankrolls, role brackets.
· Successful refactors increase ELO; failures decrease.
· Bidding determines which agent gets a task.
· run_history captures performance; add elo_scores table.

---

Next Actions
1. Create ~/harmony_hub skeleton.
2. Build the command registry bootstrap script.
3. Extend local_repo.db schema with sessions/messages FTS.
4. Activate termux-multi-agent with a trial task.
5. Iterate.
