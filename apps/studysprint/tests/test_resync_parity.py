"""Tests for Nov 3 re-sync parity tool and new Now features."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from agent import run_agent  # noqa: E402
from resync_parity import audit_resync_parity, compute_git_blob_sha, main as parity_main, scan_local_tree  # noqa: E402
from study_tools import (  # noqa: E402
    PRIVACY_STATEMENT, fetch_study_evidence, format_accessible_status,
    format_trust_receipt, plain_language_action, record_daily_checkin,
    reflow_plan_budget, render_today_view,
)

NOW = datetime(2026, 10, 30, tzinfo=timezone.utc)


def test_compute_git_blob_sha_matches_git_format():
    content = b"hello world\n"
    # echo "hello world" | git hash-object --stdin -> 3b18e512dba79e4c8300dd08aeb37f8e728b8dad
    sha = compute_git_blob_sha(content)
    assert sha == "3b18e512dba79e4c8300dd08aeb37f8e728b8dad"


def test_resync_parity_identical_target_dir(tmp_path: Path):
    app_a = tmp_path / "app_a"
    app_b = tmp_path / "app_b"
    app_a.mkdir()
    app_b.mkdir()

    (app_a / "file1.txt").write_text("content 1")
    (app_b / "file1.txt").write_text("content 1")

    report = audit_resync_parity(local_dir=app_a, target_dir=app_b)
    assert not report["drift_detected"]
    assert report["identical"] == 1
    assert report["differs"] == 0
    assert report["missing_in_target"] == 0
    assert report["missing_in_local"] == 0


def test_resync_parity_detects_differs_and_missing(tmp_path: Path):
    app_a = tmp_path / "app_a"
    app_b = tmp_path / "app_b"
    app_a.mkdir()
    app_b.mkdir()

    (app_a / "f_same.txt").write_text("same")
    (app_b / "f_same.txt").write_text("same")

    (app_a / "f_diff.txt").write_text("changed_here")
    (app_b / "f_diff.txt").write_text("original_upstream")

    (app_a / "only_local.txt").write_text("new")
    (app_b / "only_target.txt").write_text("target_only")

    report = audit_resync_parity(local_dir=app_a, target_dir=app_b)
    assert report["drift_detected"] is True
    assert report["identical"] == 1
    assert report["differs"] == 1
    assert report["missing_in_target"] == 1
    assert report["missing_in_local"] == 1

    files_by_path = {f["path"]: f for f in report["files"]}
    assert files_by_path["f_same.txt"]["status"] == "identical"
    assert files_by_path["f_diff.txt"]["status"] == "differs"
    assert files_by_path["only_local.txt"]["status"] == "missing_in_target"
    assert files_by_path["only_target.txt"]["status"] == "missing_in_local"


def test_resync_parity_expected_additions(tmp_path: Path):
    app_a = tmp_path / "app_a"
    app_b = tmp_path / "app_b"
    app_a.mkdir()
    app_b.mkdir()

    (app_a / "file1.txt").write_text("content 1")
    (app_b / "file1.txt").write_text("content 1")
    (app_a / "new_tool.py").write_text("print(1)")

    # With expected_additions, new_tool.py does not trigger drift
    report = audit_resync_parity(local_dir=app_a, target_dir=app_b,
                                 expected_additions={"new_tool.py"})
    assert report["drift_detected"] is False


def test_resync_parity_cli_exit_codes(tmp_path: Path):
    app_a = tmp_path / "app_a"
    app_b = tmp_path / "app_b"
    app_a.mkdir()
    app_b.mkdir()

    (app_a / "file1.txt").write_text("content 1")
    (app_b / "file1.txt").write_text("content 1")

    ret_ok = parity_main(["--local-dir", str(app_a), "--target-dir", str(app_b)])
    assert ret_ok == 0

    (app_a / "file1.txt").write_text("content mutated")
    ret_drift = parity_main(["--local-dir", str(app_a), "--target-dir", str(app_b)])
    assert ret_drift == 1


# --- Tests for Now features ---


def test_trust_receipt_formatting():
    ev = fetch_study_evidence({"kind": "syllabus", "ref": "examples/syllabus.json"},
                              now=NOW, root=ROOT)
    receipt = format_trust_receipt(ev)
    assert receipt["course"].startswith("BIO 101")
    assert receipt["weeks_count"] == 3
    assert len(receipt["due_dates"]) == 3
    assert receipt["items_verified"] == 8
    assert "Planned from your verified BIO 101" in receipt["trust_statement"]


def test_time_budget_slider_reflow():
    ev = fetch_study_evidence({"kind": "syllabus", "ref": "examples/syllabus.json"},
                              now=NOW, root=ROOT)
    r = run_agent({"id": "t_slider", "action": "draft", "asserted": True,
                   "artifact": {"kind": "syllabus", "ref": "examples/syllabus.json"},
                   "minutes_per_day": 25}, now=NOW, root=ROOT)
    plan = r["plan"]
    # Check that learn sessions are 25 min and retrieve sessions are 10 min
    first_session = plan["weeks"][0]["sessions"][0]
    second_session = plan["weeks"][0]["sessions"][1]
    assert first_session["kind"] == "learn" and first_session["minutes"] == 25
    assert second_session["kind"] == "retrieve" and second_session["minutes"] == 10


def test_today_view_render():
    ev = fetch_study_evidence({"kind": "syllabus", "ref": "examples/syllabus.json"},
                              now=NOW, root=ROOT)
    r = run_agent({"id": "t_today", "action": "draft", "asserted": True,
                   "artifact": {"kind": "syllabus", "ref": "examples/syllabus.json"}},
                  now=NOW, root=ROOT)
    today = r["today_view"]
    assert today is not None
    assert "Today's Sprint" in today["card_title"]
    assert len(today["sessions"]) == 2
    assert any(a["action"] == "mark_missed" for a in today["actions"])
    assert any(a["action"] == "start_session" for a in today["actions"])


def test_daily_checkin_streak_tracking():
    log: dict = {}
    l1 = record_daily_checkin(log, week=1, session_index=0, status="done")
    assert l1["total_checkins"] == 1
    assert l1["replan_recommended"] is False

    l2 = record_daily_checkin(l1, week=1, session_index=1, status="missed")
    assert l2["total_checkins"] == 2
    assert l2["replan_recommended"] is True
    assert l2["recovered_weeks"] == 1
    assert "active or recovered weeks" in l2["streak_metric"]


def test_accessible_status_and_plain_language():
    assert "[✓ ALLOW]" in format_accessible_status("ALLOW_RECOMMENDATION")
    assert "[⚠ ABSTAIN]" in format_accessible_status("ABSTAIN")
    assert "[⛔ ESCALATE]" in format_accessible_status("ESCALATE")

    msg = plain_language_action("replan", {"missed_week": 1, "target_week": 2})
    assert "I moved week 1's sessions to week 2" in msg

    r = run_agent({"id": "t_plain", "action": "draft", "asserted": True,
                   "artifact": {"kind": "syllabus", "ref": "examples/syllabus.json"},
                   "missed_week": 1}, now=NOW, root=ROOT)
    assert r["decision_accessible"].startswith("[✓ ALLOW]")
    assert "I moved week 1's sessions to week 2" in r["plain_language_explanation"]
    assert "No account is required" in r["privacy"]
