#!/data/data/com.termux/files/usr/bin/sh
# start.sh — launch the tunnel loop detached (idempotent).
DIR="$HOME/b160v-persistent"
if command -v termux-wake-lock >/dev/null 2>&1; then
  termux-wake-lock >/dev/null 2>&1 || true
fi
pgrep sshd >/dev/null 2>&1 || sshd
setsid nohup sh "$DIR/b160v-tunnel.sh" >/dev/null 2>&1 &
echo "b160v-persistent: start requested"
