"""Regression tests for dispatch-watchdog shared GitHub API budget handling."""

import io
import os
import sys
import urllib.error
from datetime import datetime, timedelta, timezone
from email.message import Message
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dispatch"))
import dispatch_watchdog as dw  # noqa: E402


def _core_snapshot(remaining, limit=5000):
    return {
        "resources": {
            "core": {
                "limit": limit,
                "remaining": remaining,
                "reset": int((datetime.now(timezone.utc)
                              + timedelta(minutes=20)).timestamp()),
            }
        }
    }


def test_preflight_uses_authoritative_headers_and_derived_reserve(monkeypatch):
    def snapshot(remaining):
        headers = Message()
        headers["X-RateLimit-Limit"] = "5000"
        headers["X-RateLimit-Remaining"] = str(remaining)
        headers["X-RateLimit-Reset"] = str(
            int((datetime.now(timezone.utc) + timedelta(minutes=20)).timestamp())
        )
        return _core_snapshot(remaining), headers

    monkeypatch.setattr(dw, "_request",
                        lambda *_args, **_kwargs: snapshot(499))
    with pytest.raises(dw.RateLimitDeferred, match="499/5000"):
        dw._rate_limit_preflight("installation-token")

    monkeypatch.setattr(dw, "_request",
                        lambda *_args, **_kwargs: snapshot(500))
    budget = dw._rate_limit_preflight("installation-token")
    assert budget["reserve"] == 500
    assert budget["remaining"] == 500


def test_rate_limit_403_defers_to_reset(monkeypatch):
    reset = int((datetime.now(timezone.utc)
                 + timedelta(minutes=10)).timestamp())
    headers = Message()
    headers["X-RateLimit-Remaining"] = "0"
    headers["X-RateLimit-Reset"] = str(reset)
    headers["X-RateLimit-Resource"] = "core"
    error = urllib.error.HTTPError(
        "https://api.github.com/repos/example/repo/issues",
        403, "Forbidden", headers,
        io.BytesIO(b'{"message":"API rate limit exceeded for installation"}'),
    )

    def fail_request(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(dw.urllib.request, "urlopen", fail_request)
    with pytest.raises(dw.RateLimitDeferred) as caught:
        dw._request("GET", "https://api.github.com/repos/example/repo/issues",
                    "installation-token")
    assert caught.value.defer_until == datetime.fromtimestamp(
        reset, timezone.utc)
    assert "resource=core" in str(caught.value)


def test_secondary_limit_honors_retry_after_before_hourly_reset(monkeypatch):
    reset = int((datetime.now(timezone.utc)
                 + timedelta(hours=1)).timestamp())
    headers = Message()
    headers["X-RateLimit-Remaining"] = "2500"
    headers["X-RateLimit-Reset"] = str(reset)
    headers["Retry-After"] = "75"
    error = urllib.error.HTTPError(
        "https://api.github.com/repos/example/repo/issues",
        403, "Forbidden", headers,
        io.BytesIO(b'{"message":"You have exceeded a secondary rate limit"}'),
    )

    def fail_request(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(dw.urllib.request, "urlopen", fail_request)
    before = datetime.now(timezone.utc)
    with pytest.raises(dw.RateLimitDeferred) as caught:
        dw._request("GET", "https://api.github.com/repos/example/repo/issues",
                    "installation-token")
    assert timedelta(seconds=74) <= caught.value.defer_until - before \
        <= timedelta(seconds=76)


def test_secondary_limit_without_retry_after_uses_minute_cooldown(monkeypatch):
    reset = int((datetime.now(timezone.utc)
                 + timedelta(hours=1)).timestamp())
    headers = Message()
    headers["X-RateLimit-Remaining"] = "2500"
    headers["X-RateLimit-Reset"] = str(reset)
    error = urllib.error.HTTPError(
        "https://api.github.com/repos/example/repo/issues",
        403, "Forbidden", headers,
        io.BytesIO(b'{"message":"You have exceeded a secondary rate limit"}'),
    )

    def fail_request(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(dw.urllib.request, "urlopen", fail_request)
    before = datetime.now(timezone.utc)
    with pytest.raises(dw.RateLimitDeferred) as caught:
        dw._request("GET", "https://api.github.com/repos/example/repo/issues",
                    "installation-token")
    delta = caught.value.defer_until - before
    assert timedelta(seconds=59) <= delta <= timedelta(seconds=61)


def test_permission_403_remains_a_hard_error(monkeypatch):
    headers = Message()
    headers["X-RateLimit-Remaining"] = "100"
    error = urllib.error.HTTPError(
        "https://api.github.com/repos/example/repo/issues",
        403, "Forbidden", headers,
        io.BytesIO(b'{"message":"Resource not accessible by integration"}'),
    )

    def fail_request(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(dw.urllib.request, "urlopen", fail_request)
    with pytest.raises(RuntimeError, match="403"):
        dw._request("GET", "https://api.github.com/repos/example/repo/issues",
                    "installation-token")


def test_main_records_defer_and_skips_sweep(monkeypatch, tmp_path, capsys):
    output = tmp_path / "output.txt"
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    monkeypatch.setattr(
        dw, "_rate_limit_preflight",
        lambda _token: (_ for _ in ()).throw(
            dw.RateLimitDeferred("core remaining=0", datetime.now(timezone.utc))
        ),
    )
    monkeypatch.setattr(
        dw, "sweep",
        lambda *_args, **_kwargs: pytest.fail("sweep ran after quota deferral"),
    )

    assert dw.main([]) == 0
    assert "deferred=true" in output.read_text()
    assert "DEFERRED" in summary.read_text()
    assert "DEFERRED" in capsys.readouterr().out


def test_queue_budget_defers_before_comment_reads(monkeypatch):
    issues = [
        {
            "number": number,
            "comments": 100,
            "created_at": "2026-11-25T00:00:00Z",
            "labels": [],
            "user": {"login": "filer"},
        }
        for number in range(1, 101)
    ]
    calls = []

    def list_issues(url, _token):
        calls.append(url)
        return issues

    monkeypatch.setattr(dw, "_get_all", list_issues)
    budget = {
        "limit": 5000,
        "remaining": 600,
        "reserve": 500,
        "reset_at": datetime.now(timezone.utc) + timedelta(minutes=10),
    }
    with pytest.raises(dw.RateLimitDeferred, match="planned_reads=202"):
        dw.sweep("owner/repo", "token", datetime.now(timezone.utc),
                 30, 60, apply=False, budget=budget)
    assert len(calls) == 1
    assert "/issues?state=open" in calls[0]


def test_empty_comment_sets_skip_the_comments_endpoint(monkeypatch):
    issue = {
        "number": 7,
        "comments": 0,
        "created_at": "2026-11-25T00:00:00Z",
        "labels": [],
        "user": {"login": "filer"},
    }
    calls = []

    def get_all(url, _token):
        calls.append(url)
        if "/issues?state=open" in url:
            return [issue]
        pytest.fail(f"unexpected API read: {url}")

    monkeypatch.setattr(dw, "_get_all", get_all)
    monkeypatch.setattr(dw, "_run_auto_claim", lambda *_args, **_kwargs: None)
    results = dw.sweep("owner/repo", "token", datetime.now(timezone.utc),
                       30, 60, apply=False)
    assert len(results) == 1
    assert len(calls) == 1


def test_failure_diagnostics_use_run_summary_without_issue_comment_posts():
    workflow = (Path(__file__).resolve().parents[2]
                / ".github" / "workflows" / "dispatch-watchdog.yml").read_text()
    assert "GITHUB_STEP_SUMMARY" in workflow
    assert "/issues/4164/comments" not in workflow
    assert "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}" not in workflow
