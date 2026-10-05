#!/data/data/com.termux/files/usr/bin/sh
mkdir -p "$HOME/.deepcli/locks"
exec 9>"$HOME/.deepcli/locks/95-hs-stack.lock"
flock -n 9 || exit 0
termux-wake-lock
sleep 120
while true; do
  ~/.local/bin/hs-stack-watchdog
  sleep 300
done
