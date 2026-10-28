#!/usr/bin/env python3
"""HITL approval workflow — V2 (cookbook-agent-loop) suite 1.

The ai-cookbook human-in-the-loop pattern reduced to its deciding
shape: a workflow that PAUSES awaiting a human approval signal,
resumes when the signal arrives, and completes with the decision on
record. Suite proof (`prove` mode): start the workflow, verify it is
still running (paused) after a beat, send the approval signal, and
assert completion carries the recorded decision.

Self-host dev server only. Requires: pip install temporalio.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import timedelta

try:
    from temporalio import workflow
    from temporalio.client import Client
    from temporalio.worker import Worker

    @workflow.defn
    class ApprovalWorkflow:
        def __init__(self) -> None:
            self._decision: dict | None = None

        @workflow.signal
        def approve(self, decision: dict) -> None:
            self._decision = decision

        @workflow.run
        async def run(self, request: dict) -> dict:
            await workflow.wait_condition(lambda: self._decision is not None,
                                          timeout=timedelta(minutes=10))
            return {"request": request, "decision": self._decision,
                    "outcome": "approved" if self._decision.get("approved") else "rejected"}

except ImportError:  # pragma: no cover
    workflow = None  # type: ignore


async def _prove(address: str) -> dict:
    client = await Client.connect(address)
    task_queue = "hitl-approval-suite"
    worker = Worker(client, task_queue=task_queue, workflows=[ApprovalWorkflow])
    async with worker:
        handle = await client.start_workflow(
            ApprovalWorkflow.run, {"unit": "evidence-fetch", "prs": [1867, 1885]},
            id=f"hitl-{id(object())}", task_queue=task_queue)
        await asyncio.sleep(1.5)
        desc = await handle.describe()
        paused = desc.status.name == "RUNNING"
        await handle.signal(ApprovalWorkflow.approve,
                            {"approved": True, "by": "role{operator}", "note": "suite proof"})
        result = await asyncio.wait_for(handle.result(), timeout=60)
    ok = paused and result["outcome"] == "approved" and result["decision"]["approved"] is True
    return {"verdict": "PASS" if ok else "FAIL", "was_paused_before_signal": paused,
            "result": result}


def main(argv: list[str] | None = None) -> int:
    if workflow is None:
        print("temporalio not installed: pip install temporalio", file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["prove"])
    ap.add_argument("--address", default="localhost:7233")
    args = ap.parse_args(argv)
    out = asyncio.run(_prove(args.address))
    print(json.dumps(out, indent=1))
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
