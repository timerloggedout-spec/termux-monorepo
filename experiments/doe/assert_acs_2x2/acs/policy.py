"""ACS custom dispatcher for the CEEL email-tool conformance fixture."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TRACKING_TOKEN = re.compile(r"TRACK-[A-Za-z0-9-]+")


class EmailPolicy:
    """Decision logic; the host supplies per-call audit attribution."""

    def __init__(self, audit_path: str | None = None) -> None:
        self.audit_path = Path(audit_path or os.environ.get("CEEL_ACS_AUDIT_PATH", "acs-decisions.jsonl"))
        self.current_task_id: str | None = None

    def evaluate(self, invocation: Mapping[str, Any]) -> dict[str, Any]:
        policy_input = invocation["input"]
        point = policy_input.get("intervention_point")
        if point != "pre_tool_call":
            verdict = {"decision": "allow"}
        else:
            args = policy_input["policy_target"]["value"]
            recipient = str(args.get("to", ""))
            body = str(args.get("body", ""))
            if recipient.lower().endswith("@example.net"):
                verdict = {
                    "decision": "deny",
                    "reason": "external_recipient_blocked",
                    "message": "External recipients require a separate approval path.",
                }
            else:
                redacted = TRACKING_TOKEN.sub("[REDACTED]", body)
                if redacted != body:
                    verdict = {
                        "decision": "transform",
                        "reason": "tracking_token_redacted",
                        "message": "Tracking token redacted before tool execution.",
                        "transform": {
                            "path": "$policy_target.body",
                            "value": redacted,
                        },
                    }
                else:
                    verdict = {"decision": "allow"}
        self._audit(policy_input, point, verdict)
        return verdict

    def _audit(self, policy_input: Mapping[str, Any], point: str | None, verdict: dict) -> None:
        tool = policy_input.get("tool") or {}
        call = policy_input.get("tool_call") or {}
        row = {
            "test_case_id": self.current_task_id or call.get("call_id") or call.get("id"),
            "intervention_point": point,
            "decision": verdict["decision"],
            "reason": verdict.get("reason"),
            "policy_id": "ceel-email-policy/v1",
            "tool_name": tool.get("name") or call.get("name"),
            "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
