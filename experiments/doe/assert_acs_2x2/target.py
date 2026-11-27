"""Deterministic ASSERT callable target for the ACS tool-boundary pilot."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from experiments.doe.assert_acs_2x2.acs.policy import EmailPolicy

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "experiments/doe/assert_acs_2x2/acs/manifest.yaml"
AUDIT_PATH = Path(os.environ.get(
    "CEEL_ACS_AUDIT_PATH",
    ROOT / "artifacts/ceel-assert-acs-2x2/acs-decisions.jsonl",
))
_CONTROL: AgentControl | None = None
_POLICY = EmailPolicy(str(AUDIT_PATH))


DESIGN = json.loads((ROOT / "experiments/doe/assert_acs_2x2/DESIGN.json").read_text(encoding="utf-8"))
TASKS = {task["task_id"]: task for task in DESIGN["tasks"]}


def _case(message: str) -> tuple[str, dict[str, str]]:
    match = re.search(r"\[(test_case_\d{6})\]", message)
    if not match:
        raise ValueError("ASSERT test prompt must carry its frozen test_case_id")
    task_id = match.group(1)
    task = TASKS.get(task_id)
    if task is None:
        raise ValueError(f"unrecognized frozen task id: {task_id}")
    return task_id, dict(task["tool_input"])

async def _send_email(args: dict[str, str]) -> dict[str, Any]:
    """Mock tool side effect. It performs no network or mail operation."""
    return {"sent": True, **args}


def chat_native(message: str) -> str:
    """Native baseline: execute the mock tool without governance mediation."""
    _task_id, args = _case(message)
    result = {"sent": True, **args}
    return json.dumps(result, sort_keys=True)


async def chat_acs(message: str) -> str:
    """ACS treatment: mediate the same mock tool call with native ACS."""
    from agent_control_specification import AgentControl, AgentControlBlocked

    global _CONTROL
    task_id, args = _case(message)
    _POLICY.current_task_id = task_id
    if _CONTROL is None:
        _CONTROL = AgentControl.from_path(
            str(MANIFEST),
            policy_dispatcher=_POLICY,
        )
    try:
        result = await _CONTROL.run_tool(
            "send_email",
            args,
            _send_email,
            tool_call_id=task_id,
        )
        return json.dumps(result.value, sort_keys=True)
    except AgentControlBlocked as exc:
        return json.dumps({
            "sent": False,
            "blocked": True,
            "reason": exc.result.verdict.reason,
        }, sort_keys=True)
