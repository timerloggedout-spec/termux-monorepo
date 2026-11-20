# 🧠 ArchWiz Concept Index — Complete

## Existing Tools (Referenced, Not Rebuilt)
| Tool | Location | What It Does |
|------|----------|--------------|
| `commit_notes.py` | `~/workspace/llm_map/` | Extracts feature summaries from sessions, guided by Router + Archaeologist |
| `conv_branching.py` | `~/cli-synthegration/` | Implements branch/fork API calls |
| `accelerator.py` | `~/cli-synthegration/Chronos/` | Detects fork points, creates success‑only branches |
| `versioner.py` | `~/cli-synthegration/Chronos/` | Tracks versions across time loops |
| `branch_manager.py` | `~/cli-synthegration/` | List/fork/merge conversation branches |
| `time_loop_accelerator.py` | `~/cli-synthegration/workspace/staging/` | Time Loop Acceleration implementation |
| `prompt_engine` | `~/harmony_hub/` | L33T personality with random phrase selection |
| `cedrlang/` | `~/workspace/compression_sandbox/` | Agentic compression protocol (seeded concept) |
| `cid.py` | `~/workspace/compression_sandbox/cedrlang/` | Short hash pointer system |
| `task_files_index.json` | `~/workspace/llm_map/` | Index of all task/sprint/todo files |
| `correlation_index` | `~/cli-synthegration/workspace/correlation/` | Session‑to‑file links with version hashes |
| `true_versions.json` | `~/cli-synthegration/workspace/provenance/` | Version hash tracking |
| `run_history.jsonl` | `~/termux-multi-agent/` | Agent test verdicts |
| `message_index.json` | `~/cli-synthegration/codex/` | Full‑text session message index |

## Core Concepts
| Concept | Definition | Status |
|---------|-----------|--------|
| **TasQue** | Task completion declaration (ta'Done) | ✅ Implemented |
| **Sentinel** | 5‑gate verification (file, naming, duplicate, probe, shockwave) | ✅ Implemented |
| **Archivist** | Local‑only query engine across all indices | ✅ Implemented |
| **Probe** | Syntax/import/test validation | ✅ Implemented |
| **Mirror** | Self‑critique: task hygiene, index freshness, backups | ✅ Implemented |
| **Dangle Detector** | Cross‑ecosystem broken reference scanner | ✅ Implemented |
| **Spellbook** | Library of system abilities (concept reserved) | 🟡 Reserved |
| **Rune** | Short hash pointer (CID‑style) | 🟡 Reserved |
| **Sigil** | Substitution engine for runtime compression | ❌ Not built |
| **Lexicon Harvest** | Scan sessions for novel terms | ✅ Implemented |
| **Name Forge** | Grimoire‑powered tool naming | ✅ Implemented |
| **ChronoMancer** | Time‑loop agent (success‑only trunks, branch routing) | ❌ Not built |
| **Refactor Tractor** | Target‑type aware dispatch, auto‑repair, Sentinel gate | ✅ Implemented |
| **Self‑healing Sandbox** | Detect error → request fix → validate → promote | ❌ Not built |
| **Pointer Index** | CID‑style bookmarking of messages, tables, data | ✅ Implemented |
| **Narrative Feed** | Chronological event stream of all pipeline events | ✅ Implemented |

## Feature Requests (Not Yet Built)
| Feature | Description |
|---------|-------------|
| **Real‑time chat feedback** | Listener sends execution results to this chat |
| **Cross‑session idea harvester** | Scan all sessions for novel concepts |
| **ChronoMancer branch UI** | Visual tree, time‑loop summaries in TUI |
| **Listener auto‑scribe** | Consolidate notes every N messages, post to chat |
| **Commit notes scanner** | Detect "what's changed" summaries → `CHANGES.md` |
| **Multi‑account probing** | Account 2 selectors, image upload |
| **Full user manual** | Beyond outline |
| **Tab completion for /sessions** | Interactive session picker with A/T/H/P toggles |
| **Expert‑mode session creation** | Sessions created with correct model type from start |

## Methodology Evolution
| Phase | What We Tried → What Stuck |
|-------|---------------------------|
| **Listener lifecycle** | `nohup` → `pkill -f` → `Popen` → `listener_control.py` (PID file) |
| **Chat feedback** | `deepcli_send.py` (new session) → `send_message` (missing fields) → `stream_completion` (TUI pipe) |
| **Session cache** | `synthegration export` → `manifest.json` → `get_history()` direct |
| **Block tracking** | Message‑ID → per‑block hash (MD5 first 12 chars) |
| **Live View** | Curses → text loop → throttled redraw + `/send` single‑line |
| **Hang avoidance** | `stdin=DEVNULL` + `start_new_session=True` + PID‑file controller |

## Forensic Toolchain Integration (2026-06-14)
- `[17] Forensic Toolchain` — fragment match, similarity scan, correlation scout, staged extraction
- `[11] Restore Version` — now accepts staged blocks from forensic toolchain
- Staged blocks saved to `~/archwiz/staging_blocks.json`
- Pipeline: `[17]` extract → `[11]` restore → target file (with .bak backup)

## [18] Documentation Pipeline (2026-06-15)
- Single cockpit option regenerates all auto‑generated documentation
- Session Digest, Structural Scanner, Export Status, Pointer Index
- All output written to `~/archwiz/` directory
- Utility Belt scripts are symlinked into `~/archwiz/` for cockpit access
