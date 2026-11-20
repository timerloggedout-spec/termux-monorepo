# 🪄 ArchWiz Tool Index — v20260614.1930
**28 tools** across **7 categories**.

## Cockpit & Pipeline
- **archwiz.py** — Dashboard: 16 options + 3 mode toggles (auto/review/pipeline)
- **activity_listener.py** — Auto‑executes assistant code blocks; deduplicated; TUI‑pipe send
- **live_view.py** — Review panel: /exec, /skip, /send, /m, /c, /ctx, /clear, /hist, /sync
- **debug_daemon.py** — Watches failures; auto‑fixes with ruff/shellcheck; reports to chat
- **listener_control.py** — PID‑file based safe start/stop for the listener

## Forensic & Version Control
- **forensic_toolchain.py** — Fragment matcher, similarity scan, correlation scout, staged extraction
- **correlation_scout.py** — Traces file-path changes across true_versions, run_history, comprehensive_provenance
- **fragment_matcher.py** — Function‑level provenance from comprehensive_provenance.json
- **restore_version.py** — Provenance‑based code resurrection; now integrated with staged forensic blocks

## Autonomous Operation
- **autonomous_runner.py** — Dispatches pending tasks; memory‑aware; crash‑recovery; Sentinel gate
- **dispatch_task.py** — Sandboxed execution with target_type and Sentinel verification
- **task_builder.py** — Interactive task creation wrapping add_task.py
- **auto_repair.py** — Auto‑fixes simple Sentinel REVIEW issues

## Verification & Testing
- **sentinel.py** — 5‑gate: file integrity, naming, duplicate, probe, shockwave
- **probe.py** — Syntax/import/test validation
- **mirror.py** — Self‑critique: task hygiene, index freshness, backup age
- **dangle_detector.py** — Cross‑ecosystem broken reference scanner

## Knowledge & Memory
- **archivist.py** — Local query engine; answers from all indices
- **tasque_declare.py** — Declares completion to taDone.md
- **timeline_editor.py** — Full DB editor + archaeologist + commit notes
- **narrative.py** — Chronological feed of pipeline events
- **lexicon_harvest.py** — Session scanning; batch review; seed terms
- **name_forge.py** — Grimoire‑powered tool naming

## Ecosystem Maintenance
- **archaeo_sweep.py** — Stateful archaeologist; only scans changed files
- **profile_filter.py** — Profile‑based index filtering
- **CONSIDERATIONS.md** — Running design log & prompt engineering
- **METHODOLOGY_INDEX.md** — Every approach tried, what broke, what stuck
- **CONCEPT_INDEX.md** — Every idea, feature, and concept cataloged

## Installed FOSS Stack
- **ruff** — Python linter + auto‑fix
- **shellcheck** — Shell script analysis
- **ripgrep (rg)** — Fast recursive search
- **fd** — Fast `find` alternative
- **jq** — JSON processor
- **entr** — File watcher

## Documentation Pipeline (2026-06-15)
- **session_digest.py** — Scans all exported sessions for structured features (tables, concept lists, task lists)
- **structural_scanner.py** — Fast chunked‑correlation scanner for code features
- **export_status.py** — Shows cached vs exported sessions and staleness (Utility Belt)
- **pointer_index.py** — Builds hash→location map of all exported code blocks
- **[18] Documentation Pipeline** — Regenerates all auto‑docs on demand
