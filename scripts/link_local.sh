#!/usr/bin/env bash
# link_local.sh — recreate the device-local symlinks declared in scripts/links.manifest.
#
# Committing symlinks that point at /data/data/com.termux/files/home/... makes the
# repo unclonable-in-practice: everywhere except one phone they are dangling. The
# links are still *useful* on-device, so we declare them and rebuild them here
# instead of storing them in git.
#
#   bash scripts/link_local.sh            # create/repair links (skips missing targets)
#   bash scripts/link_local.sh --check     # report only, exit 1 if anything is off
#   bash scripts/link_local.sh --force     # replace existing regular files too
#   TERMUX_HOME=/some/root bash scripts/link_local.sh
#
# Safe to re-run. Never deletes a target, only the link itself.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="${LINKS_MANIFEST:-$REPO_ROOT/scripts/links.manifest}"
HOME_ROOT="${TERMUX_HOME:-$HOME}"
PREFIX_ROOT="${PREFIX:-/data/data/com.termux/files/usr}"

CHECK_ONLY=0
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=1 ;;
    --force) FORCE=1 ;;
    -h | --help)
      sed -n '2,16p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *)
      printf 'unknown argument: %s\n' "$arg" >&2
      exit 2
      ;;
  esac
done

if [ ! -f "$MANIFEST" ]; then
  printf 'manifest not found: %s\n' "$MANIFEST" >&2
  exit 2
fi

created=0
ok=0
repaired=0
missing_target=0
blocked=0

expand_target() {
  case "$1" in
    '~/'*) printf '%s/%s' "$HOME_ROOT" "${1#\~/}" ;;
    '$PREFIX/'*) printf '%s/%s' "$PREFIX_ROOT" "${1#\$PREFIX/}" ;;
    *) printf '%s' "$1" ;;
  esac
}

while IFS=$'\t' read -r link target || [ -n "${link:-}" ]; do
  # Skip comments and blanks.
  case "${link:-}" in '' | \#*) continue ;; esac
  [ -n "${target:-}" ] || continue

  abs_link="$REPO_ROOT/$link"
  abs_target="$(expand_target "$target")"

  if [ ! -e "$abs_target" ]; then
    printf 'MISSING TARGET  %s -> %s\n' "$link" "$abs_target"
    missing_target=$((missing_target + 1))
    continue
  fi

  if [ -L "$abs_link" ]; then
    current="$(readlink "$abs_link")"
    if [ "$current" = "$abs_target" ]; then
      ok=$((ok + 1))
      continue
    fi
    if [ "$CHECK_ONLY" -eq 1 ]; then
      printf 'WRONG TARGET    %s -> %s (want %s)\n' "$link" "$current" "$abs_target"
      repaired=$((repaired + 1))
      continue
    fi
    rm -f "$abs_link"
    ln -s "$abs_target" "$abs_link"
    printf 'REPAIRED        %s -> %s\n' "$link" "$abs_target"
    repaired=$((repaired + 1))
    continue
  fi

  if [ -e "$abs_link" ]; then
    if [ "$FORCE" -eq 1 ] && [ "$CHECK_ONLY" -eq 0 ]; then
      rm -rf "$abs_link"
    else
      printf 'BLOCKED         %s exists and is not a symlink (use --force)\n' "$link"
      blocked=$((blocked + 1))
      continue
    fi
  fi

  if [ "$CHECK_ONLY" -eq 1 ]; then
    printf 'ABSENT          %s -> %s\n' "$link" "$abs_target"
    created=$((created + 1))
    continue
  fi

  mkdir -p "$(dirname "$abs_link")"
  ln -s "$abs_target" "$abs_link"
  printf 'LINKED          %s -> %s\n' "$link" "$abs_target"
  created=$((created + 1))
done <"$MANIFEST"

printf '\nhome=%s\n' "$HOME_ROOT"
printf 'ok=%d created=%d repaired=%d missing-target=%d blocked=%d\n' \
  "$ok" "$created" "$repaired" "$missing_target" "$blocked"

if [ "$CHECK_ONLY" -eq 1 ] && { [ "$created" -gt 0 ] || [ "$repaired" -gt 0 ] || [ "$blocked" -gt 0 ]; }; then
  exit 1
fi
if [ "$blocked" -gt 0 ]; then
  exit 1
fi
exit 0
