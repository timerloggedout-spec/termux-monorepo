#!/bin/sh
# Install/repair the fleet Temporal self-host units.
# /etc does not survive VM replacement; this script (kept on the durable
# workspace disk + mirrored in the repo at scripts/temporal/selfhost/)
# restores them. Idempotent.
set -e
D=/home/hatch/workspace/temporal-selfhost
cp "$D/temporal-selfhost.service" "$D/temporal-relay.service" \
   "$D/temporal-delphi-worker.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now temporal-selfhost temporal-relay temporal-delphi-worker
