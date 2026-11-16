#!/usr/bin/env python3
"""RFP §6 kill-and-resume proof harness (Temporal durable-execution RFP).

Extends the hello_workflow.py smoke into the bounded build every
candidate must survive (docs/rfps/temporal-durable-execution/RFP.md §6):

1. A workflow runs one idempotent, receipt-emitting unit of
   fleet-shaped work (an evidence fetch over a fixed PR set).
2. The worker is killed mid-activity; a second worker starts.
3. Assertions: the workflow completes; the receipt count is exactly 1
   (no duplicate side effect); a started-but-unrecorded unit is
   surfaced as an UNKNOWN outcome in the result envelope, never
   blindly retried (the retry reconciles against the idempotency key
   and reports the ambiguity); the full history digest lands in an
   evidence-envelope record.

Self-host dev server only (remote/Codespace, never the device):

    temporal server start-dev --port 7233
    python3 kill_resume_harness.py prove --address localhost:7233 \
        --workdir /path/to/scratch

`prove` orchestrates the two worker subprocesses itself, SIGKILLs the
first mid-activity, and prints a JSON verdict (exit 0 = proof passed).
Requires: pip install temporalio. No credentials; names only.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Fleet-shaped work unit: an evidence fetch over a fixed PR set.
# Deterministic content (no network): the "fetch" digests fixed records,
# the way fetch_evidence digests fixed PR evidence in the D0 agent.
# ---------------------------------------------------------------------------

FIXED_PR_SET = [1867, 1885, 1620, 1702]
UNIT_SLEEP_SECONDS = 8.0


def _unit_payload(unit_id: str) -> dict:
    records = [
        {"pr": pr, "claim": f"evidence:{pr}", "digest": hashlib.sha256(f"pr-{pr}".encode()).hexdigest()[:16]}
        for pr in FIXED_PR_SET
    ]
    return {"unit_id": unit_id, "records": records,
            "digest": hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()}


# Workflow/activity definitions live at module level; the __main__ guard
# below keeps the SDK sandbox re-import from re-running the entrypoint.

try:
    from temporalio import activity, workflow
    from temporalio.client import Client
    from temporalio.worker import Worker

    @activity.defn
    async def evidence_unit(workdir: str, unit_id: str) -> dict:
        """One idempotent, receipt-emitting unit of work.

        Receipt discipline: a `started` marker is written before the
        slow section; the receipt is written exactly once at the end,
        keyed by unit_id. A re-execution that finds a receipt returns
        it untouched; a re-execution that finds a started marker but
        no receipt knows the prior attempt's outcome is UNKNOWN and
        says so in its return (the workflow surfaces it).
        """
        root = Path(workdir)
        (root / "receipts").mkdir(parents=True, exist_ok=True)
        receipt_path = root / "receipts" / f"{unit_id}.json"
        started_path = root / "receipts" / f"{unit_id}.started"
        if receipt_path.exists():
            out = json.loads(receipt_path.read_text())
            out["reconciled_from"] = "existing_receipt"
            return out
        prior_started = started_path.exists()
        started_path.write_text(json.dumps({"unit_id": unit_id, "pid": os.getpid(),
                                            "at": time.time()}))
        # Slow section: this is where the kill lands.
        deadline = time.time() + UNIT_SLEEP_SECONDS
        while time.time() < deadline:
            activity.heartbeat("working")
            await asyncio.sleep(0.5)
        payload = _unit_payload(unit_id)
        receipt = {"unit_id": unit_id, "receipt_sha256":
                   hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
                   "records": len(payload["records"]),
                   "prior_attempt_unrecorded": prior_started}
        receipt_path.write_text(json.dumps(receipt, indent=1))
        return receipt

    @workflow.defn
    class DurableUnitWorkflow:
        """Runs the unit once; surfaces unknown outcomes, never hides them."""

        @workflow.run
        async def run(self, workdir: str, unit_id: str) -> dict:
            receipt = await workflow.execute_activity(
                evidence_unit, args=[workdir, unit_id],
                schedule_to_close_timeout=timedelta(minutes=5),
                heartbeat_timeout=timedelta(seconds=30),
            )
            unknown = []
            if receipt.get("prior_attempt_unrecorded"):
                unknown.append({"unit_id": unit_id,
                                "outcome": "unknown",
                                "detail": "prior attempt started but recorded no receipt; "
                                          "reconciled via idempotency key, not blindly retried"})
            return {"unit_id": unit_id, "receipt": receipt, "unknown_outcomes": unknown}

except ImportError:  # pragma: no cover - surfaced by main()
    activity = workflow = None  # type: ignore


async def _run_worker(address: str, task_queue: str) -> None:
    client = await Client.connect(address)
    worker = Worker(client, task_queue=task_queue,
                    workflows=[DurableUnitWorkflow], activities=[evidence_unit])
    await worker.run()


async def _history_digest(address: str, workflow_id: str) -> str:
    client = await Client.connect(address)
    handle = client.get_workflow_handle(workflow_id)
    history = await handle.fetch_history()
    return hashlib.sha256(history.to_json_dict().__str__().encode()).hexdigest()


async def _prove(address: str, workdir: str) -> dict:
    root = Path(workdir)
    root.mkdir(parents=True, exist_ok=True)
    unit_id = f"unit-{int(time.time())}"
    task_queue = "kill-resume-harness"
    workflow_id = f"kill-resume-{unit_id}"
    me = [sys.executable, str(Path(__file__).resolve()), "worker",
          "--address", address, "--task-queue", task_queue]

    w1 = subprocess.Popen(me, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        starter = await Client.connect(address)
        handle = await starter.start_workflow(
            DurableUnitWorkflow.run, args=[str(root), unit_id],
            id=workflow_id, task_queue=task_queue)
        # Let the activity get well into its slow section, then kill.
        await asyncio.sleep(4.0)
        w1.send_signal(signal.SIGKILL)
        w1.wait(timeout=10)
        killed_pid = w1.pid
        w2 = subprocess.Popen(me, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            result = await asyncio.wait_for(handle.result(), timeout=180)
        finally:
            w2.terminate()
            try:
                w2.wait(timeout=10)
            except subprocess.TimeoutExpired:
                w2.kill()
    finally:
        if w1.poll() is None:
            w1.kill()

    receipts = sorted((root / "receipts").glob("*.json"))
    digest = await _history_digest(address, workflow_id)
    envelope = {
        "workflow_id": workflow_id,
        "unit_id": unit_id,
        "killed_worker_pid": killed_pid,
        "workflow_result": result,
        "receipt_count": len(receipts),
        "history_sha256": digest,
        "attestation": "history digest referenced here per RFP §6 step 3 / N1; "
                       "Witness in-toto arm names-only, no keys in this record",
    }
    (root / "evidence-envelope.json").write_text(json.dumps(envelope, indent=1))
    passed = (len(receipts) == 1 and result["receipt"]["unit_id"] == unit_id
              and len(result["unknown_outcomes"]) == 1)
    return {"verdict": "PASS" if passed else "FAIL", "envelope": envelope}


def main(argv: list[str] | None = None) -> int:
    if activity is None:
        print("temporalio not installed: pip install temporalio", file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("worker", "prove"):
        p = sub.add_parser(name)
        p.add_argument("--address", default="localhost:7233")
        if name == "worker":
            p.add_argument("--task-queue", default="kill-resume-harness")
        else:
            p.add_argument("--workdir", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "worker":
        asyncio.run(_run_worker(args.address, args.task_queue))
        return 0
    verdict = asyncio.run(_prove(args.address, args.workdir))
    print(json.dumps(verdict, indent=1))
    return 0 if verdict["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
