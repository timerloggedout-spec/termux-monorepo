import datetime as dt
import io
import json
import os
import subprocess
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.ops.provider_free_diagnostics as diag


class Headers(dict):
    pass


def http_error(body, headers=None, code=429):
    return urllib.error.HTTPError("https://invalid", code, "secret reason", Headers(headers or {}), io.BytesIO(body))


def test_generic_429_is_unknown_and_never_safe():
    exc = http_error(json.dumps({"error": {"code": "rate_limit_exceeded", "message": "secret detail"}}).encode())
    result = diag.classify_http_error(exc)
    assert result["category"] == "unknown_429"
    assert result["retry_safe"] is False
    assert "secret" not in repr(result)


def test_daily_and_upstream_classifications_are_enum_only():
    daily = http_error(json.dumps({"error": {"message": "daily request limit", "metadata": {"limit_source": "free-models-per-day"}}}).encode())
    assert diag.classify_http_error(daily)["category"] == "account_daily_request_limit"
    token = http_error(json.dumps({"error": {"message": "free-models-per-day-tokens quota exceeded"}}).encode())
    assert diag.classify_http_error(token)["category"] == "account_daily_token_limit"
    upstream = http_error(json.dumps({"error": {"message": "temporarily rate-limited due to capacity", "metadata": {"provider_name": "SECRET_PROVIDER", "provider_code": "SECRET_CODE"}}}).encode())
    result = diag.classify_http_error(upstream)
    assert result["category"] == "upstream_capacity"
    assert "SECRET" not in repr(result)


def test_headers_case_insensitive_with_plain_dict():
    result = diag.classify_http_error(http_error(b"{}", {"retry-after": "3", "X-RateLimit-Reset": "not-a-date"}))
    assert result["retry_after_present"] is True
    assert result["rate_limit_reset_present"] is True
    assert result["rate_limit_reset_state"] == "unknown"


def test_malformed_and_oversized_bodies_are_unknown():
    for body in (b"not json", b"{" + b" " * (diag.MAX_BYTES + 1)):
        result = diag.classify_http_error(http_error(body))
        assert result["category"] == "unknown_429"
        assert result["retry_safe"] is False


def test_account_quota_fields_are_sanitized_and_read_only(monkeypatch):
    calls = []
    def request(path, token):
        calls.append(path)
        assert token == "secret-token"
        return {"data": {"is_free_tier": True,
                         "free_model_daily_requests": {"used": 3, "limit": 10, "remaining": 0,
                                                        "resets_at": "2025-01-01T00:00:00Z"},
                         "limit_remaining": 999, "account_id": "secret-id"}}
    monkeypatch.setattr(diag.smoke, "request", request)
    report = diag.build_report("secret-token")
    assert calls == ["/key"]
    assert report["free_account_verified"] is True
    assert report["daily_quota_present"] is True
    assert report["daily_quota_valid"] is True
    assert report["daily_quota_exhausted"] is True
    assert report["reset_state"] == "elapsed"
    assert report["rate_limit_metadata_present"] is False
    assert report["inference_attempted"] is False and report["completion_requests"] == 0
    assert report["production_admission_changed"] is False and report["paid_fallback_allowed"] is False
    assert report["inference_retry_authorized"] is False
    assert not any(secret in repr(report) for secret in ("secret-token", "secret-id", "999", "2025"))


def test_invalid_quota_remaining_is_not_safe(monkeypatch):
    for remaining in (float("nan"), float("inf"), -1, "bad", True):
        monkeypatch.setattr(diag.smoke, "request", lambda *args, r=remaining: {"data": {"free_model_daily_requests": {"remaining": r}}})
        report = diag.diagnose_account("x")
        assert report["daily_quota_valid"] is False
        assert report["daily_quota_exhausted"] is False


def test_missing_quota_and_generic_rate_limit_unknown(monkeypatch):
    monkeypatch.setattr(diag.smoke, "request", lambda *args: {"data": {"is_free_tier": False}})
    report = diag.diagnose_account("x")
    assert report["daily_quota_present"] is False
    assert report["reset_state"] == "unknown"
    body = json.dumps({"error": {"message": "rate_limit_exceeded", "metadata": {"provider_name": "p", "provider_code": "rate_limit"}}}).encode()
    assert diag.classify_http_error(http_error(body))["category"] == "unknown_429"


def test_reset_states():
    now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    assert diag._reset_state("2025-01-02T00:00:00Z", now) == "pending"
    assert diag._reset_state("bad", now) == "unknown"


def test_module_cli_missing_credential_no_network(tmp_path):
    output = tmp_path / "module.json"
    env = dict(os.environ)
    env.pop("OPENROUTER_API_KEY", None)
    proc = subprocess.run([sys.executable, "-m", "scripts.ops.provider_free_diagnostics", "--output", str(output)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=10)
    assert proc.returncode == 0, proc.stderr
    assert json.loads(output.read_text())["account_read_status"] == "missing_credential"


def test_direct_script_cli_missing_credential_no_network(tmp_path):
    output = tmp_path / "direct.json"
    env = dict(os.environ)
    env.pop("OPENROUTER_API_KEY", None)
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/ops/provider_free_diagnostics.py"), "--output", str(output)], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=10)
    assert proc.returncode == 0, proc.stderr
    assert json.loads(output.read_text())["account_read_status"] == "missing_credential"
