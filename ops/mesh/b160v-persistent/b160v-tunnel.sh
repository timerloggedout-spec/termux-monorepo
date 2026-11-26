#!/data/data/com.termux/files/usr/bin/sh
# b160v-tunnel.sh — persistent Cloudflare tunnel loop for the B160V (Termux).
#
# Keeps a Cloudflare tunnel to the local Termux sshd (127.0.0.1:8022)
# alive forever and keeps the rendezvous file current (see
# rendezvous-push.py). Two modes, from ~/b160v-persistent/cf.env:
#
#   named (primary): a named tunnel on the owner's Cloudflare zone.
#     Needs ~/b160v-persistent/cf-token (the tunnel token, 0600) and
#     CF_HOSTNAME=<stable hostname> in cf.env. The hostname never
#     rotates; the loop heartbeats the rendezvous file every 600 s.
#   quick (alternate): an anonymous *.trycloudflare.com tunnel.
#     No account needed, but the hostname rotates at every restart —
#     and the muse-vm egress is blocked at the Cloudflare edge for the
#     trycloudflare zone (measured 2026-11-26), so this mode is for
#     reaching the device from other, unblocked egresses only.
#
# Installed as ~/bin/b160v-tunnel.sh; kept alive by ~/bin/supervisor.sh
# (its stanza is added by install.sh) and started at boot by
# ~/.termux/boot/20-b160v-persistent.sh. A pidfile keeps a single instance.
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
CF_MODE="named"; CF_HOSTNAME=""
[ -f "$DIR/cf.env" ] && . "$DIR/cf.env"
log "loop start (pid $$, mode $CF_MODE)"
while true; do
  pgrep sshd >/dev/null 2>&1 || { sshd && log "sshd started"; }
  if ! command -v cloudflared >/dev/null 2>&1; then
    log "cloudflared missing — run install.sh (pkg install cloudflared)"
    sleep 60
    continue
  fi
  : > "$OUT"
  if [ "$CF_MODE" = "quick" ]; then
    cloudflared tunnel --no-autoupdate --protocol http2 \
      --url tcp://127.0.0.1:8022 >> "$OUT" 2>&1 &
    CFPID=$!
    # Poll the tunnel output for the assigned hostname; publish on change.
    I=0
    while [ $I -lt 60 ]; do
      EP=$(grep -oE '[A-Za-z0-9-]+\.trycloudflare\.com' "$OUT" 2>/dev/null | head -1)
      if [ -n "$EP" ]; then
        PREV=$(cat "$LAST_EP" 2>/dev/null || echo "")
        if [ "$EP" != "$PREV" ]; then
          echo "$EP" > "$LAST_EP"
          log "endpoint: $EP"
          python3 "$DIR/rendezvous-push.py" "$EP" cloudflare-quick >> "$LOG" 2>&1 \
            || log "rendezvous push FAILED (see above)"
        fi
        break
      fi
      kill -0 $CFPID 2>/dev/null || break
      I=$((I+1)); sleep 2
    done
    wait $CFPID
  else
    if [ ! -f "$DIR/cf-token" ] || [ -z "$CF_HOSTNAME" ]; then
      log "named mode NOT ARMED — need $DIR/cf-token and CF_HOSTNAME in cf.env (see README)"
      sleep 60
      continue
    fi
    TUNNEL_TOKEN=$(cat "$DIR/cf-token")
    export TUNNEL_TOKEN
    cloudflared tunnel --no-autoupdate run >> "$OUT" 2>&1 &
    CFPID=$!
    # Stable hostname: publish once, then heartbeat while the tunnel lives.
    echo "$CF_HOSTNAME" > "$LAST_EP"
    python3 "$DIR/rendezvous-push.py" "$CF_HOSTNAME" cloudflare-named >> "$LOG" 2>&1 \
      || log "rendezvous push FAILED (see above)"
    while kill -0 $CFPID 2>/dev/null; do
      sleep 600
      kill -0 $CFPID 2>/dev/null || break
      python3 "$DIR/rendezvous-push.py" "$CF_HOSTNAME" cloudflare-named >> "$LOG" 2>&1 \
        || log "rendezvous heartbeat FAILED (see above)"
    done
    wait $CFPID
    unset TUNNEL_TOKEN
  fi
  log "tunnel exited (rc=$?) — restarting in 5s"
  sleep 5
done
