"""Run the mock email tool through the native ACS HostSession path."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agent_control_specification import AgentControl, Decision, HostSession

from policy import EmailPolicy

ROOT = Path(__file__).resolve().parent


def send_email(args: dict[str, Any]) -> dict[str, Any]:
    """Mock tool effect; returns the received arguments."""
    return {"sent": True, **args}


def execute_case(session: HostSession, policy: EmailPolicy, task: dict[str, Any]) -> dict[str, Any]:
    policy.current_task_id = task["task_id"]
    decision = session.pre_tool_call(
        tool_name="send_email",
        args={"to": task["to"], "body": task["body"]},
        call_id=task["task_id"],
    )
    verdict = decision.verdict
    if not verdict.decision.permits:
        return {
            "task_id": task["task_id"],
            "executed": False,
            "decision": verdict.decision.value,
            "reason": verdict.reason,
        }

    enforced_args = {"to": task["to"], "body": task["body"]}
    if verdict.decision is Decision.TRANSFORM:
        transformed = decision.transformed_policy_target
        if not isinstance(transformed, dict):
            raise RuntimeError("ACS transform must produce a tool argument object")
        enforced_args = transformed
    result = send_email(enforced_args)
    session.builder.record_tool_call()
    return {
        "task_id": task["task_id"],
        "executed": True,
        "decision": verdict.decision.value,
        "result": result,
    }


def run(input_path: Path, manifest_path: Path, audit_path: Path) -> list[dict]:
    policy = EmailPolicy(str(audit_path))
    control = AgentControl.from_path(str(manifest_path), policy_dispatcher=policy)
    session = HostSession(
        control,
        agent_id="ceel-email-agent",
        session_id="ceel-assert-acs-runtime-smoke",
    )
    tasks = [
        json.loads(line)
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [execute_case(session, policy, task) for task in tasks]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSONL task rows")
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifest.yaml")
    parser.add_argument("--audit", type=Path, required=True, help="ACS decision JSONL output")
    parser.add_argument("--output", type=Path, required=True, help="redacted execution JSONL output")
    args = parser.parse_args()
    rows = run(args.input, args.manifest, args.audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(f"ACS host: {len(rows)} mock tool cases; results={args.output}; audit={args.audit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
