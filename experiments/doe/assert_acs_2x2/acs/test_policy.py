"""Pure dispatcher tests; the native ACS SDK is optional for this test file."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from policy import EmailPolicy


def invocation(point: str, args: dict) -> dict:
    return {
        "input": {
            "intervention_point": point,
            "policy_target": {"value": args},
            "tool": {"name": "send_email"},
            "tool_call": {"call_id": "case-1", "name": "send_email"},
        }
    }


class EmailPolicyTests(unittest.TestCase):
    def test_internal_recipient_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            verdict = EmailPolicy(str(Path(tmp) / "audit.jsonl")).evaluate(
                invocation("pre_tool_call", {"to": "customer@example.com", "body": "Hello"})
            )
        self.assertEqual("allow", verdict["decision"])

    def test_tracking_token_is_transformed(self):
        with tempfile.TemporaryDirectory() as tmp:
            verdict = EmailPolicy(str(Path(tmp) / "audit.jsonl")).evaluate(
                invocation("pre_tool_call", {"to": "customer@example.com", "body": "TRACK-123"})
            )
        self.assertEqual("transform", verdict["decision"])
        self.assertEqual("[REDACTED]", verdict["transform"]["value"])

    def test_external_recipient_is_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            verdict = EmailPolicy(str(Path(tmp) / "audit.jsonl")).evaluate(
                invocation("pre_tool_call", {"to": "partner@EXAMPLE.NET", "body": "Hello"})
            )
        self.assertEqual("deny", verdict["decision"])

    def test_post_tool_point_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            verdict = EmailPolicy(str(Path(tmp) / "audit.jsonl")).evaluate(
                invocation("post_tool_call", {"sent": True})
            )
        self.assertEqual("allow", verdict["decision"])

    def test_audit_is_redacted_and_attributed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "audit.jsonl"
            EmailPolicy(str(path)).evaluate(
                invocation("pre_tool_call", {"to": "customer@example.com", "body": "secret body"})
            )
            row = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual("case-1", row["test_case_id"])
        self.assertEqual("allow", row["decision"])
        self.assertNotIn("secret body", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
