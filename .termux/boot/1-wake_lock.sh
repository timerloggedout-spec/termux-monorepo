#!/data/data/com.termux/files/usr/bin/sh
mkdir -p "$HOME/.deepcli/locks"
exec 9>"$HOME/.deepcli/locks/1-wake_lock.lock"
flock -n 9 || exit 0
    termux-wake-lock
