#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${TERMUX_MONOREPO_ROOT:-$HOME/termux-monorepo}"
PUBLISHER="$ROOT/scripts/termux/publish-pinggy-endpoint.sh"
JOB_ID="${TERMUX_BRIDGE_PUBLISH_JOB_ID:-43109}"
PERIOD_MS="${TERMUX_BRIDGE_PUBLISH_PERIOD_MS:-900000}"
test -x "$PUBLISHER" || chmod 700 "$PUBLISHER"
command -v termux-job-scheduler >/dev/null || { echo "termux-job-scheduler is required" >&2; exit 1; }
command -v gh >/dev/null || { echo "gh is required" >&2; exit 1; }
"$PUBLISHER" || echo "initial publish deferred: tunnel endpoint not available yet" >&2
termux-job-scheduler --job-id "$JOB_ID" --script "$PUBLISHER" --period-ms "$PERIOD_MS" --battery-not-low false --storage-not-low false --persisted true
echo "installed Pinggy publisher as Termux job $JOB_ID (15-minute Android minimum)"
termux-job-scheduler --pending
