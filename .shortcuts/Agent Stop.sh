#!/data/data/com.termux/files/usr/bin/bash
# ⏹️ Agent Stop — POST /v1/agent/<inv>/stop
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/_agent_ctl_helper.sh"
INV="$(pick_inv "$1")"
[ -n "$INV" ] || { notify "Agent stop" "no invocation — start one first"; exit 1; }
RES="$(post_control "$INV" "stop")"
notify "⏹️ Agent stop" "inv $INV → $RES"
