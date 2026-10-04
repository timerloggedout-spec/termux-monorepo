"""Rate-limit deferral for historical context backfill.

Evidence bind 2026-10-03T17:20Z: receipt e33314bd had zero workflow runs (bot receipt). This commit is the current-SHA gate target for run 37126510237 HTTP 403 deferral.
"""

from __future__ import annotations

import io
import json
from email.message import Message
from urllib.error import HTTPError

from archwiz.context_relationships.build_index import main
from archwiz.context_relationships.github_collector import GitHubClient, RateLimitDeferred


def test_rate_limit_deferred_after_retries(monkeypatch):
    headers = Message()
    headers["Retry-After"] = "0"
    error = HTTPError("https://api.github.com/repos/o/r/issues", 403, "rate limit", headers, io.BytesIO(b"rate limit"))

    def boom(*_args, **_kwargs):
        raise error

    monkeypatch.setattr("archwiz.context_relationships.github_collector.urlopen", boom)
    client = GitHubClient("token", max_retries=0, sleep=lambda _seconds: None)
    try:
        client.get_json("/repos/o/r/issues")
    except RateLimitDeferred as exc:
        assert "deferred after HTTP 403" in str(exc)
    else:
        raise AssertionError("expected RateLimitDeferred")


def test_main_defers_rate_limit(monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_TOKEN", "token")

    def boom(*_args, **_kwargs):
        raise RateLimitDeferred("GitHub API request /repos/o/r/issues deferred after HTTP 403")

    monkeypatch.setattr("archwiz.context_relationships.build_index.build_index", boom)
    code = main([
        "--owner", "o",
        "--repo", "r",
        "--ref", "master",
        "--history-start-page", "7",
    ])
    assert code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["deferred"] is True
    assert payload["history_start_page"] == 7
