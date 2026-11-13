from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "swarm_admission_drain", ROOT / "scripts" / "ops" / "swarm_admission_drain.py"
)
drain = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(drain)


class FakeGitHub:
    def __init__(self, issue, comments=None):
        self.issue = issue
        self.comments = comments or []
        self.mutations = []

    def get(self, path):
        if path.endswith("/comments?per_page=100&page=1"):
            return list(self.comments)
        if path.endswith(f"/issues/{self.issue['number']}"):
            return self.issue
        raise AssertionError(f"unexpected GET {path}")

    def post(self, path, body):
        self.mutations.append(("POST", path, body))
        return {}

    def delete(self, path):
        self.mutations.append(("DELETE", path, None))
        return {}


def test_admission_label_delta_changes_only_admission_labels():
    current = {"project-task", "dispatch-queued", "deferred-by-tier"}
    remove, add = drain.admission_label_delta(current, "ADMITTED")
    assert remove == ["deferred-by-tier"]
    assert add == ["swarm-admitted"]
    assert "dispatch-queued" in current
    assert "project-task" in current


def test_deferred_label_delta_never_touches_claim_or_queue_labels():
    current = {"project-task", "dispatch-queued", "swarm-admitted"}
    remove, add = drain.admission_label_delta(current, "DEFERRED")
    assert remove == ["swarm-admitted"]
    assert add == ["deferred-by-tier"]
    assert "dispatch-queued" in current
    assert "project-task" in current


def test_fingerprint_is_stable_for_equivalent_facts():
    left = {"tier": 3, "after": {"build": 0}, "chain": {}}
    right = {"chain": {}, "after": {"build": 0}, "tier": 3}
    assert drain.fingerprint("ADMITTED", [], left) == drain.fingerprint(
        "ADMITTED", [], right
    )


def test_latest_fingerprint_reads_newest_receipt():
    old = "a" * 64
    new = "b" * 64
    comments = [
        {"body": f"receipt <!-- que-admission-drain:v1 sha256={old} -->"},
        {"body": f"receipt <!-- que-admission-drain:v1 sha256={new} -->"},
    ]
    assert drain.latest_fingerprint(comments) == new


def test_receipt_uses_real_newlines():
    block = {
        "lane": "swarm-dispatch",
        "que_tier": 3,
        "payload_class": "project-task",
        "route": "project-task-dispatch.yml",
    }
    facts = {
        "tier": 3, "queued_depth": 0, "flow_threshold": None,
        "after": {}, "chain": {},
        "picture": {"source": "unavailable", "detail": "stale", "tolerated": True},
    }
    body = drain.receipt_body(
        "project-task.yml", block, "ADMITTED", [], facts,
        "https://github.com/example/actions", "c" * 64,
    )
    assert "\n\n<!-- que-admission-drain:v1" in body
    assert "\\n\\n<!-- que-admission-drain:v1" not in body


def test_claimed_issue_is_never_reconsidered():
    now = datetime(2026, 11, 13, tzinfo=timezone.utc)
    issue = {
        "number": 7,
        "title": "[task] Example",
        "state": "open",
        "labels": [
            {"name": "project-task"},
            {"name": "dispatch-queued"},
            {"name": "deferred-by-tier"},
            {"name": "dispatch-claimed"},
        ],
    }
    gh = FakeGitHub(issue, [{"body": "[MUSEai] PRODUCER CLAIM"}])
    registry = {
        "project-task.yml": (
            {"lane": "swarm-dispatch", "que_tier": 3,
             "payload_class": "project-task", "route": "project-task-dispatch.yml"},
            ["project-task"], "[task]",
        )
    }
    result = drain.process(
        gh, issue, registry, {}, {"status": "unavailable", "detail": "stale"},
        now, "https://github.com/example/actions", dry_run=False,
    )
    assert result["action"] == "skip_already_claimed"
    assert gh.mutations == []


def test_dry_run_never_mutates_github():
    now = datetime(2026, 11, 13, tzinfo=timezone.utc)
    issue = {
        "number": 8,
        "title": "[task] Example",
        "state": "open",
        "labels": [
            {"name": "project-task"},
            {"name": "dispatch-queued"},
            {"name": "deferred-by-tier"},
        ],
    }
    gh = FakeGitHub(issue, [])
    registry = {
        "project-task.yml": (
            {"lane": "swarm-dispatch", "que_tier": 3,
             "payload_class": "project-task", "route": "project-task-dispatch.yml"},
            ["project-task"], "[task]",
        )
    }
    result = drain.process(
        gh, issue, registry, {}, {"status": "unavailable", "detail": "stale"},
        now, "https://github.com/example/actions", dry_run=True,
    )
    assert result["decision"] == "ADMITTED"
    assert result["action"] == "would_update"
    assert gh.mutations == []
