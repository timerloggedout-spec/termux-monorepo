# 🧬 4_51GH7 ForeSight — Change Log

| # | Tool / File | Purpose | Status |
|---|-------------|---------|--------|
| 1 | `router_agent.py` | Route queries to best project/agent/sprint | ✅ |
| 2 | `impact_oracle.py` | Shockwave, Nexus, Stability, Echo | ✅ |
| 3 | `promote.py` | FORGE_OVERSIGHT promotion (Git removed) | ✅ |
| 4 | `foresight_collect.py` | Aggregate all data → `foresight_state.json` | ✅ |
| 5 | `batch_resumer.py` | Crash‑proof checkpointed iteration | ✅ |
| 6 | `archaeologist.py` | Full lifecycle timeline + co‑evolution | ✅ |
| 7 | `reliability_scan.py` | Populate `reliability.db` time‑series | ✅ |
| 8 | `session_title_refiner.py` | Keyword‑based session renaming | ✅ |
| 9 | `find_stale_files.py` | Multi‑version, stale, duplicate detection | ✅ |
| 10 | `validate_promotion.py` | 4‑gate promotion quality check | ✅ |
| 11 | `dispatch_task.py` | Copy → dispatch → verdict → promote | ✅ |
| 12 | `agent_shell.py` | Unified CLI for all agents | ✅ |
| 13 | `task_watcher.sh` | Poll + dispatch + sync + export cycle | ✅ |
| 14 | `access_policy.json` | Machine‑readable role permissions | ✅ |
| 15 | `agent_proposals/` | Agent‑originated task proposals dir | ✅ |
| 16 | `REFERENCE.md` | Complete ecosystem reference docs | ✅ |
| 17 | `TOOL_INDEX.md` | Quick‑reference tool list | ✅ |
| 18 | `CHANGELOG.md` | This file | ✅ |
| 19 | `reliability.db` | SQLite time‑series reliability | ✅ |
| 20 | `metrics_log.jsonl` | Oracle scores log | ✅ |
| 21 | `master_tasks.json` | Unified task/sprint tracker | ✅ |
| 22 | `run.py` patched | Accepts TASK_ID from master_tasks.json | ✅ |
| 23 | `deepcli_send.py` | Clean CLI wrapper for chat_completion() | ✅ |
| 24 | Profile system | Scoped project indexing (full_recon, truth, quantum) | ✅ |
| 25 | Bloat exclusions | .hermes, .cargo, .crates.io excluded | ✅ |
| 26 | Timestamp injection | 1,211 real file mtimes in index | ✅ |
| 27 | SQLite → JSONL bridge | verdicts from local_repo.db → run_history.jsonl | ✅ |
| 28 | Correlation index clean | 5,206 → 4,643 keys, 445 codex links | ✅ |
| 29 | Task watcher auto‑refresh | fore + reliability_scan + selective_sync + export-all | ✅ |
| 30 | `.bashrc` aliases | 21 ecosystem aliases | ✅ |
| 31 | `deepcli` function | Stable CLI alias for DeepSeek API calls | ✅ |


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
