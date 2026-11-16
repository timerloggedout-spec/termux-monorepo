#!/usr/bin/env python3
"""Delphi cycle worker — cycle-scoped, never a daemon (N5, as amended
2026-10-28: VM = sandbox only; the Temporal self-host server is the
sole standing exception).

Polls the `delphi-cycle` task queue on the fleet Temporal self-host
and executes DelphiCycleWorkflow + its stage activities, for the
duration of one engagement:

  worker.py --exit-on-complete delphi-cycle/<pass-id>

polls only while that cycle runs and exits when it completes. Without
--exit-on-complete it runs in the foreground until interrupted —
still an operator-launched bounded process, not a service: there is
no systemd unit for it (the unit from the first N5 landing was
removed by PR #2177 under the sandbox order).

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


async def _main(address: str, task_queue: str,
                exit_on_complete: str | None) -> None:
    client = await Client.connect(address)
    worker = Worker(client, task_queue=task_queue,
                    workflows=[DelphiCycleWorkflow],
                    activities=activities.ACTIVITIES,
                    activity_executor=ThreadPoolExecutor(max_workers=8))
    print(f"delphi-cycle worker polling {task_queue} @ {address}",
          flush=True)
    if not exit_on_complete:
        await worker.run()
        return
    # Cycle-scoped: poll only while the named cycle runs, then exit.
    handle = client.get_workflow_handle(exit_on_complete)
    async with worker:
        await handle.result()
    print(f"cycle {exit_on_complete} complete — worker exiting",
          flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--address", default="localhost:7233")
    ap.add_argument("--task-queue", default=TASK_QUEUE)
    ap.add_argument("--exit-on-complete", metavar="WORKFLOW_ID",
                    help="poll only while this workflow runs; exit "
                         "when it completes (cycle-scoped worker)")
    args = ap.parse_args(argv)
    asyncio.run(_main(args.address, args.task_queue,
                      args.exit_on_complete))
    return 0


if __name__ == "__main__":
    sys.exit(main())
