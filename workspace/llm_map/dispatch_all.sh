#!/bin/bash
# dispatch_all.sh – run all pending with cooldown
for tid in $(jq -r '.[] | select(.status=="pending") | .id' ~/workspace/llm_map/master_tasks.json); do
  echo "=== $tid ==="
  python3 ~/workspace/llm_map/dispatch_task.py "$tid"
  sleep 15
done
