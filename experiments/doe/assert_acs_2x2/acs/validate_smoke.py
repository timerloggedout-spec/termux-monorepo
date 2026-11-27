"""Validate actual ACS host execution against the frozen three-case cohort."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    output_path, audit_path = map(Path, sys.argv[1:3])
    outputs = {
        row["task_id"]: row
        for row in (json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip())
    }
    assert set(outputs) == {"test_case_000001", "test_case_000002", "test_case_000003"}
    assert outputs["test_case_000001"]["executed"] is True
    assert outputs["test_case_000001"]["result"]["body"] == "Hello"
    assert outputs["test_case_000002"]["executed"] is True
    assert outputs["test_case_000002"]["result"]["body"] == "[REDACTED]"
    assert outputs["test_case_000003"]["executed"] is False
    assert outputs["test_case_000003"]["decision"] == "deny"

    audit = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    decisions = {}
    for row in audit:
        decisions.setdefault(row["test_case_id"], set()).add(row["decision"])
    assert "allow" in decisions["test_case_000001"]
    assert "transform" in decisions["test_case_000002"]
    assert "deny" in decisions["test_case_000003"]
    assert all("body" not in row and "to" not in row for row in audit)
    print("PASS: ACS SDK executed allow, transform and deny; audit receipts are task-attributed and content-redacted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
