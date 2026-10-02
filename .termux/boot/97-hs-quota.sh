#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sleep 45
# Loop: probe every 30 min
while true; do
  ~/.local/bin/hs-quota-watch --once >> ~/.deepcli/logs/hs-parity.jsonl 2>&1
  sleep 1800
done
