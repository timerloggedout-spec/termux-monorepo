#!/data/data/com.termux/files/usr/bin/bash
# Schedule this node's tmx jobs (idempotent; existing jobs 43107-43109 are left untouched).
#   --role secondary : 43110 heartbeat + 43111 origin-status notification
#   --role origin    : 43110 heartbeat only (origin keeps its own 43107-43109 jobs)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
role="secondary"; [ "${1:-}" = "--role" ] && role="${2:-secondary}"
PERIOD_MS="${TMX_JOB_PERIOD_MS:-900000}"   # 15 min = Android JobScheduler minimum
tmx_have termux-job-scheduler || tmx_die "termux-job-scheduler missing (pkg install termux-api + Termux:API app)"
tmx_require_identity
chmod 700 "$SCRIPT_DIR"/*.sh
pending="$(termux-job-scheduler --pending 2>/dev/null || true)"
sched() {
  # Refuse to clobber a job id that already runs some other script.
  if printf '%s\n' "$pending" | grep -w -- "$1" | grep -qv -- "$(basename "$2")"; then
    tmx_die "job id $1 is already used by another script; set TMX_JOB_HEARTBEAT/TMX_JOB_ORIGIN_STATUS to free ids"
  fi
  termux-job-scheduler --job-id "$1" --script "$2" --period-ms "$PERIOD_MS" \
    --network any --battery-not-low false --storage-not-low false --persisted true >/dev/null
  tmx_log "job $1 -> $(basename "$2") every $((PERIOD_MS/60000)) min"
}
sched "$TMX_JOB_HEARTBEAT" "$SCRIPT_DIR/publish-device-heartbeat.sh"
if [ "$role" = secondary ]; then
  sched "$TMX_JOB_ORIGIN_STATUS" "$SCRIPT_DIR/origin-status-notify.sh"
fi
"$SCRIPT_DIR/publish-device-heartbeat.sh" || true
[ "$role" = secondary ] && { "$SCRIPT_DIR/origin-status-notify.sh" || true; }
termux-job-scheduler --pending
