import io
import sys
from datetime import datetime, timedelta, timezone
from email.message import Message
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cadence_kick as k  # noqa: E402
import que_feed_collect as q  # noqa: E402
import refresh_api_backoff as refresh_backoff  # noqa: E402


def _run(created, conclusion, updated=None):
    return {
        "status": "completed",
        "conclusion": conclusion,
        "created_at": created,
        "updated_at": updated or created,
    }


def _fresh_api_stats():
    return {
        "core": {"attempts": 0, "successes": 0},
        "search": {"attempts": 0, "successes": 0},
        "preflight": {"attempts": 0, "successes": 0},
        "retries": 0,
    }


def _http_error(path, code, body, headers):
    return q.urllib.error.HTTPError(
        q.API + path, code, "Forbidden", headers, io.BytesIO(body))


INCIDENT_NOW = datetime(2026, 11, 25, 17, 22, 33, tzinfo=timezone.utc)


def test_failed_qf_run_does_not_refresh_stale_feed_and_is_cooled_down():
    runs = [
        _run("2026-11-25T17:03:49Z", "success", "2026-11-25T17:04:45Z"),
        _run("2026-11-25T17:17:49Z", "failure", "2026-11-25T17:21:52Z"),
    ]
    result = k.decide(runs, 12, INCIDENT_NOW, success_only=True,
                      failure_backoff_min=12)
    assert result["action"] == "skip"
    assert result["last_success_age_min"] > 12
    assert result["last_failure_age_min"] < 1
    assert result["failure_backoff_min"] == 12
    assert "stale successful feed" in result["reason"]


def test_qf_failure_cooldown_uses_terminal_updated_at_after_long_queue_time():
    # This fixture matches the Actions workflow-runs REST shape: no
    # completed_at field, and updated_at records the terminal change.
    run = _run("2026-11-25T17:00:00Z", "failure",
               "2026-11-25T17:21:52Z")
    during_cooldown = k.decide([run], 12, INCIDENT_NOW,
                               success_only=True, failure_backoff_min=12)
    after_cooldown = k.decide(
        [run], 12, datetime(2026, 11, 25, 17, 34, 0, tzinfo=timezone.utc),
        success_only=True, failure_backoff_min=12)

    assert "completed_at" not in run
    assert during_cooldown["action"] == "skip"
    assert during_cooldown["last_failure_age_min"] < 1
    assert after_cooldown["action"] == "kick"


def test_qf_kicks_after_failed_run_cooldown_expires():
    runs = [
        _run("2026-11-25T17:03:49Z", "success"),
        _run("2026-11-25T17:17:49Z", "failure", "2026-11-25T17:21:52Z"),
    ]
    later = datetime(2026, 11, 25, 17, 34, 0, tzinfo=timezone.utc)
    result = k.decide(runs, 12, later, success_only=True,
                      failure_backoff_min=12)
    assert result["action"] == "kick"
    assert result["last_success_age_min"] > 12


def test_qf_backoff_marker_suppresses_kick_until_server_deadline():
    deadline = "2026-11-25T18:00:00Z"
    before = k.decide([], 12, INCIDENT_NOW, success_only=True,
                      failure_backoff_min=12,
                      retry_not_before=deadline)
    after = k.decide([], 12, datetime(2026, 11, 25, 18, 0, 1,
                                      tzinfo=timezone.utc),
                     success_only=True, failure_backoff_min=12,
                     retry_not_before=deadline)
    assert before["action"] == "skip"
    assert "server-directed API backoff" in before["reason"]
    assert after["action"] == "kick"


def test_recent_success_remains_fresh_despite_a_later_failed_attempt():
    runs = [
        _run("2026-11-25T17:15:00Z", "success"),
        _run("2026-11-25T17:17:49Z", "failure", "2026-11-25T17:21:52Z"),
    ]
    result = k.decide(runs, 12, INCIDENT_NOW, success_only=True,
                      failure_backoff_min=12)
    assert result["action"] == "ok"
    assert result["last_success_age_min"] < 12


def test_qf_inflight_still_prevents_duplicate_dispatch():
    result = k.decide([
        {"status": "in_progress", "created_at": "2026-11-25T17:20:00Z"},
        _run("2026-11-25T17:03:49Z", "success"),
    ], 12, INCIDENT_NOW, success_only=True, failure_backoff_min=12)
    assert result["action"] == "skip"
    assert result["reason"] == "in-flight"


def test_dispatch_watchdog_retains_legacy_attempt_age_decision():
    result = k.decide([
        _run("2026-11-25T17:17:49Z", "failure"),
    ], 15, INCIDENT_NOW)
    assert result["action"] == "ok"
    assert result["reason"].startswith("age ")


def test_unclassified_403_is_logged_with_response_evidence_and_not_retried(
        monkeypatch, capsys):
    path = "/repos/timerloggedout-spec/termux-monorepo/actions/runs?status=queued"
    headers = Message()
    headers["X-GitHub-Request-Id"] = "SAFE-REQUEST-ID"
    headers["X-RateLimit-Remaining"] = "4999"
    body = b'{"message":"Resource not accessible by integration"}'
    calls = []

    def fail(*_args, **_kwargs):
        calls.append(1)
        raise _http_error(path, 403, body, headers)

    monkeypatch.setattr(q, "API_STATS", _fresh_api_stats())
    monkeypatch.setattr(q.urllib.request, "urlopen", fail)
    monkeypatch.setattr(q.time, "sleep", lambda _seconds: pytest.fail(
        "unclassified 403 must not be retried"))
    with pytest.raises(q.ApiHttpError) as caught:
        q.api(path, "not-a-real-token")

    diagnostic = str(caught.value)
    assert len(calls) == 1
    assert "Resource not accessible by integration" in diagnostic
    assert "SAFE-REQUEST-ID" in diagnostic
    assert "not retried (403 is unclassified)" in diagnostic
    assert "not-a-real-token" not in diagnostic
    assert q.api_request_summary()["core_attempts"] == 1
    assert q.api_request_summary()["retries"] == 0
    assert "SAFE-REQUEST-ID" in capsys.readouterr().err


def test_secondary_403_honors_retry_after_and_counts_retry(monkeypatch):
    path = "/repos/timerloggedout-spec/termux-monorepo/actions/runs?status=queued"
    headers = Message()
    headers["Retry-After"] = "2"
    headers["X-RateLimit-Resource"] = "core"
    body = b'{"message":"You have exceeded a secondary rate limit"}'
    calls = []
    delays = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b'{"workflow_runs":[]}'

    def respond(*_args, **_kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise _http_error(path, 403, body, headers)
        return Response()

    monkeypatch.setattr(q, "API_STATS", _fresh_api_stats())
    monkeypatch.setattr(q.urllib.request, "urlopen", respond)
    monkeypatch.setattr(q.time, "sleep", delays.append)
    assert q.api(path, "token") == {"workflow_runs": []}
    assert len(calls) == 2
    assert delays == [2.0]
    stats = q.api_request_summary()
    assert stats["core_attempts"] == 2
    assert stats["core_successes"] == 1
    assert stats["retries"] == 1


@pytest.mark.parametrize(("reset", "retry_after", "expected"), [
    ("105", "120", 120.0),
    ("150", "20", 50.0),
    (None, "120", 120.0),
    ("not-a-timestamp", "120", 120.0),
])
def test_primary_limit_uses_later_valid_reset_or_retry_after(
        reset, retry_after, expected):
    headers = {"X-RateLimit-Remaining": "0",
               "Retry-After": retry_after}
    if reset is not None:
        headers["X-RateLimit-Reset"] = reset

    delay, _reason = q._rate_limit_retry(
        403, '{"message":"API rate limit exceeded"}', headers, 0,
        now_ts=100.0)

    assert delay == expected


def test_primary_limit_waits_for_reset_or_defers_without_retry(monkeypatch):
    path = "/repos/timerloggedout-spec/termux-monorepo/actions/runs?status=queued"
    headers = Message()
    headers["X-RateLimit-Remaining"] = "0"
    headers["X-RateLimit-Reset"] = "1000"
    body = b'{"message":"API rate limit exceeded"}'
    monkeypatch.setattr(q, "API_STATS", _fresh_api_stats())
    monkeypatch.setattr(q.urllib.request, "urlopen", lambda *_a, **_k: (
        _ for _ in ()).throw(_http_error(path, 403, body, headers)))
    monkeypatch.setattr(q.time, "sleep", lambda _seconds: pytest.fail(
        "long primary reset must defer instead of retrying early"))
    monkeypatch.setattr(q.time, "time", lambda: 100.0)
    output = Path("/tmp/que403-github-output")
    output.unlink(missing_ok=True)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    with pytest.raises(q.ApiHttpError) as caught:
        q.api(path, "token")
    assert "deferred until 1970-01-01T00:16:40Z" in str(caught.value)
    assert "rate_limit_defer_until=1970-01-01T00:16:40Z" in output.read_text()
    assert q.api_request_summary()["core_attempts"] == 1
    assert q.api_request_summary()["retries"] == 0


def test_last_short_rate_limit_retry_persists_deadline_without_sleeping(
        monkeypatch, tmp_path):
    path = "/repos/timerloggedout-spec/termux-monorepo/actions/runs?status=queued"
    headers = Message()
    headers["Retry-After"] = "4"
    body = b'{"message":"You have exceeded a secondary rate limit"}'
    calls, delays = [], []

    def fail(*_args, **_kwargs):
        calls.append(1)
        raise _http_error(path, 429, body, headers)

    monkeypatch.setattr(q, "API_STATS", _fresh_api_stats())
    monkeypatch.setattr(q.urllib.request, "urlopen", fail)
    monkeypatch.setattr(q.time, "sleep", delays.append)
    monkeypatch.setattr(q.time, "time", lambda: 1000.0)
    output = tmp_path / "github-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    with pytest.raises(q.ApiHttpError) as caught:
        q.api(path, "token")

    assert len(calls) == q.API_RETRY_MAX_ATTEMPTS
    assert delays == [4.0, 4.0]
    assert "deferred until 1970-01-01T00:16:44Z" in str(caught.value)
    assert "rate_limit_defer_until=1970-01-01T00:16:44Z" in output.read_text()


def test_active_persisted_backoff_skips_all_collector_api_requests(
        monkeypatch, tmp_path, capsys):
    now = datetime(2026, 11, 25, 17, 22, 33, tzinfo=timezone.utc)
    marker = tmp_path / "api-backoff.json"
    marker.write_text(
        '{"schema":"que.api-backoff/v1",'
        '"not_before":"2026-11-25T18:00:00Z"}')
    monkeypatch.setattr(q, "API_BACKOFF_FILE", marker)
    monkeypatch.setattr(q, "now", lambda: now)
    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setattr(q, "api", lambda *_a, **_k: pytest.fail(
        "active persisted backoff must prevent API requests"))
    assert q.main() == 1
    assert "server-directed API retry window" in capsys.readouterr().out
    assert marker.exists()


def test_restart_refreshes_published_backoff_before_collector_api_calls(
        monkeypatch, tmp_path, capsys):
    master_marker = tmp_path / "master" / "api-backoff.json"
    local_marker = tmp_path / "event-checkout" / "api-backoff.json"
    master_marker.parent.mkdir(parents=True)
    local_marker.parent.mkdir(parents=True)
    master_marker.write_text(
        '{"schema":"que.api-backoff/v1",'
        '"not_before":"2026-11-25T18:00:00Z"}')
    # Simulate a rerun pinned to an older SHA with only an expired marker.
    local_marker.write_text(
        '{"schema":"que.api-backoff/v1",'
        '"not_before":"2026-11-25T17:00:00Z"}')

    assert "refreshed marker" in refresh_backoff.refresh(
        master_marker, local_marker)
    monkeypatch.setattr(q, "API_BACKOFF_FILE", local_marker)
    monkeypatch.setattr(q, "now", lambda: INCIDENT_NOW)
    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setattr(q, "api", lambda *_a, **_k: pytest.fail(
        "restart must honor the published master deadline before API calls"))

    assert q.main() == 1
    assert "server-directed API retry window" in capsys.readouterr().out
    assert '"not_before":"2026-11-25T18:00:00Z"' in local_marker.read_text()


def test_restart_refresh_removes_marker_absent_from_current_master(tmp_path):
    local_marker = tmp_path / "event-checkout" / "api-backoff.json"
    local_marker.parent.mkdir(parents=True)
    local_marker.write_text(
        '{"schema":"que.api-backoff/v1",'
        '"not_before":"2026-11-25T18:00:00Z"}')

    status = refresh_backoff.refresh(
        tmp_path / "master" / "api-backoff.json", local_marker)

    assert "removed stale marker" in status
    assert not local_marker.exists()


def test_producer_workflows_refresh_master_marker_and_keep_ten_minute_cadence():
    collector = (q.ROOT / ".github/workflows/que-feed-collect.yml").read_text()
    kick = (q.ROOT / ".github/workflows/que-cadence-kick.yml").read_text()

    assert 'cron: "*/10 * * * *"' in collector
    for workflow in (collector, kick):
        assert "ref: master" in workflow
        assert "path: .que-backoff-master" in workflow
        assert "scripts/que/refresh_api_backoff.py" in workflow
        assert "ops/que/feeds/api-backoff.json" in workflow


def test_expired_persisted_backoff_is_removed(tmp_path):
    marker = tmp_path / "api-backoff.json"
    marker.write_text('{"not_before":"2026-11-25T17:22:33Z"}')
    later = INCIDENT_NOW + timedelta(seconds=1)
    assert q.active_api_backoff(later, marker) is None
    assert not marker.exists()


def test_api_failure_leaves_existing_feed_unchanged(monkeypatch, tmp_path):
    feeds = tmp_path / "feeds"
    feeds.mkdir()
    old_feed = feeds / "que-queue-feed.json"
    old_feed.write_text("existing successful snapshot\n")
    monkeypatch.setattr(q, "FEEDS", feeds)
    monkeypatch.setattr(q, "API_BACKOFF_FILE", tmp_path / "no-backoff.json")
    monkeypatch.setattr(q, "now", lambda: INCIDENT_NOW)
    monkeypatch.setattr(q, "load_tiers", lambda: {})
    monkeypatch.setattr(q, "API_STATS", _fresh_api_stats())
    monkeypatch.setenv("GH_TOKEN", "token")

    def fail(path, _token):
        raise q.ApiHttpError(path, 403, '{"message":"observed 403"}',
                             {"X-GitHub-Request-Id": "fixture-id"},
                             "not retried (403 is unclassified)")

    monkeypatch.setattr(q, "api", fail)
    assert q.main() == 1
    assert old_feed.read_text() == "existing successful snapshot\n"
    assert list(feeds.iterdir()) == [old_feed]


def test_rate_limit_preflight_is_separately_counted_from_core(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b'{"resources":{"core":{"limit":5000,"remaining":4999}}}'

    monkeypatch.setattr(q, "API_STATS", _fresh_api_stats())
    monkeypatch.setattr(q.urllib.request, "urlopen", lambda *_a, **_k: Response())
    snapshot = q.api("/rate_limit", "token")
    assert snapshot["resources"]["core"]["remaining"] == 4999
    stats = q.api_request_summary()
    assert stats["rate_limit_preflight_attempts"] == 1
    assert stats["rate_limit_preflight_successes"] == 1
    assert stats["core_attempts"] == 0
    assert stats["search_attempts"] == 0
    assert stats["max_before_retries_per_cycle"] == {
        "core": 31, "search": 2, "preflight": 1}
