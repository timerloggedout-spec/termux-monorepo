#!/data/data/com.termux/files/usr/bin/sh
# Termux:Boot (secondary node). Key-only sshd on 8022 for LAN/ADB-forward recovery.
# No public port forwarding (see docs/ops/termux-b160v-hub-runbook.md).
pgrep -x sshd >/dev/null 2>&1 || sshd
