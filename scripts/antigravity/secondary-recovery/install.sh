#!/data/data/com.termux/files/usr/bin/bash
# Invoke only over an externally verified pinned SSH connection.
set -euo pipefail
umask 077
src=$(cd -- "$(dirname -- "$0")" && pwd)
marker="$HOME/.local/share/agy-1497-secondary/worktree/.agy-secondary-id"
[[ -f "$marker" && ! -L "$marker" && "$(cat "$marker")" == tmx-node-55619bd5 ]] || exit 21
[[ "$(whoami)" == u0_a243 && "$(getprop ro.product.model)" == B160V ]] || exit 23
[[ "$PREFIX" == /data/data/com.termux/files/usr ]] || exit 24
for cmd in flock sv sv-enable pgrep termux-wake-lock zsh; do command -v "$cmd" >/dev/null || { echo "STOP: required command missing: $cmd" >&2; exit 30; }; done
[[ -f "$PREFIX/etc/profile.d/start-services.sh" ]] || exit 25
"$PREFIX/bin/sshd" -t
state="$HOME/.local/state/tmx-secondary-recovery"
for d in "$state" "$HOME/.local/bin" "$HOME/.termux" "$HOME/.termux/boot" "$PREFIX/var/service/tmx-secondary-sshd"; do
  [[ ! -L "$d" ]] || exit 26
  mkdir -p "$d"
done
exec 9>"$state/install.lock"
flock -n 9 || exit 27
# Do not compete with a separately enabled native sshd service.
[[ ! -d "$PREFIX/var/service/sshd" || -f "$PREFIX/var/service/sshd/down" ]] || { echo 'STOP: native sshd service enabled' >&2; exit 28; }
backup=$(mktemp -d "$state/install-before.XXXXXX")
rollback_notice() {
  status=$?
  if (( status != 0 )); then printf 'Private rollback snapshot (installation incomplete): %s\n' "$backup" >&2; fi
}
trap rollback_notice EXIT
put() {
  local source=$1 target=$2 label=$3
  [[ ! -L "$target" && ( ! -e "$target" || -f "$target" ) ]] || exit 29
  if [[ -f "$target" ]]; then
    cmp -s "$source" "$target" && return 0
    cp -p -- "$target" "$backup/$label"
  else
    printf '%s\n' "$target" >> "$backup/created-paths"
  fi
  local tmp
  tmp=$(mktemp "${target}.XXXXXX")
  cat "$source" > "$tmp"
  chmod 700 "$tmp"
  mv -- "$tmp" "$target"
}
service="$PREFIX/var/service/tmx-secondary-sshd"
# Keep a newly created service disabled until all files are ready.
if [[ ! -e "$service/run" ]]; then : > "$service/down"; fi
put "$src/sshd-run" "$service/run" sshd-run
mkdir -p "$service/log"
[[ ! -L "$service/log" ]] || exit 29
printf '#!%s/bin/sh\nsleep 5\n' "$PREFIX" > "$backup/finish.candidate"
put "$backup/finish.candidate" "$service/finish" finish
printf '#!%s/bin/sh\nexec %s/share/termux-services/svlogger\n' "$PREFIX" "$PREFIX" > "$backup/log-run.candidate"
put "$backup/log-run.candidate" "$service/log/run" log-run
mkdir -p "$PREFIX/var/log/sv/tmx-secondary-sshd"
# svlogd: current rotates near 64 KiB; retain at most two archived files.
printf 's65536\nn2\n' > "$backup/log-config.candidate"
put "$backup/log-config.candidate" "$PREFIX/var/log/sv/tmx-secondary-sshd/config" log-config
put "$src/tmx-reconnect" "$HOME/.local/bin/tmx-reconnect" tmx-reconnect
put "$src/10-tmx-secondary-services" "$HOME/.termux/boot/10-tmx-secondary-services" boot-hook
zshrc="$HOME/.zshrc"
[[ ! -L "$zshrc" && ( ! -e "$zshrc" || -f "$zshrc" ) ]] || exit 29
if ! grep -Fqx '# BEGIN tmx-secondary-reconnect' "$zshrc" 2>/dev/null; then
  if [[ -e "$zshrc" ]]; then
    cp -p "$zshrc" "$backup/zshrc"
    zsh -n "$zshrc"
  else
    printf '%s\n' "$zshrc" >> "$backup/created-paths"
  fi
  cat >> "$zshrc" <<'ALIAS'

# BEGIN tmx-secondary-reconnect
alias reconnect='"$HOME/.local/bin/tmx-reconnect"'
# END tmx-secondary-reconnect
ALIAS
fi
zsh -n "$zshrc"
# Do not leak an advisory installer lock into runsvdir descendants.
flock -u 9
exec 9>&-
"$HOME/.local/bin/tmx-reconnect"
trap - EXIT
printf 'Private rollback snapshot: %s\n' "$backup"
