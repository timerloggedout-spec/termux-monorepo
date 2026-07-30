# 🧬 ArchWiz Methodology Index
*Generated: 2026-06-14.  Last updated: live session with 417ddd6d*

## 1. Listener Life‑Cycle Control — 4 Attempts

| Attempt | Method | Result | Why It Failed / Stuck |
|---------|--------|--------|------------------------|
| **A** | `nohup python3 listener.py &` | ❌ Ghosts | `nohup` printed "ignoring input" to terminal; processes died silently |
| **B** | `pkill -f activity_listener` + `Popen` | ❌ Killed self | `pkill -f` matched the helper script, killing the starter before the listener |
| **C** | `subprocess.Popen(start_new_session=True)` | ⚠️ Fragile | No PID tracking; multiple instances spawned accidentally |
| **D** | `listener_control.py` + PID file | ✅ **Current** | Single start/stop/restart command; cockpit `[p]` toggles cleanly |

## 2. Sending Messages to Chat — 3 Attempts

| Attempt | Method | Result | Root Cause |
|---------|--------|--------|------------|
| **A** | `deepcli_send.py` | ❌ New session | Creates a *new* `create_session()` every call, never replies to existing chat |
| **B** | `send_message()` from `core.py` | ❌ Expert error | Payload missing `thinking_enabled` / `search_enabled` – API rejected |
| **C** | `stream_completion()` from `core.py` | ✅ **Current** | Same pipe the TUI uses; payload includes all required fields |

> **Restored**: `deepcli/core.py` had `send_message` payload incomplete.  
> **Fixed**: Added `thinking_enabled: False, search_enabled: False` to match `stream_completion`.  
> **Git blame**: The omission dates to the original `deepcli` session (May 24‑25); `stream_completion` always had the fields, but `send_message` was never updated.

## 3. Session Cache Pipeline — 4 Attempts

| Attempt | Method | Result | Why |
|---------|--------|--------|-----|
| **A** | `export_poller.sh` via `synthegration` | ⚠️ Fragile | Depended on `synthegration_index.py` which had a broken `CodexIndex()` call |
| **B** | Direct `get_history(token, force_refresh=True)` | ✅ Works | Same call the TUI uses; simplest, most reliable |
| **C** | `manifest.json` converter | ❌ Abandoned | Over‑engineered; manifest format changed between exports |
| **D** | `deepcli.core.get_history()` in listener | ✅ **Current** | Called every loop iteration; cache written to `~/.deepcli/session_store/` |

## 4. Code‑Block Extraction & Dedup — 3 Iterations

| Iteration | Method | Result |
|-----------|--------|--------|
| **A** | Regex ` ``` ... ``` ` with no dedup | ❌ Duplicate blocks flooded panel |
| **B** | Dedup by message‑ID only | ❌ Blocks from same message all skipped/executed together |
| **C** | Dedup by `message_id + md5(code[:80])[:12]` | ✅ **Current** | Each block tracked independently |

## 5. Live View Panel — 5 Rewrites

| Version | Approach | Result |
|---------|----------|--------|
| **v1** | `curses` | ❌ Blank screen on Termux |
| **v2** | Text loop with `/send` multi‑line | ⚠️ `/send` trapped `q` as message text |
| **v3** | Added `/end` escape | ⚠️ Still too complex |
| **v4** | `/send` single‑line, `/m` multi‑line | ✅ **Current** | Fast, predictable |
| **v5** | Added `/ctx` toggle, `/clear`, `/hist` | ✅ **Current** | Full review toolkit |

## 6. Expert‑Mode Error — Root Cause & Fix

| Aspect | Detail |
|--------|--------|
| **Symptom** | "Update to the latest version to use Expert" |
| **First seen** | May 24‑25 sessions (Termux CLI Recon Harmonization) |
| **Root cause** | `send_message()` payload missing `thinking_enabled` / `search_enabled` fields |
| **Why TUI worked** | TUI always uses `stream_completion()` which includes those fields |
| **Fix applied** | Added fields to `send_message()` payload; fallback in `stream_completion()` error handler |
| **File modified** | `~/deepcli/deepcli/core.py` |

---

## 7. Existing Tools That Already Do Similar Things

| Tool | Capability | Overlap with ArchWiz |
|------|-----------|---------------------|
| `deepcli‑tui` | Session browsing, send/receive, `/branches`, `/branchpoints` | ArchWiz panel supplements, not replaces |
| `termux‑multi‑agent` | Orchestrator, context collector, sandbox exec | ArchWiz listener = lighter auto‑exec; multi‑agent = full orchestration |
| `cli‑synthegration` | Session export, correlation, codex | ArchWiz uses correlation for archaeology; export pipeline deprecated in favor of direct API |
| `harmony_hub` | Token provider, Grimoire, prune rules | ArchWiz uses `get_token()` and Grimoire for naming |
| `cedar_forge` | Compression, executor, recorder | Seed project; concepts folded into ArchWiz Rune/Sigil layers |

## 8. Known Breaking Overwrites (and Their Fixes)

| Overwrite | When | Fix |
|-----------|------|-----|
| `send_message` payload | May 25 session | Added `thinking_enabled` + `search_enabled` |
| `dispatch_task.py` indentation | Jun 12 session | Manually realigned `if workspace_file.is_dir()` block |
| `activity_listener.py` termios crash | Jun 13 session | Added `isatty()` guard; headless mode |
| `CodexIndex()` constructor | Original `synthegration` | Fixed by passing `base_dir` argument |
| `pkill -f` self‑kill | Jun 14 session | Replaced with `listener_control.py` PID file |

## 10. Forensic Toolchain Formalized (2026-06-14)
| Step | Method | Result |
|------|--------|--------|
| Fragment Match | Searched 5,136 exported code blocks for "send_message" | Found 10 versions across May 22‑26 |
| Similarity Scan | difflib.SequenceMatcher across all blocks | Identifies related code even with different names |
| Correlation Scout | true_versions + run_history + comprehensive_provenance | Shows every change to a file |
| Staged Extraction | Saves full block to staging_blocks.json | Feeds directly into [11] Restore Version |
| Provenance Gap | deepcli/core.py not tracked in true_versions | Fragment matcher bypasses this – tracks function bodies directly |

## 11. Export Consolidation (2026-06-15)
| Attempt | Tool | Result |
|---------|------|--------|
| 1 | `export_all.py` (cli-synthegration) | ✅ Original working batch export |
| 2 | `batch_export_all.py` (llm_map) | ✅ Duplicate |
| 3 | `batch_export.sh` (harmony_hub) | ❌ Redundant – deleted |
| **Consolidated** | Use `export_all.py` for batch, `export_session.sh` for single |
