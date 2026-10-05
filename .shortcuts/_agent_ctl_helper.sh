#!/data/data/com.termux/files/usr/bin/bash
# shared helper for /v1/agent shortcut scripts
set -uo pipefail
HUB="${HUB:-http://127.0.0.1:8800}"
STATE="$HOME/.deepcli/watchdog/current-invocation"

# pick invocation: $1 explicit, else current-invocation file, else newest
pick_inv() {
  if [ -n "${1:-}" ]; then echo "$1"; return; fi
  if [ -s "$STATE" ]; then cat "$STATE"; return; fi
  python3 - <<'PY' 2>/dev/null || echo ""
import json, urllib.request
try:
    with urllib.request.urlopen("http://127.0.0.1:8800/v1/agent/list", timeout=4) as r:
        d = json.load(r)
    runs = d.get("runs") or []
    if runs: print(runs[-1]["invocation_id"])
except Exception: pass
PY
}

post_control() {
  local inv="$1" verb="$2"
  curl -sS --max-time 8 -X POST "$HUB/v1/agent/$inv/$verb" 2>/dev/null \
    | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("status","?"))' 2>/dev/null
}

notify() {
  local title="$1" body="$2"
  termux-notification --id deepagent-run --title "$title" --content "$body" \
    --priority default 2>/dev/null || true
}

case "${3:-}" in
  pause|resume|stop|cancel)
    INV="$(pick_inv "${1:-}")"
    [ -n "$INV" ] || { notify "Agent control" "no invocation"; exit 1; }
    RES="$(post_control "$INV" "$3")"
    notify "Agent $3" "inv $INV → $RES"
    ;;
esac
