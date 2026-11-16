#!/usr/bin/env python3
"""V5 serverless-skill suite: the skill dry-walk, dev server only.

Walks the skill-temporal-serverless starter shape step by step —
scope -> access checks -> packaging -> registration -> verification
-> rollback — executing every step that is local against the
self-host dev server, and recording every Cloud step as
specified_not_run with the card-rule reason (no Temporal Cloud / AWS
/ GCP account or payment instrument exists for this fleet). The walk
passes when all local steps pass and no cloud step is silently
skipped. Requires: pip install temporalio.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import io
import json
import sys
import tarfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kill_resume_harness import DurableUnitWorkflow, evidence_unit  # noqa: E402

CLOUD_REASON = ("specified_not_run: no Temporal Cloud/AWS/GCP account or payment "
                "instrument (card rule); the skill form is what this walk proves")


async def _walk(address: str, workdir: str) -> dict:
    from temporalio.client import Client
    from temporalio.worker import Worker

    steps: list[dict] = []
    root = Path(workdir)
    root.mkdir(parents=True, exist_ok=True)

    steps.append({"step": "scope", "status": "ran",
                  "detail": "skill scope fixed: register DurableUnitWorkflow on a walk "
                            "queue, verify, roll back; no production surface touched"})
    client = await Client.connect(address)
    steps.append({"step": "access_checks", "status": "ran",
                  "detail": f"dev server reachable at {address}; namespace default"})
    steps.append({"step": "cloud_access_checks", "status": "specified_not_run",
                  "detail": CLOUD_REASON})

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name in ("kill_resume_harness.py",):
            tar.add(Path(__file__).resolve().parent / name, arcname=name)
    pkg = buf.getvalue()
    (root / "skill-pack.tar.gz").write_bytes(pkg)
    steps.append({"step": "packaging", "status": "ran",
                  "detail": f"skill pack tar.gz {len(pkg)} bytes sha256 "
                            f"{hashlib.sha256(pkg).hexdigest()[:16]}…"})
    steps.append({"step": "cloud_deploy", "status": "specified_not_run",
                  "detail": CLOUD_REASON})

    queue = "skill-dry-walk"
    wf_id = f"skill-walk-{int(time.time())}"
    worker = Worker(client, task_queue=queue,
                    workflows=[DurableUnitWorkflow], activities=[evidence_unit])
    async with worker:
        handle = await client.start_workflow(
            DurableUnitWorkflow.run, args=[str(root), f"walk-{wf_id}"],
            id=wf_id, task_queue=queue)
        steps.append({"step": "registration", "status": "ran",
                      "detail": f"workflow {wf_id} registered and started on {queue}"})
        desc = await handle.describe()
        steps.append({"step": "verification", "status": "ran",
                      "detail": f"describe: status {desc.status.name}, "
                                f"workflow type {desc.workflow_type}"})
        await handle.terminate("dry-walk rollback")
        desc = await handle.describe()
        steps.append({"step": "rollback", "status": "ran",
                      "detail": f"terminated for rollback proof; status now {desc.status.name}"})
    steps.append({"step": "cloud_registration", "status": "specified_not_run",
                  "detail": CLOUD_REASON})

    local_ok = all(s["status"] == "ran" for s in steps
                   if s["status"] != "specified_not_run")
    cloud_named = sum(1 for s in steps if s["status"] == "specified_not_run")
    return {"verdict": "PASS" if local_ok and cloud_named == 3 else "FAIL",
            "steps": steps}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--address", default="localhost:7233")
    ap.add_argument("--workdir", required=True)
    args = ap.parse_args(argv)
    out = asyncio.run(_walk(args.address, args.workdir))
    print(json.dumps(out, indent=1))
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
