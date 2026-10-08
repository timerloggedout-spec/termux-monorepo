from datetime import datetime, timedelta, timezone

from scripts.ci.actions_queue_reaper import cutoff_for


def test_schedule_cutoff_is_shorter_than_comment_ghosts():
    now = datetime(2026, 10, 7, 18, 14, tzinfo=timezone.utc)
    schedule = cutoff_for("schedule", now, older_hours=6, schedule_minutes=45)
    other = cutoff_for("issue_comment", now, older_hours=6, schedule_minutes=45)
    assert schedule == now - timedelta(minutes=45)
    assert other == now - timedelta(hours=6)
    assert schedule > other


from scripts.ci.actions_queue_reaper import classify_cancel_failure


def test_not_queued_yet_plus_delete_403_is_github_ghost():
    detail = "Cannot cancel a workflow run that has not been queued yet."
    assert classify_cancel_failure(409, detail, 403) == "github_ghost"
    assert classify_cancel_failure(409, "Cannot cancel a workflow run that is not in progress.", 403) == "uncancellable"
    assert classify_cancel_failure(409, detail, None) == "deleted"

from scripts.ci.actions_queue_reaper import is_known_github_ghost


def test_known_ghosts_skip_cancel_delete():
    assert is_known_github_ghost(37655538554)
    assert is_known_github_ghost(36803855107)
    assert is_known_github_ghost(36803852632)
    assert is_known_github_ghost(34718267095)
    assert not is_known_github_ghost(37817607215)
