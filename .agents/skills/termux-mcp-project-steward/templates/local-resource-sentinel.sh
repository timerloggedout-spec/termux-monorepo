#!/data/data/com.termux/files/usr/bin/sh
# Set TERMUX_PROJECT_ROOT before scheduling this template.
set -eu

PROJECT_ROOT="${TERMUX_PROJECT_ROOT:-$HOME}"
SNAPSHOT="$PROJECT_ROOT/scripts/termux-resource-snapshot.sh"

if [ ! -x "$SNAPSHOT" ]; then
  termux-notification --id 43107 --title "Termux sentinel requires setup" --content "Install an executable resource snapshot script at the configured project path."
  exit 0
fi

OUTPUT="$("$SNAPSHOT" 2>&1)"
STATUS="$(printf '%s\n' "$OUTPUT" | awk -F= '/^status=/{print $2; exit}')"

if [ "$STATUS" = "PRESSURE" ]; then
  MEMORY="$(printf '%s\n' "$OUTPUT" | awk -F= '/^memory_available_mib=/{print $2; exit}')"
  SWAP="$(printf '%s\n' "$OUTPUT" | awk -F= '/^swap_free_mib=/{print $2; exit}')"
  STORAGE="$(printf '%s\n' "$OUTPUT" | awk -F= '/^storage_used_percent=/{print $2; exit}')"
  termux-notification --id 43107 --title "Termux resource pressure" --content "Memory ${MEMORY:-?} MiB; swap ${SWAP:-?} MiB; storage ${STORAGE:-?}. Review resource pressure before heavy work."
fi
