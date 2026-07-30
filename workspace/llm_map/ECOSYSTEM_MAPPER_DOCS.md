# ```markdown
# 🪄 Ecosystem Mapper vPRO — Documentation

**Your LLM‑native project indexer, function researcher, and dependency explorer.**  
Built on the existing fast pipeline, now with profiles, full‑function extraction, and a dead‑simple graph viewer.

---

## 1. 🗺️ Overview

The mapper lives in `~/workspace/llm_map`. It combines multiple pre‑computed artefacts into a single, LLM‑efficient index (`llm_index_compact.jsonl`).  
We’ve added three new superpowers:

- **Profile filtering** – scan only the projects you care about.
- **Function‑level index** – every `def`, `class`, `function`, arrow function with line numbers and signatures.
- **Instant dependency graph** – see what a file imports with a single command.

The original `map` alias still works for a full global scan.

---

## 2. 🧪 Quick Start (after setup)

```bash
source ~/.bashrc

# Choose a profile (or skip to use everything)
export LLM_PROFILE=deepseek          # or 'default'

# Rebuild the compact index (fast, uses existing scan data)
map-build

# Extract all function/class definitions (takes ~20s)
map-func

# Find functions in a file
funcfind deepcli/core.py

# See the dependency tree of a file
dep deepcli/core.py

# Browse all files with dependencies interactively
depmenu
```

---

## 3. 📂 Key Files

| File | Description |
|------|-------------|
| `llm_index_compact.jsonl` | Master machine‑readable index (with `by`, `ts`, `as`, etc.) |
| `func_index.jsonl` | Every function/class definition (name, line, sig, doc) |
| `file_graph.json` | Raw dependency edges (used by `graph_query.py`) |
| `deps.jsonl` | Compact dependency list |
| `CAVEMAN_INDEX.md` | Human‑readable overview (auto‑generated) |
| `SYSTEM_MAP.md` | Project catalogue (also auto‑generated) |
| `~/.config/llm_map/profiles/` | Your custom profiles |

---

## 4. 🧬 Profiles

Profiles control which directories are included/excluded.
They live in `~/.config/llm_map/profiles/<name>.json`.

Create a new profile (example):

```bash
mkprofile deepseek --include "deepseek-cli,deepseek_harvest_work,harmony_hub,harmonizer-prod_cli,cli-synthegration,deepcli"
```

This creates a profile that only scans those directories.
To use it:

```bash
export LLM_PROFILE=deepseek
```

Then run `map-build`. The index and subsequent `func_indexer.py` will respect this scope.

Exclude directories:

```bash
mkprofile minimal --exclude "storage,concat_work*"
```

Default profile (all files, minus bloat) is used when `LLM_PROFILE` is not set.

---

## 5. 🔬 Function‑Level Research

The script `func_indexer.py` reads `llm_index_compact.jsonl`, opens each source file, and extracts all definitions into `func_index.jsonl`.

Usage:

```bash
map-func               # re‑extract (needs updated index first)
```

Querying (the `funcfind` alias):

```bash
funcfind deepcli/core.py
# Output: function name, line number, first 60 chars of signature
```

Pure `jq` for advanced queries:

```bash
# All functions named "send_message"
jq -r 'select(.name=="send_message") | "`(.file):`(.line)  `(.sig)"' func_index.jsonl

# All Python classes
jq -r 'select(.kind=="class") | "`(.file) — `(.name)"' func_index.jsonl
```

The index includes:
- `file` – relative path from `$HOME`
- `name` – function/class name
- `kind` – `def`, `function`, `class`
- `line` – line number (1‑based)
- `sig` – full signature line (trimmed to 120 chars)
- `doc` – docstring snippet (if any)

---

## 6. 🕸️ Dependency Graph

Show what a file depends on:

```bash
dep deepcli/core.py
```

This uses the existing `graph_query.py` (or `depgraph.sh`). Output is a flat list of files imported by the target.

Interactive menu (no `fzf` needed):

```bash
depmenu
```

Pick a file from a numbered list and see its dependencies.

Reverse lookup (what depends on a file?) – coming soon, but you can use:

```bash
python3 ~/workspace/llm_map/graph_query.py --depends-on some_file
# (currently only direct dependencies, not reverse)
```

---

## 7. 🤖 LLM Injection Recipes

**Minimal context for a coding question**

```bash
# Get the function signatures of the file you’re working on
funcfind deepcli/core.py > /tmp/funcs.txt

# Get its direct dependencies
dep deepcli/core.py >> /tmp/funcs.txt

# Now feed to deepcli:
# deepcli send -p "$(cat /tmp/funcs.txt) Your question here"
```

**Ultra‑compact system overview**

```bash
head -20 ~/workspace/llm_map/llm_index_compact.jsonl  # highest "used_by" files
```

---

## 8. ⚡ Aliases Reference

| Alias | Command |
|-------|---------|
| `map-build` | Rebuild index & maps (respects `$LLM_PROFILE`) |
| `map-func` | Re‑extract function definitions |
| `funcfind <file>` | Show functions in a file |
| `dep <file>` | Show dependencies of a file |
| `depmenu` | Interactive dependency browser |
| `mkprofile <name>` | Create a new profile (add `--include`/`--exclude`) |
| `map-set <profile>` | Switch profile (sets `LLM_PROFILE`) |

---

## 9. 🛠️ Under the Hood

The pipeline remains unchanged from the original (and it’s fast):

1. `build_final_all_profile.py` – assembles `step5_bloat.jsonl`, `file_graph.json`, temporal data, etc. into `llm_index_compact.jsonl` and `CAVEMAN_INDEX.md`.
2. `func_indexer.py` – parses source files for definitions.
3. `graph_query.py` – answers dependency questions from `file_graph.json`.

All scripts are in `~/workspace/llm_map`. The heavy lifting (file walking, bloat filtering) is done by earlier steps, so `map-build` runs in seconds even on Termux.

---

## 🧠 Tips for Termux

- The full index (`mfull` style) is **not** used anymore; we rely on the pre‑scanned bloat list. No hangs.
- If you add many new files, run the original `map` alias once to refresh the base scan, then use `map-build` with profiles.
- `func_indexer.py` reads every source file – on 4499 files it took ~20 seconds. That’s normal.

---

## 🎯 What’s Next?

- **Function‑level dependency tracing** (which function calls which)
- **Integration with your existing TUI** (`deepcli-tui`)
- **Automated context builder** for DeepSeek sessions

---

Built for speed, built for LLMs. LFG. 🔱🪄🏹


# 📎 Nested Index (original INDEX_OVERVIEW.md)

# LLM Index Overview

Generated from 8239 files, 0 with dependencies.
Provenance data available for 750 files.

## Top 20 files by dependents (most important)
- `.Xauthority` (0 dependents, 0 deps)
- `.bash_history` (0 dependents, 0 deps)
- `.bashrc` (0 dependents, 0 deps)
- `.deepcli_tui_history` (0 dependents, 0 deps)
- `.deepseek_api_key` (0 dependents, 0 deps)
- `.lesshst` (0 dependents, 0 deps)
- `.npmrc` (0 dependents, 0 deps)
- `.python_history` (0 dependents, 0 deps)
- `_1-Projects/a/.env` (0 dependents, 0 deps)
- `_1-Projects/a/.pylintrc` (0 dependents, 0 deps)
- `_1-Projects/a/arbitrage.log` (0 dependents, 0 deps)
- `_1-Projects/a/fix_imports.sh` (0 dependents, 0 deps)
- `_1-Projects/a/fix_imports_final.sh` (0 dependents, 0 deps)
- `_1-Projects/a/fixscript-1.sh` (0 dependents, 0 deps)
- `_1-Projects/a/fixscript-2.sh` (0 dependents, 0 deps)
- `_1-Projects/a/fixscript-3.sh` (0 dependents, 0 deps)
- `_1-Projects/a/fixscript-4.sh` (0 dependents, 0 deps)
- `_1-Projects/a/fixscript_3-1.sh` (0 dependents, 0 deps)
- `_1-Projects/a/mypy.ini` (0 dependents, 0 deps)
- `_1-Projects/a/requirements.txt` (0 dependents, 0 deps)

## Bloat summary
67 files flagged as bloat.

See `llm_index.jsonl` for full machine-readable index.

# 🆕 Recent Additions (outside of automated export)

- **`manager_agent.py`** — routing agent that directs queries to the best matching project agent.
- **`llm_mapper_pro.py`** — full-featured scanner with bloat filtering, profile support, dependency extraction.
- **Profile system** — `~/.config/llm_map/profiles/*.json` with `session_id` and account metadata.
- **`func_index.jsonl`** — all function/class definitions across 1765 files.
- **`file_graph.json`** — resolved dependency graph (241 edges).
- **`task_files_index.json`** — index of all task/sprint/todo files across the ecosystem.
- **`master_tasks.json`** — integrated work order tracking.
- **`depmenu.sh`** — interactive dependency browser.
- **`dep` alias** — now resolves imports through suffix matching.
- **Bloat management** — `discover_bloat.sh` and `map_final_with_watch.sh` for interactive exclusion.
- **Promotion validation** — workspace-level `promote.py` scripts with criteria checks.
- **Secondary account support** — `get_token_v2("secondary")` in orchestrator.

## 🚫 Exclusions Updated

- `.cargo/` added to bloat exclusions to avoid noise from Rust dependency source files.
# ```markdown
# 🧭 Router Agent (`router_agent.py`)

The Router Agent replaces the earlier Manager Agent concept (which conflicted with the multi-agent Manager role). It:
- Accepts a free‑text query from you.
- Scores all indexed projects based on function names and file path keywords.
- Cross‑references active sprints (`cli-synthegration/metrics/sprints.json`) and FORGE_OVERSIGHT delegations to recommend the exact agent and session already working on the topic.
- Prints the suggested command (e.g., `deepcli send` or `synthegration search`).

**Usage:**
```bash
python3 router_agent.py "How do I add a new API endpoint to deepcli?"
```

**Alias (add to .bashrc):**
```bash
alias route='python3 ~/workspace/llm_map/router_agent.py'
```

# 🔄 Promotion Pipeline (FORGE_OVERSIGHT)

All module promotion follows the 5‑step **FORGE_OVERSIGHT** protocol:

| Step | Action | Enforcement |
|------|--------|--------------|
| 1. Sandbox | All agent outputs go to designated sandbox dirs | `enforce_workspace_hierarchy.sh` |
| 2. Chronomancer review | Daily run_history review; fork if unverified > verified | Chronomancer agent |
| 3. Bidder validation | ELO bidder reads `run_history.validated` before wagering | Bidder agent |
| 4. Linguist compression | Inter‑agent messages compressed via `cid.py` | Linguist agent |
| 5. Promotion flag | `--promote` + timestamped backup required | `promote.py` (this tool) |

**Promotion command:**
```bash
python3 ~/workspace/llm_map/promote.py deepcli/core.py
```
This will:
1. Verify the file has a PASS verdict in `run_history.jsonl`.
2. Check for uncommitted changes in the source repo.
3. Create a timestamped backup in the next layer`s workspace.
4. Overwrite (with backup) the target file at the higher tier.
5. Log the promotion in `master_tasks.json`.

# 📋 Sprint Tracking Integration

Active sprints are tracked in `cli-synthegration/metrics/sprints.json` (11 sprints).  
The Router Agent automatically matches your query against sprint names, statuses, and actions.  
Sprints are also merged into `master_tasks.json` for unified task tracking.

# 🔐 Secondary Account Token Selection

The orchestrator now supports agent‑specific account selection via `get_agent_token()`.  
Agents of type `context_builder`, `chronos`, or `tui_dev` automatically use the **secondary account**.  
The primary account remains default for all others.

# 🧹 Bloat Management TUI

Interactive bloat exclusion is available via:
- `discover_bloat.sh` — scans for new bloat candidates, displays them with file counts/sizes, and lets you add them to `bloat_exclusions.lst`.
- `map_final_with_watch.sh` — prompts for new bloat candidates during a full map build.

# 📁 Workspace Hierarchy Enforcement

`enforce_workspace_hierarchy.sh` ensures every project has a `workspace/` directory and that mapping/bloat tools are placed in `cli-synthegration/workspace/caveman_map/`.  
Run it with:
```bash
bash ~/workspace/scripts/enforce_workspace_hierarchy.sh
```
# ```markdown
# 🔁 Time Loop Acceleration Branch (4_51GH7 Method)

The **Time Loop Acceleration Branch** is the Caveman Ecosystem`s primary update method.  
Every change — code, documentation, configuration — follows the same loop:

| Phase | Tool | Action |
|-------|------|--------|
| 🌿 **Fork** | `synthegration branch-fork`, Chronomancer | Isolate the change in a session‑tracked branch |
| 🔮 **ForeSight** | `router_agent.py --foresight`, `impact_oracle.py` | Assess Shockwave Index, Nexus Rank, and staged file blast radius |
| ⚡ **Generate** | `deepcli send`, Orchestrator CEDARscript | Apply the change as a structured diff |
| 🛡️ **Validate** | `run_history.jsonl`, `promote.py` gatekeeper | Require a PASS verdict from the exact session that made the change |
| 🚀 **Promote** | `promote.py` | Timestamped backup + move to next tier, logged in `master_tasks.json` |
| 🗂️ **Index** | `map-build`, `map-func`, `foresight_collect.py` | Rebuild master index, functions, and ForeSight state |
| 🏺 **Archaeologist** | `archaeologist.py` | Reconstruct full lifecycle timeline |

## 🛡️ Rule Enforcement Oversight

- **Promotion Gatekeeper** (`gatekeeper.py`) — blocks promotion without session‑matched PASS verdict.  
- **Metrics Log** (`metrics_log.jsonl`) — every Oracle run appends Shockwave/Nexus/Reliability scores.  
- **FORGE_OVERSIGHT** — daily Chronomancer review; Bidder validation; Linguist compression; `--promote` flag required.  
- **Sprint Tracking** — `sprints.json` and `master_tasks.json` track every active objective and its blocker.

## 🔧 Modifications Capability

All rules and resources are **self‑updating**:
- Edit `FORGE_OVERSIGHT.md` or `GRIMOIRE_DICTIONARY.md` in a forked session.  
- Validate with `impact_oracle.py` (documentation changes have low Shockwave).  
- Promote with `promote.py`.  
- The updated rules take effect immediately because all scripts read these files at runtime.

## 🧬 Evolution from Caveman

Caveman served as a seed concept, compressed into the `cid.py` pointer system alongside other seeded ideas.  
The ecosystem now operates under the **1337 l33t L33T lexicon** defined in `GRIMOIRE_DICTIONARY.md`.  
No component is static — every loop accelerates the next.

# ```markdown
# 🪄 Ecosystem Tool Categories
```
═══════════════════════════════════════════

📋 SESSION & EXPORT
  synthegration export-all          – Export all DeepSeek sessions
  synthegration export <id>         – Export code blocks from one session
  synthegration sessions [query]    – List/search conversations
  synthegration search <term>       – Full‑text search inside all messages

🗂️ CODEX & INDEXING
  synthegration codex-index         – Build codex from offline exports
  synthegration codex-search <t>    – Search codex by hash or content
  map-build                         – Rebuild master index (profiled)
  map-func                          – Re‑extract function definitions

🔀 BRANCH & FORK
  synthegration branches            – List conversation branches
  synthegration forks [session]     – Show asymmetric forks
  synthegration branch-fork <n>     – Fork a branch
  synthegration branch-merge <s> <t>– Merge branches
  synthegration branch-link <f> <t> – Link knowledge

🧠 AGENT & ORCHESTRATION
  deepcli send                      – Send prompt to DeepSeek
  deepcli-tui                       – Interactive TUI dashboard
  router_agent.py                   – Route query to best project/agent
  promote.py                        – Enforce FORGE_OVERSIGHT promotion
  gatekeeper.py                     – Block promotion without PASS verdict

🔍 RESEARCH & ANALYSIS
  funcfind <file>                   – Show functions in a file
  dep <file>                        – Show dependency tree
  depmenu                           – Interactive dependency browser
  impact_oracle.py <file>           – Shockwave Index, Nexus Rank, Reliability
  archaeologist.py <file> --full    – Full lifecycle timeline + co‑evolution
  foresight_collect.py              – Aggregate all metrics → foresight_state.json
  route --foresight "query"         – Router + ForeSight domain map

🛡️ MAINTENANCE
  map-build                         – Rebuild index
  map-func                          – Re‑extract functions
  discover_bloat.sh                 – Find new bloat candidates
  enforce_workspace_hierarchy.sh    – Ensure workspace scaffolding

📊 METRICS & LOGGING
  foresight_collect.py              – Generate foresight_state.json
  impact_oracle.py                  – Compute Shockwave/Nexus/Stability/Echo
  master_tasks.json                 – Unified task/sprint tracker
  run_history.jsonl                 – Agent test verdicts
```


## 🎯 Milestone: Pipeline Complete — 2026-06-10 18:41 UTC

**33 tasks done, 0 pending.**

### Keywords
`4_51GH7` `ForeSight` `Time Loop` `Self‑Bootstrapping Ecosystem`
`Automated Dispatch` `Adaptive Memory` `Chunked 9‑gzip`
`Fragment Similarity` `Session‑Matched Promotion` `Parallel Agents`
`1337 L33T Grimoire` `FORGE_OVERSIGHT` `Archaeologist`

### What was completed
- All three large databases (correlation, message, versioned provenance) chunked and gzip‑compressed
- Adaptive dispatch with dynamic memory management and crash‑safe resume
- Full promotion pipeline: orchestration → verdict → gatekeeper → promote
- Forensic archaeology across multiple projects (_1‑Projects/a, _1‑Projects/b)
- Custom versioning prompt for powerlevel10k/zsh
- Workspace‑check and account‑activity utility belt commands
- Context collector optimization (full / compact / minimized modes)
- Session store compression and incremental sync
- Unified CLI query extraction library
- Commit‑notes tool with Router + Archaeologist integration
- Emoji markers for code‑block outcome status in TUI
- Deduplication of true_versions.json with fragment similarity
- Truth‑report with session filtering
- Keepalive ping in watcher cycle
