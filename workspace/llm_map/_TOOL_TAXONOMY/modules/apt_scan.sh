#!/data/data/com.termux/files/usr/bin/bash
MODE="$1"; STATE_DIR="$2"; OUTFILE="$3"; source "$(dirname "$0")/common.sh"
if should_full_scan; then
    pkg list-installed 2>/dev/null | awk '{print $1}' | cut -d/ -f1 | sort -u > "$STATE_DIR/pkg_list.txt"
    while read -r pkg; do
        desc=$(pkg show "$pkg" 2>/dev/null | grep -E '^Description:' | head -1 | sed 's/^Description: //' || echo "")
        echo "$pkg|$desc"
    done < "$STATE_DIR/pkg_list.txt" > "$STATE_DIR/pkg_desc.txt"

    echo "[apt] Building package file maps..."
    while read -r pkg; do
        dpkg -L "$pkg" 2>/dev/null | grep -E '^/data/data/com.termux/files/usr/(local/)?bin/' > "$STATE_DIR/pkg_$pkg.txt"
    done < "$STATE_DIR/pkg_list.txt"

    echo "[apt] Scanning executables..."
    find /data/data/com.termux/files/usr/bin /data/data/com.termux/files/usr/local/bin /data/data/com.termux/files/usr/glibc/bin -type f -executable 2>/dev/null | \
    while read -r exe; do
        name=$(basename "$exe")
        owner=$(grep -lFx "$exe" "$STATE_DIR"/pkg_*.txt 2>/dev/null | head -1 | sed 's|.*/pkg_||;s|\.txt||')
        [ -z "$owner" ] && owner="unknown"
        echo "{\"name\":\"$name\",\"package\":\"$owner\",\"path\":\"$exe\",\"source\":\"apt\"}"
    done > "$OUTFILE"
else
    # incremental (unchanged)
    last_ts=$(cat "$STATE_DIR/last_run_time")
    dpkg --log /data/data/com.termux/files/usr/var/log/dpkg.log 2>/dev/null | awk -v ts="$last_ts" '$0 > ts && / install / {print $5}' | sort -u > "$STATE_DIR/new_pkgs.txt"
    while read -r pkg; do
        dpkg -L "$pkg" 2>/dev/null | grep -E '^/data/data/com.termux/files/usr/(local/)?bin/' | while read -r exe; do
            [ -x "$exe" ] || continue
            name=$(basename "$exe")
            echo "{\"name\":\"$name\",\"package\":\"$pkg\",\"path\":\"$exe\",\"source\":\"apt\"}"
        done
    done < "$STATE_DIR/new_pkgs.txt" > "$OUTFILE"
    cat "$STATE_DIR/new_pkgs.txt" >> "$STATE_DIR/pkg_list.txt"
fi
