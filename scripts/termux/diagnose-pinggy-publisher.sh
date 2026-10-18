#!/data/data/com.termux/files/usr/bin/bash
# Read-only diagnosis of why the device's live Pinggy endpoint is not reaching
# ops/termux-bridge/current.json. Changes nothing unless you pass --publish.
# Usage (in Termux, e.g. via scrcpy or `adb shell` + run-as):
#   bash scripts/termux/diagnose-pinggy-publisher.sh            # diagnose only
#   bash scripts/termux/diagnose-pinggy-publisher.sh --publish  # then publish once
set -uo pipefail
ROOT="${TERMUX_MONOREPO_ROOT:-$HOME/termux-monorepo}"
LOG="${TERMUX_REVERSE_SSH_LOG:-$HOME/.local/state/termux-mcp/reverse-ssh.log}"
ok(){ printf '  [ok]   %s\n' "$*"; }; bad(){ printf '  [FAIL] %s\n' "$*"; }; info(){ printf '  [info] %s\n' "$*"; }
echo "== Pinggy publisher diagnosis $(date -Is)"
echo "-- tools"
for c in gh python ssh termux-job-scheduler; do command -v "$c" >/dev/null && ok "$c found" || bad "$c missing"; done
echo "-- gh auth"
if gh auth status >/dev/null 2>&1; then ok "gh authenticated"; else bad "gh not authenticated (run: gh auth login)"; fi
echo "-- repo checkout"
[ -d "$ROOT/.git" ] && ok "repo at $ROOT" || bad "no repo at $ROOT (set TERMUX_MONOREPO_ROOT)"
[ -x "$ROOT/scripts/termux/publish-pinggy-endpoint.sh" ] && ok "publisher script executable" || bad "publisher script missing or not executable"
echo "-- reverse SSH log"
if [ -r "$LOG" ]; then
  ok "log readable: $LOG ($(wc -l <"$LOG") lines, modified $(date -r "$LOG" -Is 2>/dev/null))"
  last="$(grep -Eo 'tcp://[^ ]+' "$LOG" | tail -n1)"
  start_tcp="$(grep -c '^tcp://' "$LOG" || true)"
  [ -n "$last" ] && ok "latest endpoint in log: $last" || bad "no tcp:// endpoint in log"
  [ "${start_tcp:-0}" -gt 0 ] || bad "no line STARTS with tcp:// -- publisher's awk filter (/^tcp:\\/\\//) will find nothing; endpoint may be embedded mid-line"
else
  bad "log not found: $LOG  -- the tunnel that shows 'Pinggy connected' likely logs elsewhere:"
  find "$HOME" -maxdepth 5 -name '*pinggy*.log' -o -maxdepth 5 -name 'reverse-ssh*.log' 2>/dev/null | head -n 10 | sed 's/^/         /'
fi
echo "-- scheduled jobs"
termux-job-scheduler --pending 2>/dev/null | grep -E 'Job 4310[789]' -A2 || bad "job 43109 (publisher) not pending -- run scripts/termux/install-pinggy-publisher-job.sh"
echo "-- tunnel processes"
pgrep -af 'pinggy|ssh .*-R' | sed 's/^/         /' || info "no ssh -R / pinggy process visible"
if [ "${1:-}" = "--publish" ]; then
  echo "-- publishing once"
  "$ROOT/scripts/termux/publish-pinggy-endpoint.sh" && ok "published" || bad "publish failed (see output above)"
fi
