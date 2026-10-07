from datetime import datetime, timedelta, timezone

from scripts.ci.actions_queue_reaper import cutoff_for


def test_schedule_cutoff_is_shorter_than_comment_ghosts():
    now = datetime(2026, 10, 7, 18, 14, tzinfo=timezone.utc)
    schedule = cutoff_for("schedule", now, older_hours=6, schedule_minutes=45)
    other = cutoff_for("issue_comment", now, older_hours=6, schedule_minutes=45)
    assert schedule == now - timedelta(minutes=45)
    assert other == now - timedelta(hours=6)
    assert schedule > other
