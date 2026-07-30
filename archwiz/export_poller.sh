#!/bin/bash
SESSION_ID="${1:?Usage: export_poller.sh <session_id> [interval_sec=10]}"
INTERVAL="${2:-10}"
CACHE="$HOME/.deepcli/session_store/${SESSION_ID}.json"

while true; do
  python3 -c "
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home()/'deepcli'))
from deepcli.core import get_token, get_history
token = get_token()
msgs = get_history(token, '$SESSION_ID', force_refresh=True)
Path('$CACHE').write_text(json.dumps(msgs))
" 2>/dev/null
  if [ $? -eq 0 ]; then
    count=$(python3 -c "import json; print(len(json.load(open('$CACHE'))))" 2>/dev/null || echo 0)
    echo "[$(date +%H:%M:%S)] $count messages cached"
  else
    echo "[$(date +%H:%M:%S)] fetch failed — will retry"
  fi
  sleep "$INTERVAL"
done
