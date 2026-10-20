#!/data/data/com.termux/files/usr/bin/bash
# ORIGIN-side allowlisted control verbs for the observer|controller node.
# Installed as the ssh forced command for the controller's key ONLY:
#   command="bash ~/termux-monorepo/scripts/termux/devices/tmx-ctl.sh",no-port-forwarding,no-agent-forwarding,no-pty ssh-ed25519 AAAA... tmx-node-55619bd5
# The verb comes from $SSH_ORIGINAL_COMMAND. Every verb is read-only or idempotent.
# Nothing here kills DeepAgent/core.py, restarts Pinggy (that would cut the very
# tunnel we are on), touches git state, or reuses jobs 43107-43109.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
verb="${SSH_ORIGINAL_COMMAND:-${1:-help}}"; verb="${verb%% *}"
log="$TMX_STATE_DIR/tmx-ctl.log"; mkdir -p "$TMX_STATE_DIR"
printf '%s %s\n' "$(date -u +%FT%TZ)" "$verb" >>"$log"
case "$verb" in
  status)        termux-battery-status 2>/dev/null | jq -c '{percentage,status,temperature}' 2>/dev/null; uptime ;;
  heartbeat-now) bash "$SCRIPT_DIR/publish-device-heartbeat.sh" && echo "heartbeat published" ;;
  wake-lock)     termux-wake-lock && echo "wake-lock held" ;;
  tunnel)        pgrep -fa 'pinggy|ssh .*-R' | sed 's/-i [^ ]*/-i ***/' || echo "no tunnel process" ;;
  agent)         pgrep -fa 'core\.py|Agent\.py|deepagent|deepcli' || echo "agent not running" ;;
  jobs)          termux-job-scheduler --pending 2>/dev/null | grep -E 'Pending|id' || echo "no pending jobs listed" ;;
  disk)          df -h "$HOME" | tail -1; du -sh "$TERMUX_MONOREPO_ROOT/.git" 2>/dev/null ;;
  help|*)        echo "verbs: status heartbeat-now wake-lock tunnel agent jobs disk"; [ "$verb" = help ] || exit 2 ;;
esac
