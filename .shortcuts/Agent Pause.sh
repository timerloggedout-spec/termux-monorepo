#!/data/data/com.termux/files/usr/bin/bash
# ⏸️ Agent Pause — POST /v1/agent/<inv>/pause
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/_agent_ctl_helper.sh"
INV="$(pick_inv "$1")"
[ -n "$INV" ] || { notify "Agent pause" "no invocation — start one first"; exit 1; }
RES="$(post_control "$INV" "pause")"
notify "⏸️ Agent pause" "inv $INV → $RES"
