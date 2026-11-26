#!/data/data/com.termux/files/usr/bin/sh
# ChatGPT webWrapper — TERMUX device instance, single entrypoint.
#
#   ./run.sh
#
# Flow: IMMEDIATE TELEMETRY first (below) -> bootstrap if needed -> probe
# the persistent profile -> if no session, HEADED Chromium opens on the
# phone screen and the OWNER performs the sign-in (the participant step;
# this code never enters credentials; verification rides the on-device
# app/Google prompt only — no emailed-code step exists anywhere in this
# flow) -> once a session exists, the harvest driver runs (census-order
# capture, checkpointed, stop-on-friction).
set -eu
cd "$(dirname "$0")"

# IMMEDIATE TELEMETRY (owner ruling 2026-11-26): the entrypoint emits
# run_started into telemetry.jsonl BEFORE anything else — before
# bootstrap, before probe, before session establishment. Telemetry is
# never a post-hoc summary and there is no deferred mode; every later
# phase appends its own events (session_event / friction_event /
# conversation_captured / run_finished) in the same shapes.
if command -v python3 >/dev/null 2>&1; then
    python3 -c "import telemetry; telemetry.emit('run_started', driver='run.sh', phase='entrypoint')" || true
fi

if [ ! -f .bootstrapped ]; then
    ./bootstrap.sh
fi

probe_out="$(python3 core_se.py --probe || true)"
echo "probe: $probe_out"
case "$probe_out" in
    *'"state": "ok"'*)
        echo "session: live — starting harvest"
        ;;
    *)
        echo "session: none — opening headed Chromium for owner sign-in"
        if ! python3 core_se.py --establish; then
            python3 -c "import telemetry; telemetry.emit('run_finished', status='establish_failed')" || true
            exit 3
        fi
        echo "session: established — starting harvest"
        ;;
esac

exec python3 driver_se.py
