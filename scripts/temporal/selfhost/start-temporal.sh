#!/bin/sh
# Fleet self-hosted Temporal (owner decision 2026-10-27: self-host, not Cloud).
# Binds localhost ONLY: advertising 0.0.0.0 stalls the dev server's cluster
# bootstrap in this network namespace (found 2026-10-28, firsthand).
# Non-loopback exposure goes through the relay unit (0.0.0.0:7234 -> 127.0.0.1:7233).
exec /home/hatch/workspace/delphi-ops/temporalbuild/bin/temporal server start-dev \
  --port 7233 --ui-port 8233 \
  --db-filename /home/hatch/workspace/temporal-selfhost/temporal.db \
  --namespace default --log-level warn
