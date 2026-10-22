#!/data/data/com.termux/files/usr/bin/bash
# Schedule this node's tmx jobs (idempotent; existing jobs 43107-43109 are left untouched).
#   --role secondary : 43110 heartbeat + 43111 origin-status notification
#   --role origin    : 43110 heartbeat + 43112 queue-poll (origin keeps its own 43107-43109 jobs)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
role="secondary"; [ "${1:-}" = "--role" ] && role="${2:-secondary}"
PERIOD_MS="${TMX_JOB_PERIOD_MS:-900000}"   # 15 min = Android JobScheduler minimum
tmx_have termux-job-scheduler || tmx_die "termux-job-scheduler missing (pkg install termux-api + Termux:API app)"
tmx_require_identity
# Jobs run tiny wrappers outside the repo, so tracked files keep their git mode (no chmod in the checkout).
JOB_DIR="$HOME/.local/share/tmx-device/jobs"; mkdir -p "$JOB_DIR"
wrap() {
  local w="$JOB_DIR/$(basename "$1")"
  printf '#!%s/bin/bash\nexec bash %q "$@"\n' "${PREFIX:-/data/data/com.termux/files/usr}" "$1" >"$w"
  chmod 700 "$w"; printf '%s' "$w"
}
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
sched "$TMX_JOB_HEARTBEAT" "$(wrap "$SCRIPT_DIR/publish-device-heartbeat.sh")"
if [ "$role" = secondary ]; then
  sched "$TMX_JOB_ORIGIN_STATUS" "$(wrap "$SCRIPT_DIR/origin-status-notify.sh")"
fi
if [ "$role" = origin ]; then
  sched "$TMX_JOB_QUEUE_POLL" "$(wrap "$SCRIPT_DIR/queue-poll.sh")"
fi
bash "$SCRIPT_DIR/publish-device-heartbeat.sh" || true
if [ "$role" = secondary ]; then bash "$SCRIPT_DIR/origin-status-notify.sh" || true; fi
termux-job-scheduler --pending
