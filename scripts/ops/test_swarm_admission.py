"""Tests for swarm_admission (issue-template dispatch, QUE Tranche 4).

Run: python3 -m pytest scripts/ops/test_swarm_admission.py
Interim local proof disclosed as such; the in-Actions exercise is the
issues.opened route firing on the proof filing.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from swarm_admission import evaluate, match_template, parse_block, template_identity

NOW = datetime(2026, 11, 3, 22, 30, tzinfo=timezone.utc)

TEMPLATE = """# SWARM-DISPATCH-BEGIN
# schema: issue-dispatch/v1
# lane: swarm-dispatch
# que_tier: 3
# payload_class: project-task
# route: project-task-dispatch.yml
# after:
# chain:
# SWARM-DISPATCH-END
name: Project Task
title: "[task] "
labels: ["project-task"]
body: []
"""

TIERS = {
    "schema": "queue.dispatch-tiers/v2",
    "chains": [
        {
            "entry": "d1-studysprint",
            "stages": [
                {"node": "gate", "match": ["gate"]},
                {"node": "cuts", "match": ["release-cut"], "scope": "version:0.2.0"},
                {"node": "snapshot", "match": ["submission-snapshot"]},
            ],
        }
    ],
}


def run(name, status="queued", created="2026-11-03T22:00:00Z"):
    return {"name": name, "status": status, "created_at": created}


def test_parse_block():
    b = parse_block(TEMPLATE)
    assert b["lane"] == "swarm-dispatch"
    assert b["que_tier"] == 3
    assert b["payload_class"] == "project-task"
    assert b["after"] == []
    assert parse_block("name: No block here") is None


def test_match_by_label_and_prefix():
    labels, prefix = template_identity(TEMPLATE)
    reg = {"project-task.yml": (parse_block(TEMPLATE), labels, prefix)}
    assert match_template(reg, ["project-task"], "anything")[0] == "project-task.yml"
    assert match_template(reg, [], "[task] do a thing")[0] == "project-task.yml"
    assert match_template(reg, ["other"], "nope")[0] is None


def test_admit_clean():
    b = parse_block(TEMPLATE)
    d, reasons, facts = evaluate(b, TIERS, [run("lane events recorder")], now=NOW)
    assert d == "ADMITTED" and reasons == []
    assert facts["queued_depth"] == 1


def test_after_blocks_and_ancient_excluded():
    b = parse_block(TEMPLATE)
    b["after"] = ["release-cut"]
    d, reasons, _ = evaluate(b, TIERS, [run("studysprint release-cut")], now=NOW)
    assert d == "DEFERRED" and "release-cut" in reasons[0]
    ancient = run("studysprint release-cut", created="2026-10-01T00:00:00Z")
    d2, _, _ = evaluate(b, TIERS, [ancient], now=NOW)
    assert d2 == "ADMITTED"  # wedged ancient holds no runner; never defers


def test_flow_threshold_tier4_only():
    b = parse_block(TEMPLATE)
    b["que_tier"] = 4
    many = [run(f"follower {i}") for i in range(400)]
    d, reasons, _ = evaluate(b, TIERS, many, now=NOW)
    assert d == "DEFERRED" and any("flow" in r for r in reasons)
    b["que_tier"] = 2
    d2, _, facts2 = evaluate(b, TIERS, many, now=NOW)
    assert d2 == "ADMITTED" and facts2["flow_threshold"] is None


def test_chain_prior_stage():
    b = parse_block(TEMPLATE)
    b["chain"] = "d1-studysprint"
    b["chain_stage"] = "2"
    d, reasons, _ = evaluate(b, TIERS, [run("ss release-cut")], now=NOW)
    assert d == "DEFERRED" and any("chain" in r for r in reasons)
    d2, _, _ = evaluate(b, TIERS, [run("unrelated follower")], now=NOW)
    assert d2 == "ADMITTED"
