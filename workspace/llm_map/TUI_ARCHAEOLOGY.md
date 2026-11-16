# 🏺 TUI Branch Feature — Forensic Anthropology Report

## Investigation Summary

**Date:** 2026-06-08  
**Investigator:** 4_51GH7 ForeSight / Archaeologist Agent  
**Subject:** `deepcli-tui/tui.py` — branch/fork/edit/continue features

## Feature Evolution (from `true_versions.json`)

| Order | Patch File | Session | Timestamp |
|-------|-----------|---------|-----------|
| 1 | `patch_tui_tree_v2.py` | `d71ecaab-783d-486a-9e59-84f9f9705b3f` | 2026-05-24T00:59:03 |
| 2 | `patch_tui_branch.py` | `d71ecaab-783d-486a-9e59-84f9f9705b3f` | 2026-05-24T02:11:11 |
| 3 | `add_tui_back.py` | `d71ecaab-783d-486a-9e59-84f9f9705b3f` | 2026-05-24T02:27:12 |
| 4 | `fix_attach_tui.py` | `d71ecaab-783d-486a-9e59-84f9f9705b3f` | 2026-05-24T02:38:20 |
| 5 | `fix_tui_final.py` | `d71ecaab-783d-486a-9e59-84f9f9705b3f` | 2026-05-24T02:46:42 |
| 6 | `finalize_tui.py` | `d71ecaab-783d-486a-9e59-84f9f9705b3f` | 2026-05-24T03:26:56 |
| 7 | `finalize_v2.py` | `d71ecaab-783d-486a-9e59-84f9f9705b3f` | 2026-05-24T03:59:05 |

All seven TUI patches were promoted in a single session.

## Key Sessions (via Session Association Tool)

| Session Prefix | Relevance | Full UUID |
|---------------|-----------|-----------|
| `e102d768` | `/back`, `/branches`, `/continue`, `/select` | Resolve with `forensic-query session e102d768` |
| `3f3d5af3` | `branch`, `fork`, `tui` | Resolve with `forensic-query session 3f3d5af3` |
| `d71ecaab` | `/branches`, `/select`, all 7 TUI promotions | `d71ecaab-783d-486a-9e59-84f9f9705b3f` |

## 🌿 Tree Display Investigation

### What Was Reported
The TUI tree view previously showed 🌿 at every branch point, making the conversation structure visually clear. After `patch_tui_tree_v2.py`, the tree appeared flatter.

### What We Found
- The `marker` line (96) was **never changed** — it has always been `"🔽 " if mid == selected_parent_id else ""`
- The `🌿` display came from the **tree connectors** (`├── `, `└── `) in the original `build_tree_str`
- `patch_tui_tree_v2.py` added `MAX_TREE_LINES` pagination and restructured `build_tree_str` with the `_render()` inner function
- The tree connectors (`├── ` / `└── `) are **still present** in the current code
- The display change is a **rendering artefact of conversation size**: with 400+ messages, the tree truncates at 200 lines, and the deep nesting makes branch points invisible at the truncation boundary

### Conclusion
**This is not a code regression.** The `/branches` command works correctly, the tree connectors work correctly, and the data (`parent_id` fields) are intact. The visual difference is caused by `MAX_TREE_LINES = 200` truncating large conversations before branch points are visible. The `/more` command removes the cap but does not restore the original tree depth.

## Current State

| Feature | Status |
|---------|--------|
| `/branches` | ✅ Working — lists all root messages correctly |
| `/edit` | ✅ Working |
| `/continue` | ✅ Working |
| `/back` | ✅ Working |
| `/more` | ✅ Working (toggles full tree) |
| Tree connectors (`├── `, `└── `) | ✅ Present in code |
| 🌿 at branch points | ⚠️ Not visible at large conversation sizes |
| `/bookmark` | ❌ Not yet implemented |
| `/thinking` display | ⚠️ Feedback could be clearer |

## Data Integrity

- `parent_id` field present in all 423 messages of the inspected session
- 1 root message per session (correct)
- Cache files (`~/.deepcli/cache/`) are **session databases**, not transient caches
- `arch-009` task (rename to `session_store`) is the correct path forward

## Automation Note

The Archaeologist Role (`archaeologist.py`) is designed to perform this exact investigation automatically. However, the current implementation relies on `correlation_index.json` having session‑to‑file links, which are incomplete for TUI files. The session bridge (`arch-002`) must be fully populated for the Archaeologist to reconstruct timelines without manual `jq` queries.

**Recommended:** Wire `synthegration search` results into the correlation index so that `archaeologist.py` can resolve truncated session IDs and trace feature evolution autonomously.

## Repair Path

The `/branches` display is functionally correct. The `🌿` restoration requires modifying `build_tree_str` to:
1. Show a `🌿` marker for **every message that has children** (not just the selected parent)
2. This is a one‑line addition to the `_render()` function in `build_tree_str`

The repair is delegated as task `repair-002` in `master_tasks.json`.
