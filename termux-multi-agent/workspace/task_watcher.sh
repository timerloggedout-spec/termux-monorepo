#!/bin/bash
# task_watcher.sh – poll master_tasks.json for pending tasks and dispatch them
while true; do
  pending=$(jq -r '.[] | select(.status=="pending") | .id' master_tasks.json)
  if [ -n "$pending" ]; then
    echo "=== $(date) – Dispatching: $pending ==="
    for tid in $pending; do
      python3 dispatch_task.py "$tid"
    done
    # Refresh metrics after dispatching
    python3 ~/workspace/llm_map/foresight_collect.py 2>/dev/null
    python3 ~/workspace/llm_map/reliability_scan.py 2>/dev/null
    python3 ~/cli-synthegration/sync/selective_sync.py 2>/dev/null
    synthegration export-all 2>/dev/null
    synthegration codex-index 2>/dev/null
  else
    echo "$(date) – No pending tasks"
  fi
  sleep 30  # check every 30 seconds
done
