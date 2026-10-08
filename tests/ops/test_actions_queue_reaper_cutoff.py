from datetime import datetime, timedelta, timezone

from scripts.ci.actions_queue_reaper import classify_cancel_failure, cutoff_for, reaper_record


def test_schedule_cutoff_is_shorter_than_comment_ghosts():
    now = datetime(2026, 10, 7, 18, 14, tzinfo=timezone.utc)
    schedule = cutoff_for("schedule", now, older_hours=6, schedule_minutes=45)
    other = cutoff_for("issue_comment", now, older_hours=6, schedule_minutes=45)
    assert schedule == now - timedelta(minutes=45)
    assert other == now - timedelta(hours=6)
    assert schedule > other


def test_not_queued_yet_plus_delete_403_is_github_ghost():
    detail = "Cannot cancel a workflow run that has not been queued yet."
    assert classify_cancel_failure(409, detail, 403) == "github_ghost"
    assert classify_cancel_failure(409, "Cannot cancel a workflow run that is not in progress.", 403) == "uncancellable"
    assert classify_cancel_failure(409, detail, None) == "deleted"


def test_reaper_record_keeps_disabled_workflow_id():
    row = reaper_record({
        "id": 37655538554,
        "name": "Merge Promotion Queue",
        "event": "schedule",
        "created_at": "2026-10-07T16:57:32Z",
        "head_branch": "master",
        "workflow_id": 354842048,
    })
    assert row["workflow_id"] == 354842048
    assert row["id"] == 37655538554
    assert "action" not in row
