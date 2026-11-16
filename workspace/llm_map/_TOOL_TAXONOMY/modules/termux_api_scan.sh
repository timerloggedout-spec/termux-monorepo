#!/data/data/com.termux/files/usr/bin/bash
source "$(dirname "$0")/common.sh"
MODE="$1"; STATE_DIR="$2"; OUTFILE="$3"
ls -1 /data/data/com.termux/files/usr/bin/termux-* 2>/dev/null | while read -r api_bin; do
    name=$(basename "$api_bin")
    echo "{\"name\":\"$name\",\"package\":\"termux-api\",\"path\":\"$api_bin\",\"source\":\"termux_api\"}"
done > "$OUTFILE"
