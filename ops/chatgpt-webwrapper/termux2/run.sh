#!/bin/sh
# ChatGPT webWrapper — Termux device instance (v2) entrypoint.
#
# Telemetry first: run_started is appended to telemetry.jsonl BEFORE
# anything else — before the probe, before session establishment,
# before the harvest (owner ruling: immediate telemetry, never an
# after-step). The driver appends its own run_started on entry.
#
# No installs, no bootstrap: v2 is a session-layer driver on the
# python stdlib floor (the HTTP ladder opportunistically uses
# curl_cffi / requests when present). There is no browser binary.
cd "$(dirname "$0")" || exit 1

python3 -c "import telemetry; telemetry.emit('run_started', driver='run.sh', phase='entrypoint', surface='termux2')" 2>/dev/null || true

case "$1" in
  doctor)         exec python3 core.py --doctor ;;
  probe)          exec python3 core.py --probe ;;
  import-session) exec python3 core.py --import-session ;;
  flush)          exec python3 sink.py flush ;;
  *)              exec python3 driver.py "$@" ;;
esac
