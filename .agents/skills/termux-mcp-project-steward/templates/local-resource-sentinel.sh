#!/data/data/com.termux/files/usr/bin/sh
# Deterministic, read-only resource sentinel. It writes no logs or state.
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="${TERMUX_PROJECT_ROOT:-$(CDPATH= cd -- "$SCRIPT_DIR/../../../.." && pwd)}"
SNAPSHOT="$PROJECT_ROOT/scripts/termux-resource-snapshot.sh"

if ! command -v termux-notification >/dev/null 2>&1; then
  exit 0
fi

if [ ! -x "$SNAPSHOT" ]; then
  termux-notification --id 43107 --title "Termux sentinel requires setup" --content "Install an executable resource snapshot script at the configured project path."
  exit 0
fi

OUTPUT=""
if OUTPUT="$("$SNAPSHOT" 2>&1)"; then
  SNAPSHOT_EXIT=0
else
  SNAPSHOT_EXIT=$?
fi

STATUS="$(printf '%s\n' "$OUTPUT" | awk -F= '/^status=/{print $2; exit}')"

if [ "$SNAPSHOT_EXIT" -ne 0 ] || { [ "$STATUS" != "OK" ] && [ "$STATUS" != "PRESSURE" ]; }; then
  DIAGNOSTICS="$(printf '%s\n' "$OUTPUT" | tail -n 4 | tr '\n' ' ')"
  termux-notification --id 43107 --title "Termux resource health unknown" --content "Snapshot exit $SNAPSHOT_EXIT; diagnostics: ${DIAGNOSTICS:-no output}. Review the snapshot before heavy work."
  exit 0
fi

if [ "$STATUS" = "PRESSURE" ]; then
  MEMORY="$(printf '%s\n' "$OUTPUT" | awk -F= '/^memory_available_mib=/{print $2; exit}')"
  SWAP="$(printf '%s\n' "$OUTPUT" | awk -F= '/^swap_free_mib=/{print $2; exit}')"
  STORAGE="$(printf '%s\n' "$OUTPUT" | awk -F= '/^storage_used_percent=/{print $2; exit}')"
  termux-notification --id 43107 --title "Termux resource pressure" --content "Memory ${MEMORY:-?} MiB; swap ${SWAP:-?} MiB; storage ${STORAGE:-?}. Review resource pressure before heavy work."
fi
