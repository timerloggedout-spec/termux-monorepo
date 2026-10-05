#!/data/data/com.termux/files/usr/bin/sh
mkdir -p "$HOME/.deepcli/locks"
exec 9>"$HOME/.deepcli/locks/99-hs-codespace-cron.lock"
flock -n 9 || exit 0
termux-wake-lock
sleep 60
while true; do
  ~/.local/bin/hs-codespace-cron
  sleep 900
done
