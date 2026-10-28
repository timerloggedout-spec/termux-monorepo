#!/usr/bin/env python3
"""Delphi cycle worker — a service, not a chat session (N5 brief §2).

Polls the `delphi-cycle` task queue on the fleet Temporal self-host
and executes DelphiCycleWorkflow + its stage activities. Run by the
temporal-delphi-worker systemd unit (mirror:
scripts/temporal/selfhost/temporal-delphi-worker.service, enrolled in
install.sh keepalive coverage).

Usage: worker.py [--address localhost:7233] [--task-queue delphi-cycle]
Requires: pip install temporalio (fleet: the delphi-ops venv).
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker

try:  # package import (repo layout)
    from .workflow import DelphiCycleWorkflow, TASK_QUEUE
    from . import activities
except ImportError:  # loose-module import (same directory on sys.path)
    from workflow import DelphiCycleWorkflow, TASK_QUEUE
    import activities


async def _main(address: str, task_queue: str) -> None:
    client = await Client.connect(address)
    worker = Worker(client, task_queue=task_queue,
                    workflows=[DelphiCycleWorkflow],
                    activities=activities.ACTIVITIES,
                    activity_executor=ThreadPoolExecutor(max_workers=8))
    print(f"delphi-cycle worker polling {task_queue} @ {address}",
          flush=True)
    await worker.run()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--address", default="localhost:7233")
    ap.add_argument("--task-queue", default=TASK_QUEUE)
    args = ap.parse_args(argv)
    asyncio.run(_main(args.address, args.task_queue))
    return 0


if __name__ == "__main__":
    sys.exit(main())
