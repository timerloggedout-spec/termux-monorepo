#!/data/data/com.termux/files/usr/bin/bash
# 🚀 Agent Start — prompt via termux-dialog, POST to /v1/agent
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/_agent_ctl_helper.sh"
TASK="$(termux-dialog -t "DeepAgent task" -i "hint" 2>/dev/null \
        | python3 -c 'import sys,json; print(json.load(sys.stdin).get("text",""))' 2>/dev/null)"
[ -n "$TASK" ] || { notify "Agent Start" "cancelled"; exit 0; }
RESP="$(curl -sS --max-time 20 -X POST "$HUB/v1/agent" \
  -H 'Content-Type: application/json' \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"task": sys.argv[1], "source": "widget"}))' "$TASK")")"
INV="$(printf '%s' "$RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("invocation_id",""))' 2>/dev/null)"
[ -n "$INV" ] && printf '%s' "$INV" > "$STATE"
notify "🚀 Agent Start" "inv ${INV:-(none)}"
