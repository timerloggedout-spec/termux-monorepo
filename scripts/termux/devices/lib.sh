#!/data/data/com.termux/files/usr/bin/bash
# Shared helpers for scripts/termux/devices/*. Source, do not execute.
# Additive lane: nothing here reads or writes files outside $HOME/.config/tmx-device,
# $HOME/.local/state/tmx-device and the explicit GitHub paths named below.

TMX_CONFIG_DIR="${TMX_CONFIG_DIR:-$HOME/.config/tmx-device}"
TMX_STATE_DIR="${TMX_STATE_DIR:-$HOME/.local/state/tmx-device}"
TMX_IDENTITY_ENV="$TMX_CONFIG_DIR/identity.env"

# Load identity first so per-device overrides (repo root, origin id) win over defaults.
# shellcheck disable=SC1090
[ -r "$TMX_IDENTITY_ENV" ] && . "$TMX_IDENTITY_ENV"

TMX_REPO="${TMX_REPO:-timerloggedout-spec/termux-monorepo}"
TMX_MASTER_BRANCH="${TMX_MASTER_BRANCH:-master}"
# Heartbeats go to a side branch so master history stays clean; commits carry [skip ci].
TMX_HEARTBEAT_BRANCH="${TMX_HEARTBEAT_BRANCH:-device-heartbeat}"
TMX_HEARTBEAT_DIR="${TMX_HEARTBEAT_DIR:-ops/devices/heartbeat}"
TMX_BRIDGE_MANIFEST="${TMX_BRIDGE_MANIFEST:-ops/termux-bridge/current.json}"
TMX_ORIGIN_DEVICE_ID="${TMX_ORIGIN_DEVICE_ID:-tmx-node-primary}"
TERMUX_MONOREPO_ROOT="${TERMUX_MONOREPO_ROOT:-$HOME/termux-monorepo}"
TERMUX_REVERSE_SSH_LOG="${TERMUX_REVERSE_SSH_LOG:-$HOME/.local/state/termux-mcp/reverse-ssh.log}"

# Termux job / notification ids. 43107-43109 belong to existing jobs; never reuse them.
TMX_JOB_HEARTBEAT="${TMX_JOB_HEARTBEAT:-43110}"
TMX_JOB_ORIGIN_STATUS="${TMX_JOB_ORIGIN_STATUS:-43111}"
TMX_NOTIFY_STATUS_ID="${TMX_NOTIFY_STATUS_ID:-43111}"
TMX_NOTIFY_ALERT_ID="${TMX_NOTIFY_ALERT_ID:-43112}"
TMX_NOTIFY_GUARD_ID="${TMX_NOTIFY_GUARD_ID:-43113}"
TMX_NOTIFY_CONTROL_ID="${TMX_NOTIFY_CONTROL_ID:-43114}"   # 🎮 controller pane

TMX_ID_REGEX='^tmx-node-[a-z0-9][a-z0-9-]{3,31}$'

tmx_die() { echo "tmx: $*" >&2; exit 1; }
tmx_log() { printf '[tmx %s] %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; }
tmx_have() { command -v "$1" >/dev/null 2>&1; }

tmx_require_identity() {
  [ -n "${TERMUX_DEVICE_ID:-}" ] || tmx_die "no device identity; run scripts/termux/devices/device-identity.sh init"
  printf '%s' "$TERMUX_DEVICE_ID" | grep -Eq "$TMX_ID_REGEX" || tmx_die "invalid TERMUX_DEVICE_ID '$TERMUX_DEVICE_ID'"
}

# tmx_gh_get_file <path> <ref>  -> prints decoded file content, non-zero if missing
tmx_gh_get_file() {
  local c
  c="$(gh api "repos/$TMX_REPO/contents/$1?ref=$2" --jq '.content' 2>/dev/null)" || return 1
  [ -n "$c" ] || return 1
  printf '%s' "$c" | tr -d '\n' | base64 -d
}

# tmx_gh_sha <path> <ref> -> blob sha or empty
tmx_gh_sha() {
  local s
  s="$(gh api "repos/$TMX_REPO/contents/$1?ref=$2" --jq '.sha' 2>/dev/null)" || return 0
  printf '%s' "$s" | grep -Eq '^[0-9a-f]{40}$' && printf '%s' "$s"
  return 0
}

# tmx_ensure_branch <branch>: create from master tip if missing (additive; never moves an existing ref)
tmx_ensure_branch() {
  gh api "repos/$TMX_REPO/branches/$1" >/dev/null 2>&1 && return 0
  local base
  base="$(gh api "repos/$TMX_REPO/git/ref/heads/$TMX_MASTER_BRANCH" --jq '.object.sha')" || return 1
  gh api -X POST "repos/$TMX_REPO/git/refs" -f "ref=refs/heads/$1" -f "sha=$base" >/dev/null
}

# tmx_gh_put_file <path> <branch> <local-file> <message>
tmx_gh_put_file() {
  local sha enc
  sha="$(tmx_gh_sha "$1" "$2")"
  enc="$(base64 -w 0 "$3")"
  local args=(-X PUT "repos/$TMX_REPO/contents/$1" -f "message=$4" -f "content=$enc" -f "branch=$2")
  [ -z "$sha" ] || args+=(-f "sha=$sha")
  gh api "${args[@]}" >/dev/null
}

# tmx_battery_json -> termux-battery-status JSON or {}
tmx_battery_json() {
  if tmx_have termux-battery-status; then
    timeout 20 termux-battery-status 2>/dev/null || echo '{}'
  else
    echo '{}'
  fi
}
