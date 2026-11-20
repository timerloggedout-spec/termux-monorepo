#!/data/data/com.termux/files/usr/bin/bash
MODE="$1"; STATE_DIR="$2"; OUTFILE="$3"; source "$(dirname "$0")/common.sh"
CUSTOM_DIRS=(
    "$HOME/workspace/llm_map"
    "$HOME/harmony_hub/utility_belt"
    "$HOME/archwiz"
    "$HOME/deepcli-tui"
    "$HOME/forensic-indexer"
    "$HOME/deepseek-cli"
    "$HOME/synthegration-cli"
    "$HOME/multi-ai-cli"
    "$HOME/cli-synthegration"
    "$HOME/bin"
    "$HOME/.local/bin"
    # Add any other directories here
)
alias > "$STATE_DIR/alias_curr.txt"
if should_full_scan; then
    for dir in "${CUSTOM_DIRS[@]}"; do
        [ -d "$dir" ] || continue
        find "$dir" -type f \( -perm -111 -o -name "*.sh" -o -name "*.py" -o -name "*.rb" -o -name "*.lua" \) 2>/dev/null | \
        while read -r script; do
            name=$(basename "$script")
            alias_name=$(grep -F "$script" "$STATE_DIR/alias_curr.txt" 2>/dev/null | head -1 | cut -d= -f1 | sed 's/alias //' || echo "")
            if [ -n "$alias_name" ] || [ -x "$script" ]; then
                if [ -n "$alias_name" ]; then
                    echo "{\"name\":\"$alias_name\",\"package\":\"alias\",\"path\":\"$script\",\"source\":\"custom\"}"
                else
                    echo "{\"name\":\"$name\",\"package\":\"custom\",\"path\":\"$script\",\"source\":\"custom\"}"
                fi
            fi
        done
    done > "$OUTFILE"
    cp "$STATE_DIR/alias_curr.txt" "$STATE_DIR/alias_prev.txt"
else
    last_ts=$(cat "$STATE_DIR/last_run_time")
    for dir in "${CUSTOM_DIRS[@]}"; do
        [ -d "$dir" ] || continue
        find "$dir" -type f \( -perm -111 -o -name "*.sh" -o -name "*.py" -o -name "*.rb" -o -name "*.lua" \) -newer "$STATE_DIR/last_run_time" 2>/dev/null | \
        while read -r script; do
            name=$(basename "$script")
            alias_name=$(grep -F "$script" "$STATE_DIR/alias_curr.txt" 2>/dev/null | head -1 | cut -d= -f1 | sed 's/alias //' || echo "")
            if [ -n "$alias_name" ] || [ -x "$script" ]; then
                if [ -n "$alias_name" ]; then
                    echo "{\"name\":\"$alias_name\",\"package\":\"alias\",\"path\":\"$script\",\"source\":\"custom\"}"
                else
                    echo "{\"name\":\"$name\",\"package\":\"custom\",\"path\":\"$script\",\"source\":\"custom\"}"
                fi
            fi
        done
    done > "$OUTFILE"
    cp "$STATE_DIR/alias_curr.txt" "$STATE_DIR/alias_prev.txt"
fi
