#!/data/data/com.termux/files/usr/bin/bash
# 📊 Agent Status
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/_agent_ctl_helper.sh"
INV="$(pick_inv "$1")"
[ -n "$INV" ] || { notify "Agent status" "no invocation"; exit 1; }
curl -sS --max-time 8 "$HUB/v1/agent/status/$INV" 2>/dev/null \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("status","?"), "rc="+str(d.get("rc","?")), str(d.get("seconds","?"))+"s")' \
  | { read S; notify "📊 Agent Status" "inv $INV — $S"; }
