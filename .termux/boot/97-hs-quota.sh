#!/data/data/com.termux/files/usr/bin/sh
mkdir -p "$HOME/.deepcli/locks"
exec 9>"$HOME/.deepcli/locks/97-hs-quota.lock"
flock -n 9 || exit 0
termux-wake-lock
sleep 45
# Loop: probe every 30 min
while true; do
  ~/.local/bin/hs-quota-watch --once >> ~/.deepcli/logs/hs-parity.jsonl 2>&1
  sleep 1800
done
