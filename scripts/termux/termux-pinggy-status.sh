#!/data/data/com.termux/files/usr/bin/sh
set -eu

STATE_DIR="$HOME/.local/state/termux-mcp"
PID_FILE="$STATE_DIR/reverse-ssh.pid"
LOG_FILE="$STATE_DIR/reverse-ssh.log"
STATUS_FILE="$STATE_DIR/pinggy-status"
NOTIFICATION_ID=43109

mkdir -p "$STATE_DIR"

pid="$(cat "$PID_FILE" 2>/dev/null || true)"
endpoint="$(tail -200 "$LOG_FILE" 2>/dev/null | sed -n 's#^tcp://\([A-Za-z0-9.-]*:[0-9][0-9]*\)$#tcp://\1#p' | tail -1)"

connected=0
case "$pid" in
  ''|*[!0-9]*) ;;
  *)
    if kill -0 "$pid" 2>/dev/null && [ -n "$endpoint" ]; then
      connected=1
    fi
    ;;
esac

if [ "$connected" -eq 1 ]; then
  state="connected|$endpoint"
  title="Pinggy connected"
  content="Endpoint active: $endpoint"
else
  state="disconnected"
  title="Pinggy disconnected"
  content="No active tunnel endpoint; keeper will retry on its next run."
fi

previous="$(cat "$STATUS_FILE" 2>/dev/null || true)"
if [ "$state" != "$previous" ] && command -v termux-notification >/dev/null 2>&1; then
  termux-notification --id "$NOTIFICATION_ID" --title "$title" --content "$content" --priority high
fi

printf '%s\n' "$state" > "$STATUS_FILE"
chmod 600 "$STATUS_FILE"
