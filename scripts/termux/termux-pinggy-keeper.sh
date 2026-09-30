#!/data/data/com.termux/files/usr/bin/sh
set -eu

TERMUX_PREFIX="/data/data/com.termux/files/usr"
SSH_BIN="$TERMUX_PREFIX/bin/ssh"
STATE_DIR="$HOME/.local/state/termux-mcp"
PID_FILE="$STATE_DIR/reverse-ssh.pid"
LOG_FILE="$STATE_DIR/reverse-ssh.log"
LOCK_DIR="$STATE_DIR/keeper.lock"
PUBLISHER="$HOME/.local/bin/termux-pinggy-publisher"
STATUS="$HOME/.local/bin/termux-pinggy-status"

mkdir -p "$STATE_DIR"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  exit 0
fi
cleanup() { rmdir "$LOCK_DIR" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

running=0
if [ -s "$PID_FILE" ]; then
  pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  case "$pid" in
    ''|*[!0-9]*) ;;
    *)
      if kill -0 "$pid" 2>/dev/null && [ -r "/proc/$pid/cmdline" ] && tr '\0' ' ' < "/proc/$pid/cmdline" | grep -q 'free\.pinggy\.io'; then
        running=1
      fi
      ;;
  esac
fi

if [ "$running" -eq 0 ]; then
  rm -f "$PID_FILE"
  nohup "$SSH_BIN" -p 443 \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes \
    -o StrictHostKeyChecking=accept-new \
    -R0:localhost:8022 tcp@free.pinggy.io \
    >> "$LOG_FILE" 2>&1 &
  printf '%s\n' "$!" > "$PID_FILE"
fi

if [ -x "$PUBLISHER" ]; then
  "$PUBLISHER" || true
fi
if [ -x "$STATUS" ]; then
  "$STATUS" || true
fi
