#!/usr/bin/env bash
# AGY-1497-09. First verify the existing pinned SSH host key externally.
# JSON validation/transformation happens in settings.py on the controller.
# Local markers corroborate identity; they are not authentication or a sandbox.
set -euo pipefail
umask 077
mode=${1:-check}
case "$mode" in check|apply) ;; *) echo 'Usage: secondary_settings.sh check|apply BEFORE_SHA256 AFTER_SHA256' >&2; exit 2;; esac
root="$HOME/.local/share/agy-1497-secondary"
workspace="$root/worktree"
[[ "$PWD" == "$workspace" ]] || { echo 'STOP: wrong secondary workspace' >&2; exit 20; }
[[ -f .agy-secondary-id && ! -L .agy-secondary-id && "$(cat .agy-secondary-id)" == tmx-node-55619bd5 ]] || exit 21
[[ -f .git && ! -L .git ]] || exit 22
[[ "$(getprop ro.product.model)" == B160V && "$(whoami)" == u0_a243 ]] || exit 23
settings="$HOME/.gemini/antigravity-cli/settings.json"
[[ -f "$settings" && ! -L "$settings" ]] || exit 24
hash() { sha256sum -- "$1" | cut -d ' ' -f 1; }
if [[ "$mode" == check ]]; then
  printf 'IDENTITY_GUARDS_OK SETTINGS_SHA256=%s\n' "$(hash "$settings")"
  exit 0
fi
# These are the receipt from controller-side strict JSON validation, not user input.
before=${2:-}
after=${3:-}
[[ "$before" =~ ^[a-f0-9]{64}$ && "$after" =~ ^[a-f0-9]{64}$ ]] || exit 25
prepared="$root/verbosity-high.candidate.json"
[[ -f "$prepared" && ! -L "$prepared" && "$(hash "$prepared")" == "$after" ]] || exit 26
[[ "$(hash "$settings")" == "$before" ]] || { echo 'STOP: settings changed since validation' >&2; exit 30; }
if [[ "$before" == "$after" ]]; then
  echo 'VERIFIED: already matches JSON-validated High candidate; no change made'
  exit 0
fi
lock="$root/.verbosity-update.lock"
mkdir "$lock" || { echo 'STOP: update lock exists' >&2; exit 28; }
candidate=''
cleanup() {
  [[ -z "$candidate" ]] || rm -f -- "$candidate"
  rmdir -- "$lock"
}
trap cleanup EXIT
snapshot=$(mktemp "$root/settings-before-high.XXXXXX")
cat "$settings" > "$snapshot"
[[ "$(hash "$snapshot")" == "$before" ]] || exit 30
candidate=$(mktemp "${settings}.agy1497.XXXXXX")
cp -p -- "$settings" "$candidate"
cat "$prepared" > "$candidate"
[[ "$(hash "$candidate")" == "$after" ]] || exit 29
[[ "$(hash "$settings")" == "$before" ]] || { echo 'STOP: settings changed concurrently' >&2; exit 30; }
mv -- "$candidate" "$settings"
candidate=''
[[ "$(hash "$settings")" == "$after" ]] || exit 31
echo 'VERIFIED: installed exact JSON-validated High candidate; private rollback snapshot retained'
