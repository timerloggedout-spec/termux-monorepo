#!/usr/bin/env python3
"""Run the Puter Pool observation worker against the configured Temporal server."""
from __future__ import annotations

import argparse
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import collect_puter_pool_observation
from .workflow import PuterPoolObservationWorkflow, TASK_QUEUE


async def run(address: str, task_queue: str) -> None:
    client = await Client.connect(address)
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[PuterPoolObservationWorkflow],
        activities=[collect_puter_pool_observation],
        activity_executor=ThreadPoolExecutor(max_workers=2),
    )
    await worker.run()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", default=os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"))
    parser.add_argument("--task-queue", default=TASK_QUEUE)
    args = parser.parse_args()
    asyncio.run(run(args.address, args.task_queue))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
