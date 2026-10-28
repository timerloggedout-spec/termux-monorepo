#!/bin/sh
# Delphi cycle worker (N5): polls the delphi-cycle task queue on the
# fleet Temporal self-host. Code = the repo sparse checkout on the
# durable workspace disk (~/workspace/temporal-selfhost/repo, kept at
# master); runtime = the delphi-ops venv (temporalio SDK, env install).
exec /home/hatch/workspace/delphi-ops/temporalbuild/venv/bin/python \
  /home/hatch/workspace/temporal-selfhost/repo/scripts/temporal/delphi_cycle/worker.py \
  --address localhost:7233
