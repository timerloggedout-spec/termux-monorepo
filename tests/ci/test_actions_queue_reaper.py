"""Queue reaper classification. No network."""

from scripts.ci.actions_queue_reaper import residual_detail, still_queued


def test_still_queued_only_when_status_queued_and_open():
    assert still_queued({"status": "queued", "conclusion": None})
    assert not still_queued({"status": "completed", "conclusion": "cancelled"})
    assert not still_queued({"status": "in_progress", "conclusion": None})


def test_residual_detail_names_known_ghost_bodies():
    assert residual_detail('{"message":"Could not delete the workflow run"}') == (
        "residual ghost: delete 403"
    )
    assert "not queued yet" in residual_detail(
        "Cannot cancel a workflow run that has not been queued yet."
    )
