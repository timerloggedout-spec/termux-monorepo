# ArchWiz Monorepo — Critical Evaluation & Roadmap

> Evaluated: 2026-07-31. Stack: Python 3 / Bash / Rust (harmonizer) / TypeScript (commingle-swarm). Origin: Termux/Android monorepo.

---

## What This Is

A personal **agentic development environment** built around the DeepSeek AI API. The system closes a loop: the user chats with DeepSeek via a terminal CLI (`deepcli`), the ArchWiz cockpit auto-detects and executes code blocks from those conversations, results feed back into the knowledge graph, and a suite of forensic/verification tools (Sentinel, Archivist, Mirror, Dangle Detector) maintain quality and provenance.

### Pipeline Flow (high-level)
```text
User → DeepSeek (via deepcli TUI / cli.py)
  → core.py stream_completion() → session cache (~/.deepcli/session_store/)
    → dispatch_pipeline.py (called on every cache write, via core.py hook)
      → autonomous_runner.py / dispatch_task.py (sandboxed execution)
        → Sentinel (5-gate verification: file integrity, naming, duplicate, probe, shockwave)
          → promote.py (ascension to true_versions)
  → cli-synthegration (exports, versions, branches conversation history)
    → Chronos / time_loop_accelerator (success-only trunk management)
  → archwiz/archivist.py (query engine over all indices)
```

> **Note:** `export_poller.sh` and `activity_listener.py` are legacy execution paths — the canonical code-block execution flow runs through the TUI and `core.py`'s cache-write hook (`dispatch_pipeline.py`). The poller/listener represent an earlier, now-superseded approach and should be treated as candidates for removal or archival rather than maintained in parallel.

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

> **Key constraint:** Pure relative paths are not a safe fix here — the tools are invoked from different working directories (cockpit, listener, dispatch, TUI), so a relative path resolves differently depending on the call site. The correct solution is an **environment-aware intermediary layer**, not relative paths.

**Fix:** Create `archwiz/config.py` as a single source of truth for all paths, resolved at import time via an environment variable:

```python
# archwiz/config.py
import os
from pathlib import Path

# Set ARCHWIZ_ENV=termux | replit | local (auto-detected if unset)
_env = os.environ.get('ARCHWIZ_ENV', '').lower()
if not _env:
    _env = 'termux' if Path('/data/data/com.termux').exists() else 'replit'

if _env == 'termux':
    ARCHWIZ_ROOT = Path('/data/data/com.termux/files/home')
else:
    ARCHWIZ_ROOT = Path(os.environ.get('ARCHWIZ_HOME', Path.home()))

ARCHWIZ_DIR   = ARCHWIZ_ROOT / 'archwiz'
DEEPCLI_DIR   = ARCHWIZ_ROOT / 'deepcli'
SESSION_STORE = ARCHWIZ_ROOT / '.deepcli' / 'session_store'
WORKSPACE_DIR = ARCHWIZ_ROOT / 'workspace'
```

All scripts import from `config.py` instead of constructing paths inline. `ARCHWIZ_ENV` overrides auto-detection for edge cases. This is portable across Termux, Replit, and local Linux without changing any call-site code.

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
```text
dispatch_task.py     → /data/data/com.termux/files/home/workspace/llm_map/dispatch_task.py
agent_shell.py       → /data/data/com.termux/.../agent_shell.py
archaeologist.py     → /data/data/com.termux/.../archaeologist.py
enforce_hierarchy.sh → /data/data/com.termux/.../enforce_workspace_hierarchy.sh
```

**Fix:** Either replace symlinks with relative path symlinks (pointing into `archwiz/` or `cli-synthegration/workspace/`) or remove them and update callers to use the canonical paths.

### 6. No Dependency Declaration *(partially resolved — see Branch Evaluations below)*
~~No `requirements.txt` exists.~~ `requirements-base.txt` and `setup.sh` now exist (landed in `mistral/fixes-config-security`). Remaining gap: `requirements-base.txt` covers only `curl-cffi`, `requests`, `websockets` — system tools (`ruff`, `ripgrep`, `fd`, `shellcheck`, `jq`, `entr`) still require manual install. `multi-ai-cli/requirements.txt` exists independently but is not reconciled with the root baseline.

**Fix remaining:** Add system-tool installation to `setup.sh` via `nix-env` or document them in a `PREREQUISITES.md`. Reconcile `multi-ai-cli/requirements.txt` with `requirements-base.txt` — avoid two separate dependency tracks diverging silently.

---

## Important Warnings

### `.bak` File Pollution
The `archwiz/` directory contains **~25 timestamped `.bak` files** for `archwiz.py` and `live_view.py` alone (`archwiz.py.bak.1782737822`, `archwiz.py.bak.$(date +%H%M%S)`, etc.). These:
- Inflate repository size
- Make `ls` and `rg` results noisy
- One file is literally named `archwiz.py.bak.$(date +%H%M%S)` — the shell variable was never expanded

**Recommendation:** Move all `.bak` files to a `_archive/` folder or delete them. Git history is the canonical backup mechanism.

### commingle-swarm Is a Template / Scavenging Source
`commingle-swarm/` is a **cloned/forked external repo** kept in the monorepo as a structural reference and code-scavenging template, not a first-class project to run or maintain. It is intentionally disconnected from the rest of the monorepo. Treat it as read-only reference material — do not install its dependencies, do not wire it into the pipeline, and do not include it in health checks or index sweeps.

---

## Optimization Proposals

### A. Retire / Archive `export_poller.sh` and `activity_listener.py`
These are legacy execution paths that predate the current `core.py` cache-write hook → `dispatch_pipeline.py` flow. They duplicate work the TUI already does and introduce a second, less-reliable execution surface. The methodology log documents the pain: 4 listener lifecycle attempts, nohup ghosts, PID-file fragility. The canonical path is: `core.py stream_completion()` writes cache → `dispatch_pipeline.update_all()` → `autonomous_runner`. The listener and poller should be archived (moved to `_archive/`) once the dispatch hook is confirmed stable on Replit.

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

**Security requirements before any REST implementation:**
- Bind to `127.0.0.1` only (never `0.0.0.0`) unless behind the Replit proxy
- Require a session token (env-var seeded, checked on every request via middleware)
- CSRF protection on all state-mutating endpoints (e.g., double-submit cookie or `SameSite=Strict`)
- Origin allowlist (only the Replit preview domain)
- Rate-limit all endpoints — especially `[1]` (Full Autonomous Run), which triggers heavy workloads
- Emit an audit log entry (timestamp, action, result) for every invocation; persist to `LOG_DIR`
- Least-privilege: read-only endpoints (status, feed, metrics) available without elevated scope; execution endpoints require an explicit capability flag

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

---

---

## Branch Evaluations

### `mistral/fixes-config-security` — env-aware config, bridge hardening, security docs
*Author: timerloggedout-spec. 9 files, +297/−27 lines.*

**What it does well:**
- `archwiz/config.py` — persistent JSON config at `~/.archwiz/config.json`, proper directory/file permissions (700/600), graceful corruption handling (renames to `.broken`), atomic token writes (temp-file + `os.replace`)
- `multi-ai-cli/bridge/mistral_bridge.py` — now imports from `archwiz.config`; atomic token write with secure perms
- `tools/tests/mistral_bridge_smoke.py` — smoke test that is safe (no external calls, cleans up after itself)
- `SECURITY.md` and harvester READMEs — explicit opt-in model for credential tooling
- `requirements-base.txt` + `setup.sh` — fills the missing dependency declaration gap

**Critical gaps (fixes applied on `master`):**

| Gap | Severity | Fix applied |
|-----|----------|-------------|
| Missing `ARCHWIZ_DIR`, `DEEPCLI_DIR`, `WORKSPACE_DIR` — the paths archwiz.py actually calls | 🔴 High | Added as `@property` on `Config` + module-level constants |
| Replit detection used `REPL_OWNER` (unreliable) | 🟡 Medium | Updated to `REPL_ID` / `REPLIT_DOMAINS` / `REPLIT_DB_URL` |
| No `archwiz/__init__.py` — `from archwiz import config` fails | 🔴 High | Created `archwiz/__init__.py` |
| `setup.sh` creates a venv — breaks on Replit (no venv support) | 🔴 High | Replaced with env-aware install: venv only for `local`, system pip for Replit/Termux |
| Module-level constants missing — callers need `from archwiz.config import ARCHWIZ_DIR` | 🟡 Medium | Added flat module-level constants as drop-in replacements |
| `multi-ai-cli/core/core.py` dispatch hook copies the silent `except: pass` bug | 🔴 High | Not yet fixed — tracked in task #3 |

**Verdict:** Merging is conditional on completing task #3 (silent dispatch failure). The config design is sound. The bridge hardening and security documentation are genuine improvements.

---

### `vibe/mistralai-vibe-code-wrapper-6055d2` — MistralAI CLI + Codex-style code harvester
*Author: Vibe Nuage Agent / timerloggedout-spec co-authored. 22 files, +1072/−643 lines.*

**What it does well:**
- Complete MistralAI CLI mirroring the DeepSeek/cli-synthegration pattern end-to-end
- `code_harvester.py` — content-addressable blob store (SHA256, first 16 chars), `Pointer` class, hierarchical taxonomy (`language → project → session`), dedup by hash — directly ports the cli-synthegration Codex pattern
- 31 tests passing; regex-only extraction (no BeautifulSoup dependency)
- Dispatch hook plumbed into `multi-ai-cli/core/core.py` — same pipeline integration as deepcli

**Critical gaps:**

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| `multi-ai-cli/core/core.py` uses hardcoded `~/.mistralai-cli/` paths — ignores `archwiz/config.py` for its own storage | 🟡 Medium | Replace with `from archwiz.config import SESSION_STORE` or a parallel `MISTRALAI_SESSION_STORE` constant in config.py |
| Dispatch hook (`core.py:64-65`) is `except Exception: pass` — copies the deepcli silent-failure bug | 🔴 High | Log to stderr; tracked in task #3 |
| `multi-ai-cli/requirements.txt` is independent — not reconciled with `requirements-base.txt` | 🟡 Medium | Merge or reference from root baseline |
| `WASM_SOLVER` path constructed relative to `__file__` — solver target may be missing or resolve to incorrect package-relative location | 🟡 Medium | Resolve via `archwiz.config.DEEPCLI_DIR` or a package-local `__file__`-relative path with an existence check |
| No equivalent of `archwiz/sentinel.py` or `archwiz/probe.py` for Mistral output — verification absent | 🟢 Low | Future: extend Sentinel to validate multi-ai-cli executions |

**What to expand:**
- Add `MISTRALAI_SESSION_STORE`, `MISTRALAI_TOKENS_DIR` to `archwiz/config.py` so all AI providers share one config root
- `code_harvester.py`'s taxonomy is richer than cli-synthegration's — port the `TaxonomyNode.search()` back to the DeepSeek codex (`cli-synthegration/codex/`)
- The harvester's blob store is an ideal foundation for the **cross-session idea harvester** extension (Extension Ideas table) — add a `#concept` tag scanner on top of it

**Verdict:** High-value addition. The Codex port is well-executed. Fix the silent dispatch hook and reconcile storage paths before merging to master.

---

## User Preferences

- Evaluate critically, propose optimizations and extensions
- Preserve existing structure and stack — do not migrate or restructure
- Check recent commits and branches before recommending changes
