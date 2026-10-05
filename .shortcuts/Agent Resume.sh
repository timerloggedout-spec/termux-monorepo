#!/data/data/com.termux/files/usr/bin/bash
# ▶️ Agent Resume — POST /v1/agent/<inv>/resume
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/_agent_ctl_helper.sh"
INV="$(pick_inv "$1")"
[ -n "$INV" ] || { notify "Agent resume" "no invocation — start one first"; exit 1; }
RES="$(post_control "$INV" "resume")"
notify "▶️ Agent resume" "inv $INV → $RES"
