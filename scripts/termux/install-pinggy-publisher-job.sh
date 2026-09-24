#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${TERMUX_MONOREPO_ROOT:-$HOME/termux-monorepo}"
PUBLISHER="$ROOT/scripts/termux/publish-pinggy-endpoint.sh"
JOB_ID="${TERMUX_BRIDGE_PUBLISH_JOB_ID:-43109}"

test -x "$PUBLISHER" || chmod 700 "$PUBLISHER"
command -v termux-job-scheduler >/dev/null || { echo "termux-job-scheduler is required" >&2; exit 1; }
command -v gh >/dev/null || { echo "gh is required" >&2; exit 1; }

# Publish immediately, then refresh every five minutes. This does not modify jobs 43107/43108.
"$PUBLISHER" || echo "initial publish deferred: tunnel endpoint not available yet" >&2

termux-job-scheduler \
  --job-id "$JOB_ID" \
  --script "$PUBLISHER" \
  --period-ms 300000 \
  --battery-not-low false \
  --storage-not-low false \
  --persisted true

echo "installed Pinggy publisher as Termux job $JOB_ID"
termux-job-scheduler --pending
