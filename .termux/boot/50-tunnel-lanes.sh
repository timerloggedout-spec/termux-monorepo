#!/data/data/com.termux/files/usr/bin/sh
# Consolidated tunnel-lane supervisor.  One process tree, one log, one lock.
# Logical lanes: hub(:8800) | pinggy-tcp(->8022) | pinggy-http(->8800)
#                serveo(->8022) | keeper(URL rotation -> gh secret)
# Managed by shell-forge.  Remove this file to disable all lanes.
mkdir -p "$HOME/.deepcli/locks" "$HOME/.deepcli/logs/boot"
exec 9>"$HOME/.deepcli/locks/50-tunnel-lanes.lock"
flock -n 9 || exit 0
termux-wake-lock

LOG="$HOME/.deepcli/logs/boot/50-tunnel-lanes.log"
[ -f "$LOG" ] && [ "$(stat -c%s "$LOG" 2>/dev/null || echo 0)" -gt 1048576 ] && \
  { tail -c 262144 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"; }

log() { printf '[%s] %s\n' "$(date -Iseconds)" "$1" >> "$LOG"; }
pgrp() { pgrep -f "$1" >/dev/null 2>&1; }

lane_hub() {
  curl -sf -m 4 http://127.0.0.1:8800/health >/dev/null 2>&1 && return 0
  if [ -x "$HOME/.local/bin/servers-up" ]; then
    log "hub down; launching servers-up"
    nohup "$HOME/.local/bin/servers-up" >> "$LOG" 2>&1 &
  else
    log "hub down; servers-up not executable"
  fi
}

lane_pinggy_tcp() {
  pgrp 'ssh .*-R0:localhost:8022 tcp@free.pinggy.io' && return 0
  log "(re)starting pinggy-tcp"
  ssh -p 443 \
    -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=accept-new \
    -R0:localhost:8022 tcp@free.pinggy.io >> "$LOG" 2>&1 &
}

lane_serveo() {
  pgrp 'ssh .*-R blu-b160v-1786968270-1bb6bc:8022:localhost:8022 serveo.net' && return 0
  log "(re)starting serveo"
  ssh -N -T \
    -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=accept-new \
    -R blu-b160v-1786968270-1bb6bc:8022:localhost:8022 serveo.net >> "$LOG" 2>&1 &
}

lane_pinggy_http() {
  curl -sf -m 4 http://127.0.0.1:8800/health >/dev/null 2>&1 || return 0
  if [ -s "$HOME/.deepcli/tunnel.url" ]; then
    URL=$(cat "$HOME/.deepcli/tunnel.url" 2>/dev/null)
    if [ -n "$URL" ] && \
       curl -sS --max-time 6 -o /dev/null -w '%{http_code}' "$URL/v1/models" 2>/dev/null \
         | grep -qE '^[2-4]'; then
      return 0
    fi
  fi
  pgrp 'ssh .*-R0:localhost:8800 qr@free.pinggy.io' && return 0
  log "(re)starting pinggy-http via tunnel-up"
  nohup "$HOME/.local/bin/tunnel-up" >> "$LOG" 2>&1 &
}

lane_keeper() {
  pgrp 'tunnel-keeper-loop' && return 0
  [ -x "$HOME/.local/bin/tunnel-keeper-loop" ] || return 0
  log "(re)starting tunnel-keeper-loop"
  nohup "$HOME/.local/bin/tunnel-keeper-loop" >> "$LOG" 2>&1 &
}

sleep 20
log "orchestrator up pid=$$"
while true; do
  lane_hub
  sleep 15
  lane_pinggy_tcp
  lane_serveo
  lane_pinggy_http
  lane_keeper
  sleep 45
done
