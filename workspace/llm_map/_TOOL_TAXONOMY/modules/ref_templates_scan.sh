#!/data/data/com.termux/files/usr/bin/bash
MODE="$1"; STATE_DIR="$2"; OUTFILE="$3"; source "$(dirname "$0")/common.sh"
REF_DIR="$HOME/refTemplates"
find "$REF_DIR" -type f -executable \( -name "*.sh" -o -name "*.py" -o -name "*.rb" -o -name "*.lua" \) 2>/dev/null | while read -r script; do
    name=$(basename "$script")
    echo "{\"name\":\"$name\",\"package\":\"ref_templates\",\"path\":\"$script\",\"source\":\"ref_templates\"}"
done > "$OUTFILE"
