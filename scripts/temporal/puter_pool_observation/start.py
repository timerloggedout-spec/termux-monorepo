#!/usr/bin/env python3
"""Start a durable Puter Pool observation workflow on the Temporal task queue."""
from __future__ import annotations

import argparse
import asyncio
import os
import uuid

from temporalio.client import Client

from .contracts import PuterPoolObservationInput
from .workflow import PuterPoolObservationWorkflow, TASK_QUEUE


async def start(args: argparse.Namespace) -> None:
    client = await Client.connect(args.address)
    request = PuterPoolObservationInput(
        task_or_entry_ref=args.task_or_entry_ref,
        doe_run_id=args.doe_run_id,
        workflow_run_id=args.workflow_run_id,
        run_attempt=args.run_attempt,
        interval_seconds=args.interval_seconds,
    )
    handle = await client.start_workflow(
        PuterPoolObservationWorkflow.run,
        request,
        id=args.workflow_id,
        task_queue=TASK_QUEUE,
    )
    print(f"workflow_id={handle.id} task_queue={TASK_QUEUE}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", default=os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"))
    parser.add_argument("--workflow-id", default=f"puter-pool-observability-{uuid.uuid4().hex[:12]}")
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--task-or-entry-ref", default="")
    parser.add_argument("--doe-run-id", default="")
    parser.add_argument("--workflow-run-id", default="")
    parser.add_argument("--run-attempt", type=int, default=1)
    args = parser.parse_args()
    if not 60 <= args.interval_seconds <= 3600 or args.run_attempt < 1:
        parser.error("interval must be 60..3600 seconds and run attempt must be positive")
    asyncio.run(start(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
