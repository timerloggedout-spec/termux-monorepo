#!/bin/sh
# Install/repair the fleet Temporal self-host units.
# /etc does not survive VM replacement; this script (kept on the durable
# workspace disk + mirrored in the repo at scripts/temporal/selfhost/)
# restores them. Idempotent.
# Scope (owner order 2026-10-28, VM = sandbox only): ONLY the Temporal
# self-host exception units (owner 2026-10-27) are installed here. The
# Delphi cycle worker is NOT a VM service — it runs bounded, per
# engagement (client.py prove / worker.py foreground), and its
# repeatable proof runs in GitHub Actions
# (.github/workflows/delphi-cycle.yml).
set -e
D=/home/hatch/workspace/temporal-selfhost
cp "$D/temporal-selfhost.service" "$D/temporal-relay.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now temporal-selfhost temporal-relay
