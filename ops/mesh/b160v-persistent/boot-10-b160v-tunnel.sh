#!/data/data/com.termux/files/usr/bin/sh
# Installed as ~/.termux/boot/10-b160v-tunnel.sh — runs at device boot
# (Termux:Boot). 00-sshd.sh starts sshd; this starts the tunnel loop.
sh "$HOME/b160v-persistent/start.sh"
