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
_CONTROL: Any = None
_SESSION: Any = None
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


def _send_email(args: dict[str, str]) -> dict[str, Any]:
    """Mock tool effect; returns the received arguments."""
    return {"sent": True, **args}


def chat_native(message: str) -> str:
    """Native baseline: execute the mock tool without policy mediation."""
    _task_id, args = _case(message)
    return json.dumps(_send_email(args), sort_keys=True)


def chat_acs(message: str) -> str:
    """ACS treatment: mediate the same mock tool through HostSession."""
    from agent_control_specification import AgentControl, Decision, HostSession

    global _CONTROL, _SESSION
    task_id, args = _case(message)
    _POLICY.current_task_id = task_id
    if _SESSION is None:
        _CONTROL = AgentControl.from_path(
            str(MANIFEST),
            policy_dispatcher=_POLICY,
        )
        _SESSION = HostSession(
            _CONTROL,
            agent_id="ceel-email-agent",
            session_id="ceel-assert-acs-eval",
        )

    decision = _SESSION.pre_tool_call(
        tool_name="send_email",
        args=args,
        call_id=task_id,
    )
    verdict = decision.verdict
    if not verdict.decision.permits:
        return json.dumps({
            "sent": False,
            "blocked": True,
            "reason": verdict.reason,
        }, sort_keys=True)

    enforced_args = args
    if verdict.decision is Decision.TRANSFORM:
        transformed = decision.transformed_policy_target
        if not isinstance(transformed, dict):
            raise RuntimeError("ACS transform must produce a tool argument object")
        enforced_args = transformed
    result = _send_email(enforced_args)
    _SESSION.builder.record_tool_call()
    return json.dumps(result, sort_keys=True)
