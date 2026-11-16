"""Retry + ::error:: surfacing for the two feed collectors.

2026-10-29 burst: both collectors died on the first 403 (shared rate
bucket exhausted by a workflow_run storm) and the traceback reached
only the job log (not API-readable), surfacing as bare exit-1
annotations. These tests pin: transient HTTP errors are retried, and
a final failure prints a ::error:: annotation naming status+message.
"""
import io
import json
import sys
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "delphi"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "reviewer_metrics"))

import rfp_flood_fetch  # noqa: E402
import collect as reviewer_collect  # noqa: E402


def _http_error(code, message):
    body = json.dumps({"message": message}).encode()
    return urllib.error.HTTPError(
        "https://api.github.com/x", code, "err", {}, io.BytesIO(body))


class _Resp:
    def __init__(self, payload):
        self._b = json.dumps(payload).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_fetch_retries_transient_then_succeeds():
    with mock.patch.object(rfp_flood_fetch.time, "sleep", lambda s: None), \
         mock.patch("urllib.request.urlopen",
                    side_effect=[_http_error(403, "API rate limit exceeded"),
                                 _Resp([1, 2])]) as m:
        assert rfp_flood_fetch.get("t", "https://api.github.com/x") == [1, 2]
        assert m.call_count == 2


def test_fetch_final_failure_emits_error_annotation(capsys):
    with mock.patch.object(rfp_flood_fetch.time, "sleep", lambda s: None), \
         mock.patch("urllib.request.urlopen",
                    side_effect=[_http_error(403, "API rate limit exceeded")] * 4):
        try:
            rfp_flood_fetch.get("t", "https://api.github.com/x")
            raise AssertionError("should have raised")
        except urllib.error.HTTPError:
            pass
    out = capsys.readouterr().out
    assert "::error::rfp fetch failed status=403" in out
    assert "API rate limit exceeded" in out


def test_reviewer_get_retries_and_surfaces():
    client = reviewer_collect.ApiClient("o/r", "t")
    with mock.patch.object(reviewer_collect.time, "sleep", lambda s: None), \
         mock.patch("urllib.request.urlopen",
                    side_effect=[_http_error(429, "secondary rate limit"),
                                 _Resp({"ok": True})]) as m:
        assert client.get("/pulls") == {"ok": True}
        assert m.call_count == 2


def test_reviewer_get_non_transient_not_retried():
    client = reviewer_collect.ApiClient("o/r", "t")
    with mock.patch.object(reviewer_collect.time, "sleep", lambda s: None), \
         mock.patch("urllib.request.urlopen",
                    side_effect=[_http_error(404, "Not Found")] * 4) as m:
        try:
            client.get("/pulls/1")
            raise AssertionError("should have raised")
        except urllib.error.HTTPError:
            pass
        assert m.call_count == 1
