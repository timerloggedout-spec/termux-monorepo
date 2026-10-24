"""Tests for scripts/reviewer_metrics/collect.py (reviewer-metrics/v1)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "reviewer_metrics"))

import collect  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "state_comment_1607.txt")


def test_parse_real_state_comment():
    body = open(FIXTURE).read()
    parsed = collect.parse_state_comment(body)
    assert parsed is not None
    assert parsed["fields"]["cycle_id"] == "pr-1607-a7609cd0d1c0"
    assert parsed["fields"]["state"] == "awaiting_provider_response"
    assert parsed["required"] == ["coderabbit"]
    assert parsed["providers"]["coderabbit"]["state"] == "awaiting_provider_response"


def test_parse_rejects_non_state_comment():
    assert collect.parse_state_comment("just a regular comment") is None
    assert collect.parse_state_comment("") is None


def test_classify_file():
    assert collect.classify_file(".github/workflows/peer-review-orchestrator.yml") == "workflows"
    assert collect.classify_file("docs/ops/REVIEWER-JIT-DESIGN.md") == "docs"
    assert collect.classify_file("docs/ops/generated/reviewer-metrics.json") == "generated"
    assert collect.classify_file("deepcli/deepcli/core.py") == "code"
    assert collect.classify_file("tests/test_quota.py") == "tests"
    assert collect.classify_file("ruff.toml") == "config"
    assert collect.classify_file("ops/quota/registry.json") == "data"


def test_classify_files_primary_and_flags():
    ctx = collect.classify_files(["a.py", "b.py", "README.md"])
    assert ctx["primary"] == "code"
    assert ctx["docs_only"] is False
    ctx = collect.classify_files(["docs/a.md", "docs/b.md"])
    assert ctx["primary"] == "docs"
    assert ctx["docs_only"] is True
    ctx = collect.classify_files(["a.py", "b.md"])
    assert ctx["primary"] == "mixed"
    ctx = collect.classify_files([])
    assert ctx["primary"] == "unknown"


def _pr(number=42, login="google-labs-jules[bot]", type_="Bot"):
    return {
        "number": number,
        "user": {"login": login, "type": type_},
        "labels": [{"name": "enhancement"}],
        "changed_files": 2, "additions": 10, "deletions": 3,
    }


def test_build_cycle_records_latency_and_skip():
    body = open(FIXTURE).read().replace("pr-1607-a7609cd0d1c0", "pr-42-a7609cd0d1c0")
    comments = [
        {"body": body, "user": {"login": "timerloggedout-spec"}},
        {"body": "Review skipped — authored by a bot without a seat.",
         "user": {"login": "coderabbitai[bot]"}},
    ]
    reviews = [{
        "user": {"login": "coderabbitai[bot]", "type": "Bot"},
        "commit_id": "a7609cd0d1c08ea8ca18eeeca6fb1448f91b486e",
        "submitted_at": "2026-10-23T23:47:01Z", "state": "COMMENTED",
    }]
    records = collect.build_cycle_records(_pr(), comments, reviews, [], ["x.py", "y.py"])
    assert len(records) == 1
    rec = records[0]
    assert rec["author_class"] == "bot"
    assert rec["primary_class"] == "code"
    assert rec["coderabbit_skipped_notice"] is True
    # Cycle started 23:37:01, review at 23:47:01 -> 600s latency.
    assert rec["providers"]["coderabbit"]["latency_sec"] == 600
    assert rec["issue_comment_volume"]["coderabbit"] == 1


def test_aggregate_delivery_rate():
    rec = {
        "pr": 1, "cycle_id": "pr-1-aaa", "head_sha": "aaa",
        "cycle_started_at": "2026-10-23T00:00:00Z", "state": "responses_collected",
        "ready": "true", "author": "timerloggedout-spec", "author_class": "user",
        "primary_class": "code", "classes": {"code": 1}, "docs_only": False,
        "generated_only": False,
        "size": {"files": 1, "additions": 1, "deletions": 0}, "labels": [],
        "providers": {"coderabbit": {"state": "provider_completed", "required": True,
                                     "delivered": True, "cooldown": False, "latency_sec": 300}},
        "verdicts": {"coderabbit": {"APPROVED": 1}}, "review_comment_counts": {"coderabbit": 4},
        "issue_comment_volume": {"coderabbit": 2}, "coderabbit_skipped_notice": False,
    }
    out = collect.aggregate([rec], prs_examined=1, warnings=[])
    assert out["schema"] == "reviewer-metrics/v1"
    totals = out["providers"]["coderabbit"]["totals"]
    assert totals["delivery_rate"] == 1.0
    assert totals["median_latency_sec"] == 300
    assert out["providers"]["coderabbit"]["by_context"]["user/code"]["cycles"] == 1
    # JSON-serializable end to end.
    json.dumps(out)
