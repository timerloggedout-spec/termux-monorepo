#!/data/data/com.termux/files/usr/bin/bash
# install.sh — idempotent installer for hygiene-watchdog sv service.
set -eu
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
SVDIR="$PREFIX/var/service"
HERE="$(cd "$(dirname "$0")" && pwd)"
WD_TARGET="$HOME/.local/bin/hygiene-watchdog"

mkdir -p "$(dirname "$WD_TARGET")"
cp "$HERE/hygiene-watchdog" "$WD_TARGET"
chmod 755 "$WD_TARGET"

SVC="$SVDIR/hygiene-watchdog"
mkdir -p "$SVC/log"
cp "$HERE/sv/run"     "$SVC/run"
cp "$HERE/sv/log/run" "$SVC/log/run"
chmod 755 "$SVC/run" "$SVC/log/run"
mkdir -p "$HOME/.deepcli/logs/hygiene/sv"

# leave it DOWN until operator enables
touch "$SVC/down"

echo "installed.  to enable:"
echo "  rm $SVC/down"
echo "  sv up hygiene-watchdog"
