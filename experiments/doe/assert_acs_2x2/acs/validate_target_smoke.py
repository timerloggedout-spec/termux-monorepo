"""Execute the exact callable imported by ASSERT eval configs."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["CEEL_ACS_AUDIT_PATH"] = sys.argv[1]

from experiments.doe.assert_acs_2x2.target import chat_acs


def main() -> int:
    outputs = [
        json.loads(chat_acs("[test_case_000001] internal recipient")),
        json.loads(chat_acs("[test_case_000002] tracking token")),
        json.loads(chat_acs("[test_case_000003] external recipient")),
    ]
    assert outputs[0]["sent"] is True
    assert outputs[0]["body"] == "Hello"
    assert outputs[1]["sent"] is True
    assert outputs[1]["body"] == "[REDACTED]"
    assert outputs[2]["sent"] is False
    assert outputs[2]["blocked"] is True
    audit = [
        json.loads(line)
        for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert {row["test_case_id"] for row in audit} == {
        "test_case_000001", "test_case_000002", "test_case_000003"
    }
    print("PASS: ASSERT callable target uses HostSession allow/transform/deny.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
