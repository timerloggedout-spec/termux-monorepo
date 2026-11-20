#!/bin/bash
# dispatch_queue.sh – sequential task runner with cooldown
MASTER="$HOME/workspace/llm_map/master_tasks.json"
DISPATCHER="$HOME/workspace/llm_map/dispatch_task.py"
DELAY=5
pending=$(jq -r '.[] | select(.status=="pending") | .id' "$MASTER")
[ -z "$pending" ] && { echo "No pending tasks."; exit 0; }
total=$(echo "$pending" | wc -l)
count=0
for tid in $pending; do
  count=$((count+1))
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "⚡ [$count/$total] $tid"
  nice -n 10 python3 "$DISPATCHER" "$tid"
  echo "   ↻ cooling down ${DELAY}s"
  sleep "$DELAY"
done
echo "✅ All $total tasks processed."
