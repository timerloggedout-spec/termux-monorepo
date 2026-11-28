"""Regression tests for Team MVT evidence completeness handling."""
from scripts.ops.evaluate_team_mvt import EXPECTED_CELLS, summarize


def test_skipped_lane_job_is_incomplete_not_evaluator_failure():
    summary, failed = summarize([], "skipped")
    assert failed is False
    assert summary["status"] == "incomplete"
    assert summary["cells"] == 0
    assert summary["expected"] == EXPECTED_CELLS
    assert summary["promotion_ready"] is False
    assert "lane job was skipped" in summary["reason"]


def test_cancelled_matrix_without_failed_receipts_is_incomplete():
    summary, failed = summarize([], "cancelled")
    assert failed is False
    assert summary["status"] == "incomplete"
    assert summary["promotion_ready"] is False


def test_complete_matrix_keeps_correctness_unknown():
    rows = [
        {"lane": f"lane-{index % 5}", "eligible": "false", "execution_status": "skipped"}
        for index in range(EXPECTED_CELLS)
    ]
    summary, failed = summarize(rows, "success")
    assert failed is False
    assert summary["status"] == "observed"
    assert summary["cells"] == EXPECTED_CELLS
    assert summary["promotion_ready"] is False
    assert "UNKNOWN" in summary["reason"]


def test_unexplained_incomplete_matrix_fails_closed():
    summary, failed = summarize([], "success")
    assert failed is True
    assert summary["status"] == "invalid"
    assert summary["promotion_ready"] is False


def test_complete_matrix_with_execution_failure_fails_closed():
    rows = [
        {"lane": f"lane-{index % 5}", "eligible": "true",
         "execution_status": "failure" if index == 0 else "success"}
        for index in range(EXPECTED_CELLS)
    ]
    summary, failed = summarize(rows, "success")
    assert failed is True
    assert summary["status"] == "execution_failed"
    assert summary["execution_failures"] == 1
    assert summary["promotion_ready"] is False
