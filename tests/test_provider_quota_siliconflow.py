"""Synthetic-only private monetary observation contracts; no account calls."""
import datetime as dt
import json
from types import SimpleNamespace

import pytest

from scripts import provider_quota_service as service
from scripts.provider_quota_transport import observe_siliconflow_balance, SILICONFLOW_BALANCE_URL

NOW = dt.datetime(2030, 4, 5, 12, tzinfo=dt.timezone.utc)


def payload(**changes):
    return {"code": 20000, "status": True, "data": {
        "id": "private-user-sentinel", "email": "private-email-sentinel",
        "balance": "0.88", "chargeBalance": "88.00", "totalBalance": "88.88",
        **changes,
    }}


def run(body, status=200):
    calls = []
    def request(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(status_code=status, json=lambda: body)
    result = service.observe_service("siliconflow.balance", "synthetic-key", scope="user:primary",
                                     now=NOW, request=request)
    return result, calls


def test_private_balance_is_not_request_quota_or_entitlement():
    result, calls = run(payload())
    assert calls[0]["url"] == SILICONFLOW_BALANCE_URL
    assert calls[0]["method"] == "GET" and calls[0]["allow_redirects"] is False
    assert calls[0]["max_response_bytes"] == 65536
    assert result["status"] == "observed"
    assert result["signals"] == {"monetary_balance": "0.88", "monetary_charge_balance": "88.00",
                                 "monetary_total_balance": "88.88"}
    assert result["request_quota"] == result["entitlement"] == result["reset"] == result["currency"] == "unknown"
    assert result["runtime_admission"] == "unchanged"
    assert result["valid_until"] == "2030-04-05T12:01:00Z"
    encoded = json.dumps(result)
    assert "private-user-sentinel" not in encoded and "private-email-sentinel" not in encoded
    public = service.public_status(result)
    assert set(public) == {"service_id", "provider_family", "status", "observed_at"}
    assert "88.88" not in json.dumps(public) and "user:primary" not in json.dumps(public)


@pytest.mark.parametrize("body,status", [
    ({"code": 20000, "status": False, "data": {}}, 200),
    ({"code": True, "status": True, "data": {}}, 200),
    ({"code": 20000, "status": True, "data": []}, 200),
    (payload(balance="NaN"), 200), (payload(balance=-1), 200),
    (payload(balance=True), 200), (payload(balance="-1"), 200),
    (payload(), 401), (payload(), 429), (payload(), 302),
])
def test_invalid_and_error_responses_fail_closed(body, status):
    result, _ = run(body, status)
    assert result["status"] == "unknown" and result["signals"] == {}
    assert result["request_quota"] == "unknown"


@pytest.mark.parametrize("key", ["", "bad\nkey", "x" * 4097, None])
def test_missing_or_malformed_credential_never_calls_transport(key):
    def forbidden(**kwargs):
        pytest.fail("transport must not run")
    result = observe_siliconflow_balance(key, forbidden, observed_at=NOW.isoformat(), scope="user:primary")
    assert result["status"] == "unknown"


def test_regional_fallback_and_inference_are_not_fixed_sources():
    for url in ("https://api.siliconflow.cn/v1/user/info", "https://api.siliconflow.com/v1/chat/completions"):
        with pytest.raises(ValueError, match="fixed-source"):
            service.https_request(method="GET", url=url, headers={"Authorization": "Bearer synthetic"},
                                  timeout=5, allow_redirects=False, max_response_bytes=65536)
