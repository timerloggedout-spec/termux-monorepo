#!/data/data/com.termux/files/usr/bin/sh
# b160v-tunnel.sh — persistent reverse-tunnel loop for the B160V (Termux).
#
# Keeps a Pinggy free TCP tunnel to the local Termux sshd (127.0.0.1:8022)
# alive forever: Pinggy caps a free tunnel at ~60 min, so when ssh exits
# this loop restarts it after a short pause and publishes the NEW endpoint
# to the rendezvous file (see rendezvous-push.py) after every reconnect.
# Started at boot by ~/.termux/boot/10-b160v-tunnel.sh; safe to run once —
# a pidfile keeps a single instance.
set -u
DIR="$HOME/b160v-persistent"
mkdir -p "$DIR"
PIDFILE="$DIR/loop.pid"
if [ -f "$PIDFILE" ]; then
  OLD=$(cat "$PIDFILE" 2>/dev/null || echo "")
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "b160v-tunnel: already running (pid $OLD)"
    exit 0
  fi
fi
echo $$ > "$PIDFILE"
LOG="$DIR/tunnel.log"
OUT="$DIR/last-run.log"
LAST_EP="$DIR/last-endpoint"
log() { echo "$(date '+%Y-%m-%dT%H:%M:%S') $*" >> "$LOG"; }
log "loop start (pid $$)"
while true; do
  pgrep sshd >/dev/null 2>&1 || { sshd && log "sshd started"; }
  : > "$OUT"
  ssh -p 443 -R0:127.0.0.1:8022 \
      -o StrictHostKeyChecking=no \
      -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
      -o ExitOnForwardFailure=yes \
      -i "$HOME/.ssh/id_ed25519" \
      tcp@free.pinggy.io >> "$OUT" 2>&1 &
  SSHPID=$!
  # Poll the tunnel output for the assigned endpoint; publish on change.
  I=0
  while [ $I -lt 60 ]; do
    EP=$(grep -oE 'tcp://[A-Za-z0-9.-]+:[0-9]+' "$OUT" 2>/dev/null | head -1)
    if [ -n "$EP" ]; then
      PREV=$(cat "$LAST_EP" 2>/dev/null || echo "")
      if [ "$EP" != "$PREV" ]; then
        echo "$EP" > "$LAST_EP"
        log "endpoint: $EP"
        python3 "$DIR/rendezvous-push.py" "$EP" >> "$LOG" 2>&1 \
          || log "rendezvous push FAILED (see above)"
      fi
      break
    fi
    kill -0 $SSHPID 2>/dev/null || break
    I=$((I+1)); sleep 2
  done
  wait $SSHPID
  log "tunnel exited (rc=$?) — restarting in 5s"
  sleep 5
done
