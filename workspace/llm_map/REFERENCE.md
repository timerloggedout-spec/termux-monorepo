# ```markdown
# 🧬 4_51GH7 ForeSight Ecosystem — Complete Reference

## 🔁 Time Loop Acceleration Branch

```
🌿 Fork → 🔮 ForeSight → ⚡ Generate → 🛡️ Validate → 🚀 Promote → 🗂️ Index → 🏺 Archaeologist
```

| Phase | Tool | Action |
|-------|------|--------|
| 🌿 Fork | `synthegration branch-fork` | Isolate change in session‑tracked branch |
| 🔮 ForeSight | `route --foresight`, `oracle` | Assess Shockwave Index, Nexus Rank |
| ⚡ Generate | `dispatch`, orchestrator | Apply change via CEDARscript |
| 🛡️ Validate | `run_history.jsonl`, `gatekeeper` | Require PASS from exact session |
| 🚀 Promote | `promote` | Timestamped backup + tier graduation |
| 🗂️ Index | `map-build`, `map-func`, `fore` | Rebuild ecosystem indices |
| 🏺 Archaeologist | `archaeo` | Full lifecycle timeline |

## 📊 Impact Scoring Frames

| Frame | Meaning | Grimoire Term |
|-------|---------|---------------|
| 💥 Shockwave Index | Destructive potential (files affected) | Shockwave |
| 🌀 Nexus Rank | Validated importance (PageRank‑like) | Nexus |
| ⚒️ Forged Stability | Days since last failure | Forged Stability |
| 🔁 Echo Return | PASS verdicts on this file | Echo |
| 🎯 Convergence Weight | Composite reliability score | Convergence |
| 🔥 Entropy Score | Staged files in blast radius | Entropy |

## 🪄 Complete Tool Index

### Session & Export
- `synthegration export-all` — Export all DeepSeek sessions
- `synthegration export <id>` — Export code blocks from one session
- `synthegration sessions [query]` — List/search conversations
- `synthegration search <term>` — Full‑text search inside all messages

### Codex & Indexing
- `synthegration codex-index` — Build codex from offline exports
- `synthegration codex-search <t>` — Search codex by hash or content
- `map-build` — Rebuild master index (profiled)
- `map-func` — Re‑extract function definitions

### Branch & Fork
- `synthegration branches` — List conversation branches
- `synthegration forks [session]` — Show asymmetric forks
- `synthegration branch-fork <n>` — Fork a branch
- `synthegration branch-merge <s> <t>` — Merge branches
- `synthegration branch-link <f> <t>` — Link knowledge

### Agent & Orchestration (with aliases)
| Alias | Command | Action |
|-------|---------|--------|
| `deepcli <prompt>` | Shell function | Send prompt to DeepSeek |
| — | `deepcli-tui` | Interactive TUI dashboard |
| `route [--foresight] <q>` | `router_agent.py` | Route query to best project/agent |
| `dispatch <task_id>` | `dispatch_task.py` | Dispatch task through orchestrator |
| `promote <file>` | `promote.py` | Enforce FORGE_OVERSIGHT promotion |
| `agent-shell list|run|cmd` | `agent_shell.py` | CLI for all agents |

### Research & Analysis (with aliases)
| Alias | Command | Action |
|-------|---------|--------|
| `funcfind <file>` | jq query | Show functions in a file |
| `dep <file>` | bash script | Show dependency tree |
| `depmenu` | bash script | Interactive dependency browser |
| `oracle <file>` | `impact_oracle.py` | Shockwave, Nexus, Reliability |
| `archaeo <file> --full` | `archaeologist.py` | Lifecycle timeline + co‑evolution |
| `fore` | `foresight_collect.py` | Aggregate metrics |

### Maintenance
| Alias | Action |
|-------|--------|
| `map-build` | Rebuild master index |
| `map-func` | Re‑extract functions |
| `discover_bloat.sh` | Find bloat candidates |
| `enforce_workspace_hierarchy.sh` | Ensure scaffolding |
| `task-watch` | Poll & dispatch pending tasks |

### Metrics & Logging
| File | Purpose |
|------|---------|
| `foresight_state.json` | Aggregated ForeSight metrics |
| `metrics_log.jsonl` | Oracle scores per file |
| `reliability.db` | SQLite time‑series reliability |
| `master_tasks.json` | Unified task/sprint tracker |
| `run_history.jsonl` | Agent test verdicts |

## 🛡️ FORGE_OVERSIGHT Promotion Protocol

1. **Sandbox** — All agent outputs go to designated sandbox dirs
2. **Chronomancer review** — Daily run_history review; fork if unverified > verified
3. **Bidder validation** — ELO bidder reads run_history.validated before wagering
4. **Linguist compression** — Inter‑agent messages compressed via cid.py
5. **Promotion flag** — `--promote` + timestamped backup required

## 🔐 Access Policy Summary

| Role | Allowed | Forbidden |
|------|---------|-----------|
| Developer | termux-multi-agent, workspace/llm_map, sandbox/* | harmony_hub, deepcli/core.py |
| Linguist | harmony_hub, workspace/llm_map, sandbox/* | termux-multi-agent |
| Chronomancer | provenance, workspace/llm_map, sandbox/* | termux-multi-agent, deepcli |
| Orchestrator | termux-multi-agent, workspace/llm_map, sandbox/* | — |

## 📊 Database Population Guide

To populate all databases from scratch:

```bash
# 1. Full ecosystem scan
export LLM_PROFILE=full_recon
map-build && map-func

# 2. Export DeepSeek sessions (one-time seed)
synthegration export-all
synthegration codex-index

# 3. Run ForeSight aggregation
fore

# 4. Run reliability scan on all source files
python3 reliability_scan.py

# 5. Run Oracle on core files
oracle deepcli/deepcli/core.py

# 6. Incremental sync (after initial seed)
python3 ~/cli-synthegration/sync/selective_sync.py
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `llm_index_compact.jsonl` | Master machine‑readable index |
| `func_index.jsonl` | Every function/class definition |
| `file_graph.json` | Resolved dependency graph |
| `foresight_state.json` | Aggregated metrics for ForeSight |
| `master_tasks.json` | Unified task/sprint tracker |
| `run_history.jsonl` | Agent test verdicts |
| `metrics_log.jsonl` | Oracle scores per file |
| `reliability.db` | SQLite time‑series reliability |
| `access_policy.json` | Machine‑readable role permissions |
| `GRIMOIRE_DICTIONARY.md` | 1337SP3@K lexicon |
| `FORGE_OVERSIGHT.md` | Promotion protocol & delegations |
| `agent_proposals/` | Agent‑originated task proposals |


## 🔧 Troubleshooting

### `unknown file attribute: h` in zsh
**Cause:** `INTERACTIVE_COMMENTS` option is disabled, causing zsh to interpret `#` as a file attribute query.
**Fix:** Add `setopt INTERACTIVE_COMMENTS` to the top of `~/.zshrc` (before `p10k` loads) and restart the shell.
**Why keep it on:** Enables inline `# @agent` style comments for LLM integration.


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
