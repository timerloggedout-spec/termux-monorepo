# 🪄 Agent Tool-Access Matrix

| Agent | Token | CLI Tools | DB Access | Sandbox | Output Destination |
|-------|-------|-----------|-----------|---------|--------------------|
| **Chronomancer** | Primary/Secondary | `branch_conversation`, `list-messages`, `find-fork-point` | `run_history` (read/write) | N/A | `run_history` + new session |
| **Linguist** | Primary | `cid.py`, `cedrlang.py`, `ast-grep`, `llm_map` | `cedar_index.json` | `~/harmony_hub/workspace/linguist/` | Pointer registry + compressed prompts |
| **Bidder** | Primary | `elo_updater.py` | `run_history`, `elo_ratings.json` | N/A | ELO adjustments |
| **Scout** | Secondary | `deepseek-full-suite.mjs`, `capture-upload-api.js` | N/A | `~/deepseek-cli/test-reports/` | Test reports + endpoint cache |
| **Harvester** | Primary | `comprehensive_fast.py`, `fragment_matcher.py` | `messages_fts`, `hash_index.json` | `~/deepseek_harvest_work/` | Code blocks + provenance |
| **Orchestrator** | Primary/Secondary | `direct_task.py` | `run_history` | `~/termux-multi-agent/workspace/` | Sandbox file + validation |

## Communication Flow
1. **User Agent** (this chat) is the only interface that can request features or report issues.
2. Agents return results to their **Output Destination** (sandbox or DB).
3. **Orchestrator** polls destinations and promotes validated results.
4. **Chronomancer** monitors `run_history` and triggers forks when noise exceeds signal.
