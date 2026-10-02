#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sleep 60
while true; do
  ~/.local/bin/hs-codespace-cron
  sleep 900
done
