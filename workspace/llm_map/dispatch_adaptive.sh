#!/bin/bash
# dispatch_adaptive.sh – adaptive task runner with real memory limits
MASTER="$HOME/workspace/llm_map/master_tasks.json"
DISPATCHER="$HOME/workspace/llm_map/dispatch_task.py"

MIN_FREE_MEM=150000   # 150 MB minimum before launching
TARGET_FREE=300000    # aim for this after each run

get_free_mem() { awk '/MemAvailable/ {print $2}' /proc/meminfo 2>/dev/null || echo 999999; }

pending=$(jq -r '.[] | select(.status=="pending") | .id' "$MASTER")
if [ -z "$pending" ]; then
  echo "No pending tasks."
  exit 0
fi

total=$(echo "$pending" | wc -l)
count=0
for tid in $pending; do
  count=$((count+1))
  while true; do
    free_mem=$(get_free_mem)
    [ "$free_mem" -ge "$MIN_FREE_MEM" ] && break
    echo "⏳ Memory low (${free_mem} KB) — waiting 15s"
    sleep 15
  done
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "⚡ [$count/$total] $tid  (free: ${free_mem} KB)"
      # Set ulimit to 80% of free memory (KB), min 400 MB, max 1 GB
    nice -n 10 python3 "$DISPATCHER" "$tid"
  free_after=$(get_free_mem)
  if [ "$free_after" -lt "$MIN_FREE_MEM" ]; then
    cooldown=30
  elif [ "$free_after" -lt "$TARGET_FREE" ]; then
    cooldown=10
  else
    cooldown=3
  fi
  echo "   ↻ adaptive cooldown ${cooldown}s (free: ${free_after} KB)"
  sleep "$cooldown"
done
echo "✅ All $total tasks processed."
