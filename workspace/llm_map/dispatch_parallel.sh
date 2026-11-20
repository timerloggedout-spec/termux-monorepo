#!/bin/bash
# dispatch_parallel.sh – memory‑aware, tmux or background
MASTER="$HOME/workspace/llm_map/master_tasks.json"
DISPATCHER="$HOME/workspace/llm_map/dispatch_task.py"

get_free_mem() { awk '/MemAvailable/ {print $2}' /proc/meminfo 2>/dev/null || echo 0; }

pending=$(jq -r '.[] | select(.status=="pending") | .id' "$MASTER")
[ -z "$pending" ] && echo "No pending tasks." && exit 0

if command -v tmux &>/dev/null; then
  echo "Using tmux for parallel dispatch"
  tmux new-session -d -s "dispatcher" 2>/dev/null
  for tid in $pending; do
    tmux new-window -t "dispatcher" -n "$tid" \
      "echo '=== $tid ===' && python3 $DISPATCHER $tid && echo '✅ $tid complete' && sleep 5 && exit"
    echo "🚀 $tid (tmux)"
  done
  echo "Monitor: tmux attach -t dispatcher"
else
  echo "tmux not found – using background jobs (max 2)"
  MAX=2
  running=0
  for tid in $pending; do
    while [ "$running" -ge "$MAX" ] || [ "$(get_free_mem)" -lt 200000 ]; do
      running=$(jobs -r | wc -l)
      sleep 5
    done
    echo "🚀 $tid"
    nice -n 10 python3 "$DISPATCHER" "$tid" &
    running=$((running+1))
  done
  wait
  echo "✅ All parallel tasks done."
fi
