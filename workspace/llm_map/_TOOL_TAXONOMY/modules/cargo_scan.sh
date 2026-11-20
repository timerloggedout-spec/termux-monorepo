#!/data/data/com.termux/files/usr/bin/bash
source "$(dirname "$0")/common.sh"
MODE="$1"; STATE_DIR="$2"; OUTFILE="$3"
cargo install --list 2>/dev/null | grep -E '^[a-zA-Z0-9_-]+ v' | awk '{print $1}' > "$STATE_DIR/cargo_curr.txt"
if should_full_scan || ! diff -q "$STATE_DIR/cargo_curr.txt" "$STATE_DIR/cargo_prev.txt" >/dev/null 2>&1; then
    while read -r crate; do
        bin_path="/data/data/com.termux/files/usr/bin/$crate"
        [ -x "$bin_path" ] && echo "{\"name\":\"$crate\",\"package\":\"cargo:$crate\",\"path\":\"$bin_path\",\"source\":\"cargo\"}"
    done < "$STATE_DIR/cargo_curr.txt" > "$OUTFILE"
    cp "$STATE_DIR/cargo_curr.txt" "$STATE_DIR/cargo_prev.txt"
fi
