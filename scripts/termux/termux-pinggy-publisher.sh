#!/data/data/com.termux/files/usr/bin/sh
set -eu

STATE_DIR="$HOME/.local/state/termux-mcp"
LOG_FILE="$STATE_DIR/reverse-ssh.log"
LAST_FILE="$STATE_DIR/last-published-endpoint"
REPO="timerloggedout-spec/termux-monorepo"

[ -r "$LOG_FILE" ] || exit 0

endpoint="$(tail -200 "$LOG_FILE" | sed -n 's#^tcp://\([A-Za-z0-9.-]*:[0-9][0-9]*\)$#tcp://\1#p' | tail -1)"
[ -n "$endpoint" ] || exit 0

last="$(cat "$LAST_FILE" 2>/dev/null || true)"
[ "$endpoint" = "$last" ] && exit 0

# Do not expose credentials or use a token on the command line.
if ! gh auth status >/dev/null 2>&1; then
  exit 0
fi

# The endpoint is public routing metadata, not a credential; publish it as a
# repository variable so Actions can consume the current allocation.
gh variable set TERMUX_MCP_ENDPOINT --repo "$REPO" --body "$endpoint" >/dev/null
gh variable set TERMUX_MCP_ENDPOINT_UPDATED_AT --repo "$REPO" --body "$(date -Iseconds)" >/dev/null
printf '%s\n' "$endpoint" > "$LAST_FILE"
chmod 600 "$LAST_FILE"
