#!/data/data/com.termux/files/usr/bin/sh
# Installed as ~/.termux/boot/20-b160v-persistent.sh — runs at device boot
# (Termux:Boot). Slot 20 fits the device's existing numbering
# (00-sshd · 10-tmx-secondary-services · 45-tailscale · 50-master-rescue ·
# 99-mem-guard). sshd is started by 00; this entry starts the owner's
# supervisor loop (~/bin/supervisor.sh), which keeps the tunnel loop
# alive, and kicks the tunnel loop directly as belt-and-braces.
termux-wake-lock
sleep 5
sh "$HOME/b160v-persistent/start.sh"
