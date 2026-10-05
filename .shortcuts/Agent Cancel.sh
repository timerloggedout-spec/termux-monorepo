#!/data/data/com.termux/files/usr/bin/bash
# ❌ Agent Cancel — POST /v1/agent/<inv>/cancel
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/_agent_ctl_helper.sh"
INV="$(pick_inv "$1")"
[ -n "$INV" ] || { notify "Agent cancel" "no invocation — start one first"; exit 1; }
RES="$(post_control "$INV" "cancel")"
notify "❌ Agent cancel" "inv $INV → $RES"
