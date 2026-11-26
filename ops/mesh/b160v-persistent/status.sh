#!/data/data/com.termux/files/usr/bin/sh
# status.sh — one-screen state of the persistent-SSH legs on the device.
DIR="$HOME/b160v-persistent"
echo "== b160v-persistent status =="
pgrep sshd >/dev/null 2>&1 && echo "sshd: RUNNING (port 8022)" || echo "sshd: NOT RUNNING"
if [ -f "$DIR/loop.pid" ] && kill -0 "$(cat "$DIR/loop.pid")" 2>/dev/null; then
  echo "tunnel loop: RUNNING (pid $(cat "$DIR/loop.pid"))"
else
  echo "tunnel loop: NOT RUNNING"
fi
echo "endpoint (local): $(cat "$DIR/last-endpoint" 2>/dev/null || echo none)"
python3 - <<'PY'
import os
tok = os.environ.get("B160V_GH_TOKEN") or os.environ.get("WEBWRAPPER_GH_TOKEN")
env = os.path.expanduser("~/b160v-persistent/token.env")
armed = bool(tok) or os.path.exists(env) or os.path.exists(os.path.expanduser("~/b160v-rendezvous/.git"))
print("rendezvous writer:", "ARMED" if armed else "NOT ARMED (see README: token.env)")
PY
echo "-- last tunnel log lines --"
tail -5 "$DIR/tunnel.log" 2>/dev/null || echo "(no log yet)"
