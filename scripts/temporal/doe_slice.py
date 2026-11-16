#!/usr/bin/env python3
"""TD-004 DoE slice: 2^4 factorial over the durable-execution design.

Factors (RFP §3): substrate {local-dev, cloud-managed} x attestation
{witness-envelope, none} x placement {remote, device} x routing
{moneyball, static}. Runnable cells in this environment are exactly
substrate=local-dev + placement=remote (4 arms x 2 repetitions, real
workflow/run IDs as trace identity). Every other cell publishes a
canonical row with status specified_not_run and its reason (cloud:
card rule / no account; device: remote-first, no server on-device) —
the factorial is complete, the unrun cells are named, not dropped.

Fixed at run time and stamped on the output: contract hash (the
evidence-envelope schema), env fingerprint, benchmark version, and
the deterministic scorer (score depends only on outcome fields —
completed, exactly one receipt, zero unknown outcomes — never on
wall-clock). Requires: pip install temporalio + a dev server.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import itertools
import json
import platform
import sys
import time
from datetime import timedelta
from pathlib import Path

BENCHMARK_VERSION = "doe-slice/v1"
COHORT = "temporal-doe-g4"
TASK = "evidence-unit"
QUEUES = ("doe-q-a", "doe-q-b")
MONEYBALL_WEIGHTS = {"doe-q-a": 0.62, "doe-q-b": 0.38}  # fixed for the slice

try:
    from temporalio import activity, workflow
    from temporalio.client import Client
    from temporalio.worker import Worker

    @activity.defn
    async def doe_unit(workdir: str, unit_id: str) -> dict:
        root = Path(workdir)
        (root / "receipts").mkdir(parents=True, exist_ok=True)
        receipt_path = root / "receipts" / f"{unit_id}.json"
        if receipt_path.exists():
            return json.loads(receipt_path.read_text())
        await asyncio.sleep(0.3)
        receipt = {"unit_id": unit_id, "records": 4}
        receipt_path.write_text(json.dumps(receipt))
        return receipt

    @workflow.defn
    class DoeUnitWorkflow:
        @workflow.run
        async def run(self, workdir: str, unit_id: str, attestation: str) -> dict:
            receipt = await workflow.execute_activity(
                doe_unit, args=[workdir, unit_id],
                schedule_to_close_timeout=timedelta(minutes=2))
            return {"unit_id": unit_id, "receipt": receipt,
                    "attestation": attestation, "unknown_outcomes": []}

except ImportError:  # pragma: no cover
    workflow = None  # type: ignore


def _score(status: str, result: dict | None) -> float:
    if status != "completed" or not result:
        return 0.0
    ok = (result["receipt"]["unit_id"] == result["unit_id"]
          and result["unknown_outcomes"] == [])
    return 1.0 if ok else 0.0


async def _run(address: str, workdir: str) -> dict:
    client = await Client.connect(address)
    workers = [Worker(client, task_queue=q, workflows=[DoeUnitWorkflow],
                      activities=[doe_unit]) for q in QUEUES]
    rows = []
    stamp = int(time.time())
    async with workers[0], workers[1]:
        for substrate, attest, placement, routing in itertools.product(
                ("local-dev", "cloud-managed"), ("witness-envelope", "none"),
                ("remote", "device"), ("moneyball", "static")):
            arm = f"{substrate}|{attest}|{placement}|{routing}"
            runnable = substrate == "local-dev" and placement == "remote"
            if not runnable:
                reason = ("card rule: no cloud account" if substrate == "cloud-managed"
                          else "remote-first: no Temporal server on-device")
                rows.append({"cohort": COHORT, "task": TASK, "arm": arm,
                             "repetition": None, "workflow_id": None, "run_id": None,
                             "status": "specified_not_run", "reason": reason,
                             "score": None})
                continue
            queue = (max(MONEYBALL_WEIGHTS, key=MONEYBALL_WEIGHTS.get)
                     if routing == "moneyball" else QUEUES[0])
            for rep in (1, 2):
                unit_id = f"doe-{stamp}-{len(rows)}-{rep}"
                wf_id = f"doe-{unit_id}"
                handle = await client.start_workflow(
                    DoeUnitWorkflow.run, args=[workdir, unit_id, attest],
                    id=wf_id, task_queue=queue)
                result = await asyncio.wait_for(handle.result(), timeout=120)
                desc = await handle.describe()
                receipt_files = list((Path(workdir) / "receipts").glob(f"{unit_id}.json"))
                status = "completed" if len(receipt_files) == 1 else "receipt_mismatch"
                rows.append({"cohort": COHORT, "task": TASK, "arm": arm,
                             "repetition": rep, "workflow_id": wf_id,
                             "run_id": desc.run_id, "status": status,
                             "score": _score(status, result),
                             "attestation_digest": (
                                 hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
                                 if attest == "witness-envelope" else None)})
    return {"schema": "doe-canonical-rows/v1", "benchmark_version": BENCHMARK_VERSION,
            "rows": rows}


def main(argv: list[str] | None = None) -> int:
    if workflow is None:
        print("temporalio not installed: pip install temporalio", file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--address", default="localhost:7233")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--schema", required=True, help="evidence-envelope schema path (contract hash)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = asyncio.run(_run(args.address, args.workdir))
    out["contract_hash"] = hashlib.sha256(Path(args.schema).read_bytes()).hexdigest()
    import temporalio
    out["env_fingerprint"] = {"python": platform.python_version(),
                              "temporalio_sdk": getattr(temporalio, "__version__", "unknown"),
                              "platform": platform.platform()}
    out["scorer"] = "deterministic outcome-fields only (completed, receipt==1, unknown==0)"
    Path(args.out).write_text(json.dumps(out, indent=1))
    ran = [r for r in out["rows"] if r["status"] == "completed"]
    print(json.dumps({"rows": len(out["rows"]), "completed": len(ran),
                      "specified_not_run": len(out["rows"]) - len(ran),
                      "mean_score_ran": (sum(r["score"] for r in ran) / len(ran)) if ran else None}))
    return 0 if len(ran) == 8 else 1


if __name__ == "__main__":
    sys.exit(main())
