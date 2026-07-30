# 🪄 LLM Ecosystem Mapper — vPRO

**A complete LLM‑native file indexer, function‑level code explorer, and dependency graph navigator for Termux/Android.**

---

## 📜 Overview

The LLM Ecosystem Mapper turns your chaotic home directory into a **queryable knowledge graph** of files, dependencies, and code definitions. It’s designed to be:

- **Fast** – incremental assembly from pre‑scanned data; no full re‑walk.
- **LLM‑efficient** – compact indices (`jsonl`), human‑readable maps, exact function signatures.
- **Profile‑driven** – target specific projects (e.g., `deepseek`, `harmony_hub`) without noise.
- **Graph‑aware** – dependency trees for any source file.
- **Termux‑native** – everything runs on Android with zero bloat.

**Core pipeline:**  
`step5_bloat.jsonl` + `file_graph.json` + provenance data → `build_final_all_profile.py` → `llm_index_compact.jsonl` + `CAVEMAN_INDEX.md` + `SYSTEM_MAP.md`  
`llm_index_compact.jsonl` → `func_indexer.py` → `func_index.jsonl` (every function/class definition).

---

## 📦 Installation

All tools live in `~/workspace/llm_map/`. If you followed the latest session, you already have:

| File | Role |
|------|------|
| `build_final_all_profile.py` | Profile‑aware main assembler |
| `generate_system_map.sh` | Generates `SYSTEM_MAP.md` from index |
| `func_indexer.py` | Extracts all function/class definitions |
| `func_index.jsonl` | Output of above |
| `graph_query.py` | Existing dependency query tool |
| `depgraph.sh` | Thin wrapper around `graph_query.py` |
| `depmenu.sh` | Interactive numbered menu for deps |
| `profile_filter.py` | Profile loading logic (imported by assembler) |
| `~/.config/llm_map/profiles/` | Custom profile JSON files |

**Required packages:** `python3`, `jq` (for function queries). `fzf` is optional for the advanced TUI.

```bash
pkg install -y jq python
```

---

## 🚀 Quick Start

1. **Set a profile (optional)**
```bash
export LLM_PROFILE=deepseek    # use your custom profile
# or `map-set deepseek` if you've sourced .bashrc
```

2. **Assemble the index**
```bash
map-build    # runs build_final_all_profile.py + generate_system_map.sh
```
The index will be filtered to the profile’s includes.
Output: `[1/6] Central: 4499 files … ✅ Final index: 4499 entries`

3. **Extract function definitions**
```bash
map-func     # generates func_index.jsonl
```

4. **Explore**
```bash
funcfind deepcli/core.py       # list all functions in that file
dep deepcli/core.py            # show dependency tree
depmenu                        # interactive file picker
```

---

## 🧠 Core Commands

| Alias | Command | Description |
|-------|---------|-------------|
| `map-build` | `cd ~/workspace/llm_map && python3 build_final_all_profile.py && ./generate_system_map.sh` | Full index rebuild with current `$LLM_PROFILE` |
| `map-func` | `python3 ~/workspace/llm_map/func_indexer.py` | Extract function/class defs from indexed source files |
| `funcfind <pattern>` | `jq -r 'select(.file | test("<pattern>")) | …' func_index.jsonl` | Search functions by filename (regex) |
| `dep <file>` | `bash ~/workspace/llm_map/depgraph.sh <file>` | Print dependency tree of a file |
| `depmenu` | `bash ~/workspace/llm_map/depmenu.sh` | Select file from list and view its dependencies |
| `map-set <name>` | `export LLM_PROFILE=<name>` | Switch active profile |

Original aliases still available:
```bash
map        # old alias (non‑profiled): builds full index
mupdate    # if you kept my PRO script (not recommended)
```

---

## 👥 Profiles

Profiles are JSON files in `~/.config/llm_map/profiles/`. They define which files to include/exclude.

Create a profile:
```bash
mkprofile <name> --include "dir1,dir2" --exclude "bloat_dir,tmp*"
```
Or write the JSON by hand:
```json
{
  "include": ["deepseek-cli", "deepseek_harvest_work", "harmony_hub"],
  "exclude": ["storage", "concat_work*"]
}
```
- `include` – only files whose path starts with one of these strings are kept.  
  The special value `["."]` (default) includes everything (except `exclude`).
- `exclude` – paths starting with any of these are dropped.

Usage:
```bash
export LLM_PROFILE=my_project
map-build
map-func
```
Now `llm_index_compact.jsonl`, `CAVEMAN_INDEX.md`, and `func_index.jsonl` will only contain those projects.

---

## 🔍 Function Index (Exact Research)

`func_index.jsonl` contains one JSON object per line for every function, method, or class:
```json
{"file": "deepcli/core.py", "name": "chat_completion", "kind": "de", "line": 375, "sig": "def chat_completion(token: str, prompt: str, ...", "doc": ""}
```
- `kind`: `"de"` (def), `"cl"` (class), `"function"` (JS/TS function or arrow).
- `line`: line number.
- `sig`: the actual signature line trimmed to 120 chars.
- `doc`: first docstring line if found (Python only).

Query examples:
```bash
funcfind deepcli/core.py

# Functions containing "cache" in any file
jq -r 'select(.name | test("cache")) | "`(.file):`(.line)  `(.name)  `(.sig[:60])"' func_index.jsonl

# All Python functions in harmoy_hub
jq -r 'select(.file | startswith("harmony_hub") and .kind=="de") | "`(.name) line `(.line)"' func_index.jsonl

# Count definitions per file
jq -r '.file' func_index.jsonl | sort | uniq -c | sort -rn | head
```

---

## 🕸️ Dependency Graph

The graph is built from `file_graph.json`. Commands:
- `dep <file>` – who depends on this file? (i.e., files that import it)
- `graph_query.py` can also do reverse queries (`--who-uses`) – check the script.

Data files:
- `file_graph.json` – `{ "file": ["dep1", "dep2"] }`
- `deps.jsonl` – edges as `{"from": "a.py", "to": "b.py", "type": "import"}` (optional).

TUI:
- `depmenu` gives a numbered list.
- If `fzf` is installed, `graph_fzf.sh` provides fuzzy filtering with a preview pane.

---

## 📄 Output Files

| File | Format | Purpose |
|------|--------|---------|
| `llm_index_compact.jsonl` | JSONL | Master machine index: every file with size, language, bloat flag, project, dependency count, AST snippet, temporal data. |
| `CAVEMAN_INDEX.md` | Markdown | Human overview: projects, top files. |
| `SYSTEM_MAP.md` | Markdown | Detailed per‑project listing. |
| `func_index.jsonl` | JSONL | All functions/classes with line numbers and signatures. |
| `ast_snippets.json` | JSON | Snippet hashes → signature text. |

---

## 🧪 LLM Integration

Quick injection into DeepSeek:
```bash
{
  echo "Here is a map of the current project ecosystem:"
  head -20 ~/workspace/llm_map/context_short.txt
  echo ""
  echo "Relevant functions for deepcli/core.py:"
  funcfind deepcli/core.py
  echo ""
  echo "Question: <your question>"
} > /tmp/llm_prompt.txt
# Then send via deepcli or paste.
```
Or use `dep` to pull in dependencies:
```bash
echo "Files that depend on deepcli/core.py:" >> /tmp/llm_prompt.txt
dep deepcli/core.py >> /tmp/llm_prompt.txt
```

Profile‑scoped context: Set `LLM_PROFILE` before building, then your prompt only contains relevant projects.

---

## ⚙️ Architecture (How It Works Under the Hood)

1. **Data collection** (existing earlier steps):
   - A scanner produces `step5_bloat.jsonl` and `full_map_output.txt`.
   - A dependency analyser generates `file_graph.json`.
   - Temporal and fragment provenance data come from the Chronos system.
2. **Assembly** (`build_final_all_profile.py`):
   - Reads `step5_bloat.jsonl`, applies profile filter.
   - Enriches each entry with dependency counts, AST snippets, timestamps, version info.
   - Writes `llm_index_compact.jsonl` and `CAVEMAN_INDEX.md`.
3. **Function extraction** (`func_indexer.py`):
   - Reads `llm_index_compact.jsonl`.
   - Opens each source file (respecting the profile) and extracts all definitions.
   - Writes `func_index.jsonl`.
4. **Graph queries**: `graph_query.py` parses `file_graph.json` to answer dependency questions.

Incremental update: If the upstream scanner (`step5_bloat.jsonl`) is updated, simply re‑run `map-build`. It’s fast because it only reassembles, not re‑walks.

---

## 🔧 Troubleshooting

- `map-build` shows “IndentationError”: The original `sed` patch failed. Use the manually corrected `build_final_all_profile.py` we created last.
- `funcfind` returns nothing: Ensure `func_index.jsonl` exists and paths don’t have a leading `./`. The path‑normalization script fixed that.
- `dep` says “No such file”: Make sure you’re passing a relative path from home (e.g., `deepcli/core.py`).
- Profiles not taking effect: Verify `$LLM_PROFILE` is exported and the JSON file exists in `~/.config/llm_map/profiles/`.

---

## 🏁 Roadmap

- **Function‑level dependency resolution**: cross‑reference `func_index.jsonl` with `file_graph.json` to answer “which functions call which”.
- **TUI integration**: embed `funcfind` and `dep` into the existing `deepcli-tui` or a new `dialog`‑based browser.
- **Auto‑LLM context builder**: given a user question, automatically pull relevant functions and dependencies.

---

Built for the Caveman Ecosystem. 🧬⚡🏹
