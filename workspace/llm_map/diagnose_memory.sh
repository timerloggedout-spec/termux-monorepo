#!/bin/bash
# diagnose_memory.sh – monitor memory during a dispatch
TASK_ID="${1:-arch-013}"
LOG="$HOME/tmp/memory_diag_$TASK_ID.log"
mkdir -p "$HOME/tmp"
echo "Monitoring $TASK_ID — writing to $LOG"
python3 ~/workspace/llm_map/dispatch_task.py "$TASK_ID" &
PID=$!
while kill -0 $PID 2>/dev/null; do
  rss=$(ps -o rss= -p $PID 2>/dev/null | tr -d ' ')
  echo "$(date +%H:%M:%S) RSS: ${rss:-0} KB" | tee -a "$LOG"
  sleep 1
done
echo "Peak: $(sort -t: -k2 -nr "$LOG" | head -1)" | tee -a "$LOG"
