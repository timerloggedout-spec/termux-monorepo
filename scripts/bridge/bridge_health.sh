#!/data/data/com.termux/files/usr/bin/bash
# bridge_health.sh - single entrypoint for hub+tunnel health.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
URLFILE="$HOME/.deepcli/tunnel.url"
REPO="timerloggedout-spec/termux-monorepo"

say() { printf "\n-- %s --\n" "$1"; }

cmd="${1:-all}"

case "$cmd" in
  local)
    python3 "$SCRIPT_DIR/health_probe.py" local ;;
  external)
    python3 "$SCRIPT_DIR/health_probe.py" external "$URLFILE" ;;
  add-route)
    say ROUTE
    python3 "$SCRIPT_DIR/health_route.py"
    rc=$?
    if [ "$rc" -eq 0 ]; then
      say RESTART
      pkill -f "deepcli/server.py" 2>/dev/null
      sleep 2
      nohup "$HOME/.local/bin/servers-up" >/dev/null 2>&1 &
      disown 2>/dev/null
      sleep 10
      say LOCAL
      python3 "$SCRIPT_DIR/health_probe.py" local
    fi ;;
  all)
    python3 "$SCRIPT_DIR/health_route.py"
    rc=$?
    if [ "$rc" -eq 0 ]; then
      pkill -f "deepcli/server.py" 2>/dev/null
      sleep 2
      nohup "$HOME/.local/bin/servers-up" >/dev/null 2>&1 &
      disown 2>/dev/null
      sleep 10
    fi
    say LOCAL
    python3 "$SCRIPT_DIR/health_probe.py" local
    LRC=$?
    say EXTERNAL
    python3 "$SCRIPT_DIR/health_probe.py" external "$URLFILE"
    ERC=$?
    if [ "$LRC" -eq 0 ] && [ "$ERC" -eq 0 ]; then
      say CANARY
      gh workflow run tunnel-canary.yml --repo "$REPO" 2>/dev/null
    fi ;;
  *)
    echo "usage: bridge_health.sh {local|external|add-route|all}"
    exit 2 ;;
esac
