# ArchWiz Monorepo — Critical Evaluation & Roadmap

> Evaluated: 2026-07-31. Stack: Python 3 / Bash / Rust (harmonizer) / TypeScript (commingle-swarm). Origin: Termux/Android monorepo.

---

## What This Is

A personal **agentic development environment** built around the DeepSeek AI API. The system closes a loop: the user chats with DeepSeek via a terminal CLI (`deepcli`), the ArchWiz cockpit auto-detects and executes code blocks from those conversations, results feed back into the knowledge graph, and a suite of forensic/verification tools (Sentinel, Archivist, Mirror, Dangle Detector) maintain quality and provenance.

### Pipeline Flow (high-level)
```
User → DeepSeek (via deepcli) → session cache (~/.deepcli/session_store/)
  → archwiz/dispatch_pipeline.py (called on every cache write)
    → activity_listener.py (extracts + deduplicates code blocks)
      → autonomous_runner.py / dispatch_task.py (sandboxed execution)
        → Sentinel (5-gate verification: file integrity, naming, duplicate, probe, shockwave)
          → promote.py (ascension to true_versions)
  → cli-synthegration (exports, versions, branches conversation history)
    → Chronos / time_loop_accelerator (success-only trunk management)
  → archwiz/archivist.py (query engine over all indices)
```

---

## How to Run (on Replit)

Most tools **cannot run as-is** on Replit — see the Termux coupling issue below. Once that is resolved, the entry point is:

```bash
python3 archwiz/archwiz.py        # Main cockpit (TUI menu)
python3 deepcli/deepcli.py new    # Start a new DeepSeek session
python3 deepcli/deepcli.py send "prompt here"
```

The DeepSeek integration requires a valid `ds_session_id` cookie and bearer token extracted from a browser session (see `deepcli/extract-token.js`).

---

## Critical Issues (Must Fix)

### 1. Termux Path Coupling — Blocks Everything
Almost all `subprocess.run(...)` calls in `archwiz/archwiz.py` use `os.path.expanduser('~/archwiz/...')`, which correctly resolves to `/home/runner/archwiz/...` on Replit. However:

- `archwiz/archwiz.sh` has a hardcoded Termux shebang: `/data/data/com.termux/files/usr/bin/bash`
- `cli-synthegration/workspace/reference/token_provider.py:5` hardcodes `/data/data/com.termux/files/home/deepcli`
- Top-level `enforce_hierarchy.sh` is a broken symlink → `/data/data/com.termux/files/home/workspace/scripts/enforce_workspace_hierarchy.sh`
- Many top-level symlinks (e.g., `dispatch_task.py`, `agent_shell.py`, `archaeologist.py`) point into the Termux filesystem — silently broken on Replit
- Large archive files (`archwiz/pointer_inverted.json`, session logs) contain historical Termux paths — low priority but confusing

**Fix:** Introduce `ARCHWIZ_HOME` environment variable (default: `~`). Replace all `~/archwiz/...` string construction with `Path(os.environ.get('ARCHWIZ_HOME', Path.home())) / 'archwiz' / ...`. Create a `config.py` in `archwiz/` that provides this resolution.

### 2. Silent Exception Swallowing in `core.py`
`deepcli/deepcli/core.py:58-59` has a bare `except Exception: pass` around the ArchWiz dispatch call. If the dispatch pipeline fails (missing file, import error, broken path), the failure is completely invisible. The user sees normal operation while the pipeline is dead.

```python
# current (line ~55-59)
try:
    ...dispatch...
except Exception:
    pass   # ← silent failure, no log, no warning
```

**Fix:** At minimum log to stderr: `except Exception as e: print(f"[archwiz dispatch] {e}", file=sys.stderr, flush=True)`

### 3. Duplicate Completion Paths (`send_message` vs `stream_completion`)
`deepcli/deepcli/core.py` has two chat completion implementations. The methodology log (`archwiz/METHODOLOGY_INDEX.md`) confirms `send_message` had missing `thinking_enabled`/`search_enabled` fields causing "Update to latest version" API errors. The fix was applied but the two paths remain diverged — any future change to one may miss the other.

**Fix:** Unify behind a single `_build_payload()` function. Both `send_message` and `stream_completion` call it. Remove the old `deepcli_old.py` and the backup `send_message_working` variant.

### 4. Hardcoded Session ID Default
`archwiz/archwiz.py:349` has a hardcoded session UUID as the fallback: `sid = '417ddd6d-9711-465d-ab90-c92cc04aeabf'`. This is a personal session ID that will silently target a non-existent session for any new user.

**Fix:** Remove the hardcoded default. If no `.json` files exist in the session store, prompt the user to start a session first.

### 5. Broken Symlinks at Root
Multiple top-level symlinks are permanently broken on any non-Termux host:
```
dispatch_task.py → /data/data/com.termux/files/home/workspace/llm_map/dispatch_task.py
agent_shell.py   → /data/data/com.termux/.../agent_shell.py
archaeologist.py → /data/data/com.termux/.../archaeologist.py
enforce_hierarchy.sh → /data/data/com.termux/.../enforce_workspace_hierarchy.sh
```

**Fix:** Either replace symlinks with relative path symlinks (pointing into `archwiz/` or `cli-synthegration/workspace/`) or remove them and update callers to use the canonical paths.

### 6. No Dependency Declaration
No `requirements.txt` exists. The Python environment depends on Termux `pkg` installs of: `curl_cffi`, `requests`, `ruff`, `ripgrep`, `fd`, `shellcheck`, `jq`, `entr`. On Replit, these must be installed explicitly.

**Fix:** Create `requirements.txt` at the root with all Python deps. Add a `setup.sh` that installs system tools via `nix` or the package skill.

---

## Important Warnings

### `.bak` File Pollution
The `archwiz/` directory contains **~25 timestamped `.bak` files** for `archwiz.py` and `live_view.py` alone (`archwiz.py.bak.1782737822`, `archwiz.py.bak.$(date +%H%M%S)`, etc.). These:
- Inflate repository size
- Make `ls` and `rg` results noisy
- One file is literally named `archwiz.py.bak.$(date +%H%M%S)` — the shell variable was never expanded

**Recommendation:** Move all `.bak` files to a `_archive/` folder or delete them. Git history is the canonical backup mechanism.

### commingle-swarm Has No Installed Dependencies
`commingle-swarm/` is a TypeScript/Node project with a `package.json` but no `node_modules/`. It is a self-contained P2P/PWA and appears disconnected from the rest of the monorepo (no import relationships found). It cannot be started without `npm install`.

---

## Optimization Proposals

### A. Unified Config Layer
Replace all scattered `os.path.expanduser('~/archwiz/...')` calls (~60+ occurrences in `archwiz.py` alone) with a single import:

```python
# archwiz/config.py
from pathlib import Path
ARCHWIZ_ROOT = Path(os.environ.get('ARCHWIZ_HOME', Path.home()))
ARCHWIZ_DIR  = ARCHWIZ_ROOT / 'archwiz'
DEEPCLI_DIR  = ARCHWIZ_ROOT / 'deepcli'
SESSION_STORE = ARCHWIZ_ROOT / '.deepcli' / 'session_store'
```

This makes the entire system relocatable and testable.

### B. `fzf` Integration (Shelved → Resolvable)
CONSIDERATIONS.md documents why fzf was shelved: it indexed 194k files without respecting `bloat_exclusions.lst`. The fix is already documented:
```bash
find ~ -type d | grep -vFf bloat_exclusions.lst | fzf
```
The keyboard issue was Termux-specific and does not apply on Replit. This is ready to implement.

### C. Real-Time Chat Feedback (ROADMAP Priority 🔴)
The listener executes code blocks but cannot send results back to the conversation. The methodology log proves `stream_completion()` is the correct path (Attempt C). The missing piece is a `report_back(session_id, text)` helper that calls `stream_completion` with the execution result as a user message.

### D. ChronoMancer Branch-Routing UI (ROADMAP 🟡)
`cli-synthegration/Chronos/accelerator.py` and `versioner.py` have the data layer. What's missing is a TUI visualizer for the branch tree — a read-only `curses` (or rich-text) panel showing fork points and child session previews.

### E. Self-Healing Sandbox (CONCEPT_INDEX: ❌ Not Built)
The full loop: Sentinel detects a failure → auto-repair attempts a fix → Probe validates → promote if clean. `auto_repair.py` handles the Sentinel REVIEW tier. The gap is the detection→dispatch→promote chain being fully automated without human `[1]` invocation. This is ~50 lines of glue in `autonomous_runner.py`.

### F. Web Dashboard (Replit-Native Extension)
The cockpit is currently terminal-only (stdin/stdout). On Replit, a lightweight Flask/FastAPI server exposing the same 19 menu actions as REST endpoints, with a minimal HTML dashboard, would make the environment accessible from any browser — including mobile. The pipeline status, activity feed, and live metrics are natural candidates for this.

### G. Expert-Mode Session Creation (ROADMAP 🟡)
Sessions created without the `thinking_enabled`/`search_enabled` fields default to non-Expert mode. The `create_session()` call in `core.py` should accept and forward these flags, and `cli.py`'s `new` command should expose `--expert / --no-expert`.

---

## Extension Ideas

| Idea | Effort | Value |
|------|--------|-------|
| Multi-account DeepSeek probing | Medium | Enables parallel task execution on account 2 |
| Cross-session idea harvester | Medium | Scan all exports for novel `#concept` tags across sessions |
| Prompt engine rotation (A/B test) | Low | Validate the CONSIDERATIONS.md prompt-phrase observations empirically |
| Commit notes scanner → CHANGES.md | Low | Auto-detect "what changed" summaries from session digests |
| Tab completion for `/sessions` | Low | Already partially designed in TUI |
| Sigil substitution engine (cedrlang) | High | Runtime compression protocol — reduces token usage |
| Export poller as a Replit workflow | Low | `export_poller.sh` is a natural persistent workflow |

---

## User Preferences

- Evaluate critically, propose optimizations and extensions
- Preserve existing structure and stack — do not migrate or restructure
- Check recent commits and branches before recommending changes
