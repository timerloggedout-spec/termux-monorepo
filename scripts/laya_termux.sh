#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
# Termux is the operator/orchestration hub. Heavy Laya weights run remotely unless
# the local environment already provides a compatible PyTorch/Laya stack.
case "${1:-status}" in
  live) gh workflow run "Laya Live Runtime" --ref "${2:-master}" ;;
  cadence) gh workflow run "Laya CADENCE Sweep" --ref "${2:-master}" -f cohort="termux-$(date -u +%Y%m%dT%H%M%SZ)" ;;
  jev) gh workflow run "Jev Live Adapter" --ref "${2:-master}" ;;
  local-mock) python scripts/laya_sweep.py --output - ;;
  status) gh run list --workflow laya-live.yml --limit 5 ;;
  *) echo "usage: $0 {live|cadence|jev|local-mock|status} [ref]" >&2; exit 2 ;;
esac
