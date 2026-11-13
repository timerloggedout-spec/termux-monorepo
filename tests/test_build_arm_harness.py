"""Harness adapter + census marker tests (QUE #5261).

The marker failure of record (#5151 correction c.6823683769):
sealion/cohere/baseten = tool_call_seen TRUE, roundtrip_ok FALSE,
marker_not_reported. Rule: observability before protocol change
(#5151 c.6823803091) — the census row now carries the final reply
excerpt + marker_state; the Cohere v2 adapter fix (document id) is
the prime-suspect protocol correction.

Run: python3 -m pytest tests/test_build_arm_harness.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "ops"))
import build_arm_census as census  # noqa: E402
import build_arm_harness as harness  # noqa: E402

ROOT = Path(__file__).parent.parent
CALL = {"id": "call-1", "name": "read_file",
        "arguments": {"path": "ops/dispatch/build-arms.json"}}


def _arm(protocol):
    return {"arm_id": "fixture-arm", "model": "fixture-model",
            "endpoint": {"provider": "fixture", "protocol": protocol}}


def test_cohere_v2_tool_result_document_carries_id():
    messages = []
    reply = {"content": None, "tool_calls": [CALL]}
    harness.append_assistant_and_results(
        messages, _arm("cohere-v2"), reply, [(CALL, "build-arms/v1")])
    tool_msg = messages[-1]
    assert tool_msg["role"] == "tool"
    block = tool_msg["content"][0]
    assert block["type"] == "document"
    # The fix: Cohere v2 drops document blocks without an id.
    assert block["document"]["id"] == "doc-call-1"
    assert block["document"]["data"] == "build-arms/v1"


def test_openai_tool_result_shape_unchanged():
    messages = []
    reply = {"content": None, "tool_calls": [CALL]}
    harness.append_assistant_and_results(
        messages, _arm("openai"), reply, [(CALL, "build-arms/v1")])
    assert messages[-1] == {"role": "tool", "tool_call_id": "call-1",
                            "content": "build-arms/v1"}


def _census_with_final(monkeypatch, final_text):
    arm = {"arm_id": "fixture-arm", "model": "fixture-model",
           "budget": {"class": "free-tier"}, "status": "candidate",
           "endpoint": {"provider": "fixture", "protocol": "openai",
                        "secret_env": "FIXTURE_ARM_KEY"}}
    monkeypatch.setenv("FIXTURE_ARM_KEY", "fixture")
    replies = iter([
        {"content": "OK", "tool_calls": [], "usage": {}},          # invoke
        {"content": None, "tool_calls": [CALL], "usage": {}},      # loop
        {"content": final_text, "tool_calls": [], "usage": {}},    # final
    ])
    monkeypatch.setattr(harness, "chat_once",
                        lambda a, m, t, max_tokens=2048: next(replies))
    return census.census_http_arm(arm, ROOT)


def test_census_marker_exact_reports_and_is_eligible(monkeypatch):
    row = _census_with_final(monkeypatch, "build-arms/v1")
    loop = row["checks"]["agent_loop"]
    assert row["verdict"] == "eligible"
    assert loop["roundtrip_ok"] is True
    assert loop["marker_state"] == "exact"
    assert loop["final_reply_excerpt"] == "build-arms/v1"


def test_census_marker_contained_is_observable_not_eligible(monkeypatch):
    row = _census_with_final(
        monkeypatch, "The schema value is `build-arms/v1`.")
    loop = row["checks"]["agent_loop"]
    assert row["verdict"] == "failed"
    assert loop["marker_state"] == "contained"
    assert "build-arms/v1" in loop["final_reply_excerpt"]


def test_census_marker_empty_and_absent_are_distinguishable(monkeypatch):
    empty = _census_with_final(monkeypatch, "")
    assert empty["checks"]["agent_loop"]["marker_state"] == "empty"
    absent = _census_with_final(monkeypatch, "I could not read the file.")
    loop = absent["checks"]["agent_loop"]
    assert loop["marker_state"] == "absent"
    assert loop["final_reply_excerpt"] == "I could not read the file."
