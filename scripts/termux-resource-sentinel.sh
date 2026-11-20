#!/data/data/com.termux/files/usr/bin/sh
# Deterministic Termux resource sentinel. It writes no logs or state.
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SNAPSHOT="$SCRIPT_DIR/termux-resource-snapshot.sh"
JOB_ID=43107

if [ ! -x "$SNAPSHOT" ]; then
  termux-notification --id "$JOB_ID" --title "Termux sentinel unavailable" --content "Resource snapshot script is missing or not executable."
  exit 0
fi

OUTPUT="$($SNAPSHOT 2>&1)"
STATUS="$(printf '%s\n' "$OUTPUT" | awk -F= '/^status=/{print $2; exit}')"

if [ "$STATUS" = "PRESSURE" ]; then
  MEMORY="$(printf '%s\n' "$OUTPUT" | awk -F= '/^memory_available_mib=/{print $2; exit}')"
  SWAP="$(printf '%s\n' "$OUTPUT" | awk -F= '/^swap_free_mib=/{print $2; exit}')"
  STORAGE="$(printf '%s\n' "$OUTPUT" | awk -F= '/^storage_used_percent=/{print $2; exit}')"
  termux-notification --id "$JOB_ID" --title "Termux resource pressure" --content "Memory ${MEMORY:-?} MiB; swap ${SWAP:-?} MiB; storage ${STORAGE:-?}. Review before heavy work."
fi
