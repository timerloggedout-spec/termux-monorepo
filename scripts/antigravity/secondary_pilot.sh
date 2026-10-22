#!/usr/bin/env bash
# AGY-1497-07: explicit manual pilot, never a scheduled or daemon entry point.
set -euo pipefail
mode=${1:-preflight}
case "$mode" in preflight|verify|pilot) ;; *) echo 'Usage: bash secondary_pilot.sh preflight|verify|pilot' >&2; exit 2;; esac
expected="$HOME/.local/share/agy-1497-secondary/worktree"
[[ "$PWD" == "$expected" ]] || { echo 'STOP: wrong pilot workspace' >&2; exit 20; }
[[ -f .agy-secondary-id && ! -L .agy-secondary-id ]] || exit 21
[[ "$(cat .agy-secondary-id)" == 'tmx-node-55619bd5' ]] || exit 21
[[ -f .git && ! -L .git ]] || { echo 'STOP: expected linked thin worktree' >&2; exit 22; }
worktree_root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo 'STOP: git does not resolve this worktree' >&2; exit 22; }
[[ "$(cd -- "$worktree_root" && pwd -P)" == "$(pwd -P)" ]] || { echo 'STOP: git resolves a different worktree' >&2; exit 22; }
[[ -x "$HOME/.local/bin/agy" ]] || exit 23
export AGY_CLI_DISABLE_AUTO_UPDATE=true
if [[ "$mode" == preflight ]]; then
  "$HOME/.local/bin/agy" --version
  "$HOME/.local/bin/agy" agents
  printf 'PREFLIGHT_OK: secondary marker, dedicated linked worktree, installed CLI\n'
  exit 0
fi
if [[ "$mode" == pilot ]]; then
  [[ ! -e pilot-result.txt && ! -L pilot-result.txt ]] || { echo 'STOP: pilot result already exists; do not replay' >&2; exit 24; }
  attempt_marker=.pilot-attempted
  [[ ! -e "$attempt_marker" && ! -L "$attempt_marker" ]] || { echo 'STOP: pilot attempt already reserved; do not replay' >&2; exit 24; }
  # Exclusive creation reserves the one permitted model call, including failures/timeouts.
  ( set -o noclobber; printf 'reserved\n' > "$attempt_marker" ) || { echo 'STOP: pilot attempt already reserved; do not replay' >&2; exit 24; }
  # Supported by observed 1.4.5 help. One bounded model request; no retries.
  "$HOME/.local/bin/agy" --agent agy-implementer --effort low --print-timeout 90s --output-format json --print 'AGY-1497-07 bounded operational pilot. Work only in the current directory. Create exactly one new file pilot-result.txt with exactly AGY1497_OK followed by one newline. Do not modify any other file, settings, permissions, agents or skills; do not read credentials, access other directories, call networks, publish, spawn agents, install or update. Report the created path and stop.'
fi
[[ -f pilot-result.txt && ! -L pilot-result.txt ]] || { echo 'FAIL: regular pilot result missing' >&2; exit 25; }
[[ "$(wc -c < pilot-result.txt | tr -d ' ')" == 11 ]] || { echo 'FAIL: result byte count' >&2; exit 26; }
cmp -s -- pilot-result.txt <(printf 'AGY1497_OK\n') || { echo 'FAIL: result content' >&2; exit 27; }
printf 'PILOT_VERIFIED: exact regular file content; discovery and dispatch are separate evidence\n'
