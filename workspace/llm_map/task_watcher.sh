#!/bin/bash
# task_watcher.sh – poll master_tasks.json for pending tasks and dispatch them
while true; do
  pending=$(jq -r '.[] | select(.status=="pending") | .id' master_tasks.json)
  if [ -n "$pending" ]; then
    echo "=== $(date) – Dispatching: $pending ==="
    for tid in $pending; do
      python3 dispatch_task.py "$tid"
    done
    # Session store (~/.deepcli/cache) is updated by every TUI/agent call automatically.
# The export cycle below builds versioning indices from those cached sessions.
# Refresh metrics after dispatching
    python3 ~/workspace/llm_map/foresight_collect.py 2>/dev/null
    python3 ~/workspace/llm_map/reliability_scan.py 2>/dev/null
    python3 ~/cli-synthegration/sync/selective_sync.py 2>/dev/null
    synthegration export-all 2>/dev/null
    synthegration codex-index 2>/dev/null
    # Inject AST hashes if full_map_output.txt exists
    # Regenerate AST signatures (non‑interactive) and inject hashes
    bash ~/workspace/llm_map/expand_sig_map.sh 2>/dev/null
    if [ -f ~/workspace/llm_map/full_map_output.txt ]; then
        python3 ~/workspace/llm_map/inject_ast_hashes.py 2>/dev/null
    fi
    # Run fragment matching
    if [ -f ~/cli-synthegration/workspace/provenance/fragment_matcher.py ]; then
        python3 ~/cli-synthegration/workspace/provenance/fragment_matcher.py 2>/dev/null
    fi
  else
    echo "$(date) – No pending tasks"
  fi
  sleep 30  # check every 30 seconds
done
