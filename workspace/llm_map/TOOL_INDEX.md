# 🪄 ArchWiz Tool Index — v20260613.1713

**23 tools** across 5 categories.

## Cockpit & Pipeline
- **archwiz.py** — Dashboard — 16 options + pipeline toggle + live status bar
- **activity_listener.py** — Auto‑executes assistant code blocks from any session
- **export_poller.sh** — Fetches session history from DeepSeek to TUI cache
- **live_view.py** — Unified conversation + autoexec feed + send messages
- **debug_daemon.py** — Watches for failures, auto‑fixes with ruff/shellcheck, reports to chat

## Autonomous Operation
- **autonomous_runner.py** — Dispatches pending tasks with memory checks and crash recovery
- **dispatch_task.py** — Sandboxed task execution with orchestrator + Sentinel gate
- **task_builder.py** — Interactive task creation wrapping add_task.py
- **auto_repair.py** — Auto‑fixes simple Sentinel REVIEW issues (wrong paths, missing Grid entries)

## Verification & Testing
- **sentinel.py** — 5‑gate verification: file integrity, naming, duplicate, probe, shockwave
- **probe.py** — Syntax check, import check, unit test runner
- **mirror.py** — Self‑critique: task hygiene, index freshness, backup age, lexicon orphans
- **dangle_detector.py** — Cross‑ecosystem broken reference scanner

## Knowledge & Memory
- **archivist.py** — Local query engine — answers from all indices without network
- **tasque_declare.py** — Declares task completion to taDone.md
- **timeline_editor.py** — Full database editor + archaeologist launcher + commit notes
- **narrative.py** — Chronological feed of all pipeline events, errors, and TasQue declarations
- **lexicon_harvest.py** — Scans sessions for novel terms, batch review, seed terms
- **name_forge.py** — Suggests tool names from the Grimoire Protocol table
- **restore_version.py** — Provenance‑based code resurrection from true_versions.json

## Ecosystem Maintenance
- **archaeo_sweep.py** — Stateful archaeologist sweep — only scans changed files
- **profile_filter.py** — Profile‑based index filtering (archwiz, deepseek, etc.)
- **CONSIDERATIONS.md** — Running design log and prompt engineering knowledge base

## Installed FOSS Debug Stack
- **entr** — file watcher for auto‑rebuild on changes
- **shellcheck** — static analysis for shell scripts
- **ripgrep (rg)** — fast recursive search
- **fd** — fast alternative to `find`
- **jq** — JSON processor
