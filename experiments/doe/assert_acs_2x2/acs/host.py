"""Run the mock email tool through the native ACS host SDK."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from agent_control_specification import AgentControl, AgentControlBlocked

from policy import EmailPolicy

ROOT = Path(__file__).resolve().parent


async def send_email(args: dict[str, Any]) -> dict[str, Any]:
    """Mock side effect; the fixture returns data in process."""
    return {"sent": True, "to": args["to"], "body": args["body"]}


async def execute_case(control: AgentControl, policy: EmailPolicy, task: dict[str, Any]) -> dict[str, Any]:
    policy.current_task_id = task["task_id"]
    try:
        result = await control.run_tool(
            "send_email",
            {"to": task["to"], "body": task["body"]},
            send_email,
            tool_call_id=task["task_id"],
        )
        return {"task_id": task["task_id"], "executed": True, "result": result.value}
    except AgentControlBlocked as exc:
        return {
            "task_id": task["task_id"],
            "executed": False,
            "decision": "deny",
            "reason": exc.result.verdict.reason,
        }


async def run(input_path: Path, manifest_path: Path, audit_path: Path) -> list[dict]:
    policy = EmailPolicy(str(audit_path))
    control = AgentControl.from_path(str(manifest_path), policy_dispatcher=policy)
    tasks = [
        json.loads(line)
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [await execute_case(control, policy, task) for task in tasks]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSONL task rows")
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifest.yaml")
    parser.add_argument("--audit", type=Path, required=True, help="ACS decision JSONL output")
    parser.add_argument("--output", type=Path, required=True, help="redacted execution JSONL output")
    args = parser.parse_args()
    rows = asyncio.run(run(args.input, args.manifest, args.audit))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(f"ACS host: {len(rows)} mock tool cases; results={args.output}; audit={args.audit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
