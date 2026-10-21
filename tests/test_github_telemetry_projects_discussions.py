"""Pure normalize tests for Projects + Discussions (no network)."""
from __future__ import annotations

from ops.github_telemetry.discussions import normalize_discussions_payload
from ops.github_telemetry.projects import normalize_projects_payload


def test_normalize_projects():
    payload = {
        "data": {
            "repository": {
                "projectsV2": {
                    "nodes": [
                        {
                            "id": "PVT_1",
                            "title": "Ops",
                            "number": 1,
                            "url": "https://example.com",
                            "closed": False,
                            "items": {
                                "totalCount": 2,
                                "nodes": [
                                    {
                                        "type": "ISSUE",
                                        "content": {
                                            "__typename": "Issue",
                                            "number": 9,
                                            "title": "t",
                                            "state": "OPEN",
                                            "url": "u",
                                        },
                                    }
                                ],
                            },
                        }
                    ]
                }
            }
        }
    }
    s = normalize_projects_payload(payload)
    assert s["project_count"] == 1
    assert s["projects"][0]["title"] == "Ops"
    assert s["label"] == "locally_reconstructed"


def test_normalize_discussions():
    payload = {
        "data": {
            "repository": {
                "discussions": {
                    "totalCount": 1,
                    "nodes": [
                        {
                            "number": 3,
                            "title": "Hello",
                            "url": "u",
                            "createdAt": "2026-01-01T00:00:00Z",
                            "updatedAt": "2026-01-02T00:00:00Z",
                            "answerChosenAt": None,
                            "category": {"name": "General", "slug": "general"},
                            "author": {"login": "alice"},
                            "comments": {"totalCount": 4},
                        }
                    ],
                }
            }
        }
    }
    s = normalize_discussions_payload(payload)
    assert s["discussion_count"] == 1
    assert s["discussions"][0]["title"] == "Hello"
    assert s["discussions"][0]["answered"] is False
