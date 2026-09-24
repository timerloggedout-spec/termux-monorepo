#!/usr/bin/env bash
set -euo pipefail

REPO="${TERMUX_BRIDGE_REPO:-timerloggedout-spec/termux-monorepo}"
REF="${TERMUX_BRIDGE_REF:-master}"
PATH_IN_REPO="${TERMUX_BRIDGE_PATH:-ops/termux-bridge/current.json}"
KEY="${TERMUX_MCP_SSH_KEY:-$HOME/.ssh/termux_mcp_client}"

command -v gh >/dev/null || { echo "gh is required" >&2; exit 1; }
command -v ssh >/dev/null || { echo "ssh is required" >&2; exit 1; }
test -r "$KEY" || { echo "SSH key not found: $KEY" >&2; exit 1; }

json="$(gh api "repos/$REPO/contents/$PATH_IN_REPO?ref=$REF" --jq '.content' | tr -d '\n' | base64 -d)"
host="$(printf '%s' "$json" | python -c 'import json,sys; print(json.load(sys.stdin)["endpoint"])')"
port="$(printf '%s' "$json" | python -c 'import json,sys; print(json.load(sys.stdin)["port"])')"
user="$(printf '%s' "$json" | python -c 'import json,sys; print(json.load(sys.stdin).get("ssh_user") or "")')"

test -n "$host" && test -n "$port" && test -n "$user" || {
  echo "bridge manifest is incomplete; wait for the Termux publisher to refresh it" >&2
  exit 1
}

exec ssh -i "$KEY" \
  -o IdentitiesOnly=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -p "$port" "$user@$host"
