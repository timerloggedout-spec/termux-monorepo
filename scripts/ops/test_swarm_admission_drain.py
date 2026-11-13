"""QUE #4977 Fix 3b — deferred-admission drain regression tests."""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import swarm_admission_drain as drain  # noqa: E402

NOW = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
TIERS = {"chains": []}
TASK_BLOCK = {
    "lane": "swarm-dispatch",
    "payload_class": "project-task",
    "que_tier": 3,
    "route": "project-task-dispatch.yml",
    "after": [],
}
FLOW_BLOCK = {
    "lane": "swarm-dispatch",
    "payload_class": "research-service",
    "que_tier": 4,
    "route": "research-service.yml",
    "after": [],
}


class FakeGitHub:
    def __init__(self, comments=None):
        self.comments = list(comments or [])
        self.posts = []
        self.deletes = []

    def get(self, path):
        assert "/comments?" in path
        return self.comments

    def post(self, path, body):
        self.posts.append((path, body))
        if path.endswith("/comments"):
            self.comments.append({"body": body})

    def delete(self, path):
        self.deletes.append(path)


def test_admission_label_delta_preserves_queue_and_claim_state():
    remove, add = drain.admission_label_delta(
        {"deferred-by-tier", "dispatch-queued", "dispatch-claimed"},
        "ADMITTED",
    )
    assert remove == ["deferred-by-tier"]
    assert add == ["swarm-admitted"]
    # The function never mutates dispatch-queued or dispatch-claimed.
    remove2, add2 = drain.admission_label_delta(
        {"swarm-admitted", "dispatch-queued"}, "DEFERRED"
    )
    assert remove2 == ["swarm-admitted"]
    assert add2 == ["deferred-by-tier"]


def test_non_flow_tier_can_re_evaluate_without_queue_picture():
    decision, reasons, facts = drain.decide(
        TASK_BLOCK, TIERS,
        {"status": "unavailable", "detail": "collector stale; fallback 403"},
        NOW,
    )
    assert decision == "ADMITTED"
    assert reasons == []
    assert facts["picture"]["tolerated"] is True


def test_flow_tier_stays_deferred_when_queue_picture_is_unavailable():
    decision, reasons, facts = drain.decide(
        FLOW_BLOCK, TIERS,
        {"status": "unavailable", "detail": "collector stale; fallback 403"},
        NOW,
    )
    assert decision == "DEFERRED"
    assert "queue picture unavailable" in reasons[0]
    assert facts["picture"]["source"] == "unavailable"


def test_fingerprint_is_stable_and_sensitive_to_decision_evidence():
    a = drain.fingerprint("ADMITTED", [], {"tier": 3, "queued_depth": 0})
    b = drain.fingerprint("ADMITTED", [], {"queued_depth": 0, "tier": 3})
    c = drain.fingerprint("DEFERRED", ["after gate"], {"tier": 3})
    assert a == b
    assert a != c


def test_process_re_evaluates_and_stamps_admission_transition():
    gh = FakeGitHub()
    issue = {
        "number": 5195,
        "title": "[task] DoE: example",
        "labels": [
            {"name": "project-task"},
            {"name": "deferred-by-tier"},
            {"name": "dispatch-queued"},
        ],
    }
    registry = {"project-task.yml": (TASK_BLOCK, ["project-task"], "[task]")}
    picture = {"status": "unavailable", "detail": "stale; fallback 403"}
    result = drain.process(
        gh, issue, registry, TIERS, picture, NOW,
        "https://github.com/example/repo/actions/runs/123",
    )
    assert result["decision"] == "ADMITTED"
    assert result["action"] == "updated"
    assert any(path.endswith("/labels") and body["labels"] == ["swarm-admitted"]
               for path, body in gh.posts)
    assert any(path.endswith("/comments") for path, _ in gh.posts)
    assert any(path.endswith("/labels/deferred-by-tier") for path in gh.deletes)
    assert "dispatch-queued" not in gh.deletes
    assert "dispatch-claimed" not in gh.deletes


def test_repeated_same_deferred_receipt_is_idempotent():
    gh = FakeGitHub()
    issue = {
        "number": 77,
        "title": "research service",
        "labels": [{"name": "research-service"}, {"name": "deferred-by-tier"}],
    }
    registry = {"research-service.yml": (FLOW_BLOCK, ["research-service"], "")}
    picture = {"status": "unavailable", "detail": "stale; fallback 403"}
    first = drain.process(gh, issue, registry, TIERS, picture, NOW, "run-url")
    assert first["decision"] == "DEFERRED"
    first_comment_count = len(gh.comments)
    second = drain.process(gh, issue, registry, TIERS, picture, NOW, "run-url")
    assert second["action"] == "unchanged"
    assert len(gh.comments) == first_comment_count
