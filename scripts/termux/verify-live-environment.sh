#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${TERMUX_MONOREPO_ROOT:-$HOME/termux-monorepo}"
LOG="${TERMUX_REVERSE_SSH_LOG:-$HOME/.local/state/termux-mcp/reverse-ssh.log}"
JOB_ID="${TERMUX_BRIDGE_PUBLISH_JOB_ID:-43109}"
echo "== CLI =="; command -v git; git --version; command -v gh; gh --version | head -n1; gh auth status; git -C "$ROOT" rev-parse --show-toplevel; git -C "$ROOT" status --short --branch; git -C "$ROOT" remote -v | head -n2
echo "== Pinggy boot process =="; pgrep -af 'manus-termux-reverse-ssh|pinggy|ssh .*8022' || { echo "FAIL: no reverse-SSH/Pinggy process"; exit 2; }
echo "== Reverse SSH log =="; test -r "$LOG"; tail -n30 "$LOG"
echo "== Scheduled publisher =="; termux-job-scheduler --pending; termux-job-scheduler --pending | grep -q "$JOB_ID" || { echo "FAIL: publisher job $JOB_ID not pending"; exit 3; }
echo "== Current bridge manifest =="; gh api 'repos/timerloggedout-spec/termux-monorepo/contents/ops/termux-bridge/current.json?ref=master' --jq '.content' | tr -d '\n' | base64 -d
