#!/data/data/com.termux/files/usr/bin/bash
# Install the destructive-git guard on a Termux node (replica of the origin's guard:
# `git reset --hard` -> BLOCKED). Additive: installs into ~/.local/bin, ~/.config/tmx-git-guard
# and $PREFIX/etc/profile.d; never edits the repository.
#
# Layers:
#   1. PATH wrapper  ~/.local/bin/git      blocks destructive subcommands before git runs
#   2. global hook   core.hooksPath pre-push  blocks branch deletion and non-fast-forward pushes
#                    (also covers tools that call $PREFIX/bin/git directly), chains repo hooks
#   3. audit log     ~/.local/state/tmx-git-guard/blocked.log (+ termux-notification)
#
# Escape hatch: only an interactive TTY may bypass, by typing the confirmation phrase.
# Agents and scheduled jobs (no TTY) can never bypass.
set -euo pipefail
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
REAL_GIT="$PREFIX/bin/git"
BIN_DIR="$HOME/.local/bin"
GUARD_DIR="$HOME/.config/tmx-git-guard"
HOOKS_DIR="$GUARD_DIR/hooks"
[ -x "$REAL_GIT" ] || { echo "git not found at $REAL_GIT (pkg install git)" >&2; exit 1; }
mkdir -p "$BIN_DIR" "$HOOKS_DIR" "$HOME/.local/state/tmx-git-guard"

cat >"$BIN_DIR/git" <<EOF
#!$PREFIX/bin/bash
# tmx-git-guard wrapper (installed by scripts/termux/devices/install-git-guard.sh)
REAL_GIT="$REAL_GIT"
EOF
cat >>"$BIN_DIR/git" <<'EOF'
LOG="$HOME/.local/state/tmx-git-guard/blocked.log"
PHRASE="I accept permanent data loss"

block() {
  local why="$1"; shift
  printf '%s\tBLOCKED\t%s\tcwd=%s\tgit %s\n' "$(date -u +%FT%TZ)" "$why" "$PWD" "$*" >>"$LOG" 2>/dev/null || true
  echo "BLOCKED by tmx-git-guard: $why" >&2
  echo "  git $*" >&2
  echo "  This repo is the origin device's full backup: additive changes only." >&2
  if [ -t 0 ] && [ -t 2 ]; then
    printf 'Type "%s" to run it anyway: ' "$PHRASE" >&2
    local ans; IFS= read -r ans
    if [ "$ans" = "$PHRASE" ]; then
      printf '%s\tBYPASS\t%s\tgit %s\n' "$(date -u +%FT%TZ)" "$why" "$*" >>"$LOG" 2>/dev/null || true
      exec "$REAL_GIT" "$@"
    fi
  fi
  command -v termux-notification >/dev/null 2>&1 && \
    termux-notification --id 43113 --title "git guard: BLOCKED" --content "$why — git $*" --priority high >/dev/null 2>&1 &
  exit 97
}

# Find the subcommand, skipping global options.
args=("$@"); i=0; n=${#args[@]}
while [ $i -lt $n ]; do
  case "${args[$i]}" in
    -C|-c|--git-dir|--work-tree|--namespace|--exec-path|--config-env) i=$((i+2)) ;;
    -*) i=$((i+1)) ;;
    *) break ;;
  esac
done
sub="${args[$i]:-}"; rest=("${args[@]:$((i+1))}")

has() { local a; for a in "${rest[@]}"; do for p in "$@"; do [ "$a" = "$p" ] && return 0; done; done; return 1; }
has_short() { local a; for a in "${rest[@]}"; do case "$a" in --*) ;; -*"$1"*) return 0 ;; esac; done; return 1; }
has_prefix() { local a; for a in "${rest[@]}"; do case "$a" in "$1"*) return 0 ;; esac; done; return 1; }

case "$sub" in
  reset)   has --hard --merge --keep && block "reset discards work" "$@" ;;
  clean)   { has --force || has_short f; } && block "clean deletes untracked files" "$@" ;;
  push)
    { has --force --force-with-lease --force-if-includes --delete --mirror --prune || has_short f || has_short d \
      || has_prefix --force-with-lease= || has_prefix ':' || has_prefix '+'; } && block "force/delete push" "$@" ;;
  branch)  { has --delete -D -M --force || has_short d || has_short D || has_short M || has_short f; } && block "branch delete/move" "$@" ;;
  tag)     { has --delete || has_short d; } && block "tag delete" "$@" ;;
  checkout) { has --force -f || has . || has --; } && block "checkout overwrites working tree" "$@" ;;
  switch)  has --discard-changes --force -f -C --force-create && block "switch discards/resets" "$@" ;;
  restore) { has --staged && ! has --worktree -W; } || block "restore overwrites working tree" "$@" ;;
  rm)      has --cached || block "rm deletes tracked files" "$@" ;;
  mv)      block "mv reorganizes tracked files" "$@" ;;
  stash)   has clear drop && block "stash clear/drop" "$@" ;;
  filter-branch|filter-repo|replace) block "history rewrite" "$@" ;;
  gc)      { has --prune=now || has_prefix --prune=now; } && block "gc prune=now" "$@" ;;
  reflog)  has expire delete && block "reflog expire/delete" "$@" ;;
  update-ref) has -d --stdin && block "update-ref delete" "$@" ;;
  worktree) has remove prune && has --force -f && block "worktree force removal" "$@" ;;
esac
exec "$REAL_GIT" "$@"
EOF
chmod 755 "$BIN_DIR/git"

cat >"$HOOKS_DIR/pre-push" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# tmx-git-guard pre-push: no ref deletion, no non-fast-forward.
ZERO=0000000000000000000000000000000000000000
LOG="$HOME/.local/state/tmx-git-guard/blocked.log"
input="$(cat)"
while read -r lref lsha rref rsha; do
  [ -n "$lref" ] || continue
  if [ "$lsha" = "$ZERO" ]; then
    echo "BLOCKED by tmx-git-guard: deleting remote ref $rref" >&2
    printf '%s\tBLOCKED\tpre-push delete %s\n' "$(date -u +%FT%TZ)" "$rref" >>"$LOG"; exit 1
  fi
  if [ "$rsha" != "$ZERO" ]; then
    if ! git cat-file -e "$rsha^{commit}" 2>/dev/null; then
      echo "BLOCKED by tmx-git-guard: remote $rref has commits you have not fetched (git fetch first)" >&2; exit 1
    fi
    if ! git merge-base --is-ancestor "$rsha" "$lsha"; then
      echo "BLOCKED by tmx-git-guard: non-fast-forward push to $rref" >&2
      printf '%s\tBLOCKED\tpre-push non-ff %s\n' "$(date -u +%FT%TZ)" "$rref" >>"$LOG"; exit 1
    fi
  fi
done <<<"$input"
# Chain to the repository's own hook, if any.
repo_hook="$(git rev-parse --git-path hooks/pre-push 2>/dev/null)"
if [ -n "$repo_hook" ] && [ -x "$repo_hook" ] && [ "$repo_hook" != "$0" ]; then
  printf '%s\n' "$input" | "$repo_hook" "$@"
fi
EOF
chmod 755 "$HOOKS_DIR/pre-push"
"$REAL_GIT" config --global core.hooksPath "$HOOKS_DIR"

# PATH: login shells (profile.d) and interactive bash (~/.bashrc), idempotent.
cat >"$PREFIX/etc/profile.d/tmx-git-guard.sh" <<'EOF'
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) PATH="$HOME/.local/bin:$PATH"; export PATH ;; esac
EOF
touch "$HOME/.bashrc"
grep -q 'tmx-git-guard' "$HOME/.bashrc" || \
  printf '\n# tmx-git-guard\n. %s/etc/profile.d/tmx-git-guard.sh\n' "$PREFIX" >>"$HOME/.bashrc"

echo "tmx-git-guard installed. Open a new shell, then test:"
echo "  git -C \"\$HOME/termux-monorepo\" reset --hard   # expect: BLOCKED (exit 97)"
