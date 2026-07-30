LAST_RUN_FILE="$STATE_DIR/last_run_time"
function should_full_scan() {
    if [ "$MODE" = "full" ] || [ ! -f "$LAST_RUN_FILE" ]; then return 0; else return 1; fi
}
