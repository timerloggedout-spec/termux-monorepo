#!/data/data/com.termux/files/usr/bin/bash
# CONTROLLER pane (🎮) for an observer-controller node. The OBSERVER pane is
# origin-status-notify.sh (id 43111). This posts a second card in the same group:
#   id 43114  media-style "d-pad": ⏮/⏭ choose a verb, ▶ run it on the origin, ⏸ mute
#             + buttons: Heartbeat now · Wake origin · Agent?
# Two cards in group tmx-origin = the "dual pane" (Android has no true split
# notification; a bundled pair is the closest native equivalent, and survives
# Bugjaeger screen-share without any clipboard hop).
# Verbs run over ssh to the origin's forced-command tmx-ctl.sh; output is shown in
# the card, never copied to the clipboard.
#   controller-panel.sh                 # draw/refresh
#   controller-panel.sh next|prev|run|run <verb>
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
ID="${TMX_NOTIFY_CONTROL_ID:-43114}"
KEY="${TMX_CONTROLLER_KEY:-$HOME/.ssh/tmx_controller_ed25519}"
VERBS=(status agent tunnel jobs disk heartbeat-now wake-lock)
mkdir -p "$TMX_STATE_DIR"; SEL="$TMX_STATE_DIR/controller-sel"; RES="$TMX_STATE_DIR/controller-last"
i="$(cat "$SEL" 2>/dev/null || echo 0)"; n=${#VERBS[@]}

run_verb() {
  local v="$1" target
  target="$(bash "$SCRIPT_DIR/origin-status-notify.sh" --print 2>/dev/null | python -c 'import json,sys;print(json.load(sys.stdin).get("ssh",""))')"
  if [ -z "$target" ]; then echo "$v: origin endpoint unknown (bridge manifest)" >"$RES"; return; fi
  # target looks like: ssh -p PORT USER@HOST  (built from the bridge manifest)
  set -- $target
  timeout 25 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new \
    -i "$KEY" "${@:2}" "$v" 2>&1 | tail -c 300 >"$RES" || echo "$v: ssh failed" >>"$RES"
}

case "${1:-draw}" in
  next) i=$(( (i+1) % n )) ;;
  prev) i=$(( (i-1+n) % n )) ;;
  run)  run_verb "${2:-${VERBS[$i]}}" ;;
esac
echo "$i" >"$SEL"
tmx_have termux-notification || { echo "verb=${VERBS[$i]} last=$(cat "$RES" 2>/dev/null)"; exit 0; }
self="bash '$SCRIPT_DIR/controller-panel.sh'"
termux-notification --id "$ID" --group tmx-origin --ongoing --alert-once --priority low --type media \
  --title "🎮 Origin control · ${VERBS[$i]}" --content "$(cat "$RES" 2>/dev/null || echo 'ready')" \
  --media-previous "$self prev" --media-next "$self next" \
  --media-play "$self run" --media-pause "bash '$SCRIPT_DIR/origin-status-notify.sh' --mute 120" \
  --button1 "Heartbeat" --button1-action "$self run heartbeat-now" \
  --button2 "Wake" --button2-action "$self run wake-lock" \
  --button3 "Agent?" --button3-action "$self run agent"
