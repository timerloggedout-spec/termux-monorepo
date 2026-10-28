"""Fetch defer-discipline tests: a shared-token 403 is a defer, not a failure."""
import importlib.util
import io
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ledger_fetch", ROOT / "scripts" / "delphi" / "ledger_fetch.py")
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)


def http403(req, **kw):
    raise urllib.error.HTTPError(req.full_url, 403, "Forbidden",
                                 {}, io.BytesIO(b"rate limit exceeded"))


def test_defer_after_retries(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch.urllib.request, "urlopen", http403)
    monkeypatch.setattr(fetch.time, "sleep", lambda s: None)
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    old = sys.argv
    sys.argv = ["ledger_fetch.py", "--cache", str(tmp_path / "c"), "--repo", "o/r"]
    try:
        rc = fetch.main()
    finally:
        sys.argv = old
    assert rc == 0  # deferred, not failed
    assert not (tmp_path / "c" / "issues.json").exists()  # no partial cache


def test_non_rate_error_propagates(monkeypatch):
    def http404(req, **kw):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found",
                                     {}, io.BytesIO(b"nope"))
    monkeypatch.setattr(fetch.urllib.request, "urlopen", http404)
    monkeypatch.setattr(fetch.time, "sleep", lambda s: None)
    try:
        fetch.get("x", "https://api.github.com/repos/o/r/issues/1")
        raise AssertionError("404 must propagate")
    except urllib.error.HTTPError as e:
        assert e.code == 404
