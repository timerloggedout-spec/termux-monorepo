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


def _run_cli(tmp_path, template_text, runs_text=None, feeds=None, now="2026-11-03T22:30:00Z"):
    import json as _json
    import subprocess

    tdir = tmp_path / "templates"
    tdir.mkdir(exist_ok=True)
    (tdir / "project-task.yml").write_text(template_text)
    runs = tmp_path / "runs.json"
    if runs_text is not None:
        runs.write_text(runs_text)
    fdir = tmp_path / "feeds"
    fdir.mkdir(exist_ok=True)
    if feeds is not None:
        (fdir / "queue-by-tier.json").write_text(_json.dumps(feeds[0]))
        (fdir / "state.json").write_text(_json.dumps(feeds[1]))
    tiers = tmp_path / "tiers.json"
    tiers.write_text(_json.dumps(TIERS))
    comment = tmp_path / "stamp.md"
    out = tmp_path / "out.txt"
    script = Path(__file__).parent / "swarm_admission.py"
    proc = subprocess.run(
        [sys.executable, str(script),
         "--templates-dir", str(tdir),
         "--tiers", str(tiers),
         "--runs-file", str(runs),
         "--feeds-dir", str(fdir),
         "--now", now,
         "--issue-labels", "project-task",
         "--issue-title", "[task] x",
         "--run-url", "https://example.invalid/run/2",
         "--comment-out", str(comment),
         "--github-output", str(out)],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return comment.read_text(), out.read_text()


def test_collection_error_tolerated_for_nonflow_tier3(tmp_path):
    # #4979 point 3 (supersedes the pre-#4979 sentinel behavior pinned
    # here for proof run 41737482551): a picture failure must NOT defer
    # a non-flow tier -- dispatch-tiers v2 admits tiers 1-3 at any
    # depth and the tier-3 verdict does not consume the picture. The
    # stamp still NAMES the failure and the tolerance.
    import json as _json

    body, out = _run_cli(tmp_path, TEMPLATE,
                         runs_text=_json.dumps({"collection_error": True}))
    assert "ADMITTED" in body and "decision=admitted" in out
    assert "picture: unavailable" in body and "tolerated" in body


def test_collection_error_defers_flow_tier4_with_named_cause(tmp_path):
    # #4979 point 2: a flow-tier filing defers only on a NAMED cause --
    # the failed status+page and the API error class, not the old
    # generic "collection error" sentinel text.
    import json as _json

    t4 = TEMPLATE.replace("# que_tier: 3", "# que_tier: 4")
    sentinel = {"collection_error": {"failed_status": "queued", "failed_page": 3,
                                     "error_class": "rate_limited"}}
    body, out = _run_cli(tmp_path, t4, runs_text=_json.dumps(sentinel))
    assert "DEFERRED" in body and "decision=deferred" in out
    assert "status=queued" in body and "page=3" in body and "rate_limited" in body


def test_fresh_feeds_are_the_picture(tmp_path):
    # #4979 point 1: fresh collector feeds in the checkout are the
    # picture -- the fallback runs file does not even need to exist.
    by_tier = {"schema": "que.queue-by-tier/v1", "generated_at": "2026-11-03T22:29:00Z",
               "tiers": {}}
    active = {str(i): {"status": "queued", "workflow": f"follower {i}", "tier": 4,
                       "created_at": "2026-11-03T22:00:00Z"} for i in range(400)}
    state = {"watermark": "2026-11-03T22:29:00Z", "active": active}
    t4 = TEMPLATE.replace("# que_tier: 3", "# que_tier: 4")
    body, out = _run_cli(tmp_path, t4, runs_text=None, feeds=(by_tier, state))
    assert "DEFERRED" in body and "flow" in body  # 400 queued >= tier-4 threshold
    assert "picture: collector-feeds" in body and "as-of 2026-11-03T22:29:00Z" in body


def test_stale_feeds_fall_back_to_live_picture(tmp_path):
    import json as _json

    by_tier = {"schema": "que.queue-by-tier/v1", "generated_at": "2026-11-03T20:00:00Z",
               "tiers": {}}
    state = {"watermark": "2026-11-03T20:00:00Z", "active": {}}
    live = {"picture_source": "live-fallback", "collected_at": "2026-11-03T22:29:30Z",
            "runs": [run("lane events recorder")]}
    body, out = _run_cli(tmp_path, TEMPLATE, runs_text=_json.dumps(live),
                         feeds=(by_tier, state))
    assert "ADMITTED" in body and "picture: live-fallback" in body


def test_picture_gate(tmp_path):
    import json as _json
    import subprocess

    fdir = tmp_path / "feeds"
    fdir.mkdir()
    (fdir / "queue-by-tier.json").write_text(_json.dumps(
        {"generated_at": "2026-11-03T22:29:00Z", "tiers": {}}))
    (fdir / "state.json").write_text(_json.dumps({"watermark": "2026-11-03T22:29:00Z", "active": {}}))
    out = tmp_path / "gate.txt"
    script = Path(__file__).parent / "swarm_admission.py"
    proc = subprocess.run(
        [sys.executable, str(script), "picture-gate",
         "--feeds-dir", str(fdir), "--now", "2026-11-03T22:30:00Z",
         "--github-output", str(out)],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "fresh"
    assert "feeds_fresh=true" in out.read_text()


def test_missing_tiers_file_defers_not_crashes(tmp_path):
    # Regression for proof run 41731985726: dispatch-tiers.json absent
    # (its PR unmerged) must yield a DEFERRED stamp + exit 0.
    import json as _json
    import subprocess

    tdir = tmp_path / "templates"
    tdir.mkdir()
    (tdir / "project-task.yml").write_text(TEMPLATE)
    runs = tmp_path / "runs.json"
    runs.write_text(_json.dumps([run("lane events recorder")]))
    comment = tmp_path / "stamp.md"
    out = tmp_path / "out.txt"
    script = Path(__file__).parent / "swarm_admission.py"
    proc = subprocess.run(
        [sys.executable, str(script),
         "--templates-dir", str(tdir),
         "--tiers", str(tmp_path / "ABSENT.json"),
         "--runs-file", str(runs),
         "--issue-labels", "project-task",
         "--issue-title", "[task] x",
         "--run-url", "https://example.invalid/run/1",
         "--comment-out", str(comment),
         "--github-output", str(out)],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    body = comment.read_text()
    assert "DEFERRED" in body and "evaluation error" in body
    assert "decision=deferred" in out.read_text()
