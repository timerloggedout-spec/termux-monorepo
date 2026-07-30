#!/data/data/com.termux/files/usr/bin/bash
export LLM_PROFILE=archwiz

# Kill any existing pipeline processes (clean slate)
pkill -f export_poller.sh 2>/dev/null
pkill -f activity_listener 2>/dev/null
sleep 1

# Start poller in background, log to file
nohup bash ~/archwiz/export_poller.sh 417ddd6d-9711-465d-ab90-c92cc04aeabf 10 > ~/archwiz/poller.log 2>&1 &

# Start listener in background, log to file
nohup python3 ~/archwiz/activity_listener.py \
  --session 417ddd6d-9711-465d-ab90-c92cc04aeabf \
  --auto --max-age 99999 --task-id arch-016 \
  > ~/archwiz/listener.log 2>&1 &

# Optional: rebuild Grid if older than 2 days
GRID="$HOME/workspace/llm_map/llm_index_compact.jsonl"
if [ ! -f "$GRID" ] || [ $(($(date +%s) - $(stat -c %Y "$GRID" 2>/dev/null || echo 0))) -gt 172800 ]; then
  echo "Grid stale — rebuilding..."
  python3 "$HOME/workspace/llm_map/build_final_all_profile.py" &
fi

# Launch cockpit in foreground
echo ""
# Self-healing: verify imports before launch
python3 -c "import json, os, pathlib, shutil, subprocess, sys, time" 2>/dev/null || { echo "Fixing imports..."; sed -i "s/^import json.*/import json, os, pathlib, shutil, subprocess, sys, time/" ~/archwiz/archwiz.py; }
exec python3 ~/archwiz/archwiz.py
