#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="${TERMUX_BRIDGE_REPO:-timerloggedout-spec/termux-monorepo}"
BRANCH="${TERMUX_BRIDGE_BRANCH:-master}"
PATH_IN_REPO="${TERMUX_BRIDGE_PATH:-ops/termux-bridge/current.json}"
LOG="${TERMUX_REVERSE_SSH_LOG:-$HOME/.local/state/termux-mcp/reverse-ssh.log}"
USER_NAME="${TERMUX_SSH_USER:-$USER}"

command -v gh >/dev/null || { echo "gh is required" >&2; exit 1; }
test -r "$LOG" || { echo "reverse SSH log not found: $LOG" >&2; exit 1; }

endpoint="$(
  awk '/^tcp:\/\// { v=$0; sub(/^tcp:\/\//,"",v); print v }' "$LOG" |
  tail -n 1
)"
test -n "$endpoint" || { echo "no Pinggy tcp endpoint found in $LOG" >&2; exit 1; }

host="${endpoint%:*}"
port="${endpoint##*:}"
[[ "$host" != "$endpoint" && "$port" =~ ^[0-9]+$ ]] || { echo "invalid endpoint: $endpoint" >&2; exit 1; }

payload="$(
  python - "$host" "$port" "$USER_NAME" <<'PY'
import json, sys
host, port, user = sys.argv[1], int(sys.argv[2]), sys.argv[3]
print(json.dumps({
  "schema_version": 1,
  "status": "active",
  "transport": "pinggy-tcp-over-ssh",
  "endpoint": host,
  "port": port,
  "ssh_user": user,
  "remote_target": "127.0.0.1:8022",
  "source": "device-runtime",
  "expires_in_minutes": 60,
  "note": "Ephemeral endpoint. Updated automatically by the Termux publisher after reconnect. SSH private keys are never stored here."
}, indent=2) + "\n")
PY
)"

tmp="$(mktemp)"
old="$(mktemp)"
trap 'rm -f "$tmp" "$old"' EXIT
printf '%s' "$payload" >"$tmp"

current_json="$(gh api "repos/$REPO/contents/$PATH_IN_REPO?ref=$BRANCH" --jq '.content' 2>/dev/null || true)"
if [ -n "$current_json" ]; then
  printf '%s' "$current_json" | tr -d '\n' | base64 -d >"$old" || true
  if cmp -s "$tmp" "$old"; then
    echo "bridge manifest already current"
    exit 0
  fi
fi

sha="$(gh api "repos/$REPO/contents/$PATH_IN_REPO?ref=$BRANCH" --jq '.sha' 2>/dev/null || true)"
encoded="$(base64 -w 0 "$tmp")"

args=(-X PUT "repos/$REPO/contents/$PATH_IN_REPO"
  -f "message=ops(termux): publish live Pinggy bridge endpoint"
  -f "content=$encoded"
  -f "branch=$BRANCH")
if [ -n "$sha" ]; then
  args+=(-f "sha=$sha")
fi

gh api "${args[@]}" >/dev/null
printf 'published %s:%s as %s@%s\n' "$host" "$port" "$USER_NAME" "$REPO"
