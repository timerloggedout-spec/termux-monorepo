"""SiliconFlow has no currently documented working quota API; never call network."""
import datetime as dt
import pytest
from scripts import provider_quota_service as service
from scripts import provider_quota_transport as transport
from scripts import provider_quota_mapping as mapping
NOW = dt.datetime(2030, 4, 5, 12, tzinfo=dt.timezone.utc)
def test_disabled_service_never_calls_injected_transport_or_network(monkeypatch):
    def forbidden(**kwargs):
        pytest.fail("disabled SiliconFlow service must not call any transport")
    monkeypatch.setattr(service.http.client, "HTTPSConnection", forbidden)
    result = service.observe_service("siliconflow.balance", "synthetic-key",
        scope="user:primary", now=NOW, request=forbidden)
    assert result["status"] == "unknown"
    assert result["reason"] == "no_documented_working_api"
    assert result["signals"] == {} and result["source"] is None
    assert result["request_quota"] == result["entitlement"] == "unknown"
    assert service.SERVICES["siliconflow.balance"]["activation"] == "disabled_until_documented_working_api"
def test_retired_and_alternate_hosts_are_not_accepted():
    assert not hasattr(transport, "SILICONFLOW_BALANCE_URL")
    for url in ("https://api.siliconflow.com/v1/user/info",
                "https://api.siliconflow.cn/v1/user/info",
                "https://api.siliconflow.com/v1/chat/completions"):
        with pytest.raises(ValueError, match="fixed-source"):
            service.https_request(method="GET", url=url, headers={"Authorization": "Bearer synthetic"},
                timeout=5, allow_redirects=False, max_response_bytes=65536)
def test_historical_parser_capability_is_not_live_and_source_is_rejected():
    row = mapping.capability("siliconflow")
    assert row["status"] == "unsupported_live_source_historical_parser"
    assert row["parser_available"] is True
    assert row["remaining"] == "not_observed" and row["fail_closed"] is True
    result = mapping.observe_family("siliconflow",
        source="https://api.siliconflow.com/v1/user/info",
        observed_at="2030-04-05T12:00:00Z", now=NOW, scope="synthetic",
        metadata={"code": 20000, "status": True, "data": {"balance": "99"}})
    assert result["status"] == "unknown"
    assert result["reason"] == "no_documented_working_api"


def test_disabled_cli_returns_unknown_without_credentials_or_transport(monkeypatch, tmp_path, capsys):
    import json
    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    output = private / "siliconflow.json"
    monkeypatch.setattr(service, "https_request", lambda **kw: pytest.fail("no network"))
    original_get = service.os.environ.get
    def env_get(key, *args):
        assert key is not None and key != "SILICONFLOW_API_KEY"
        return original_get(key, *args)
    monkeypatch.setattr(service.os.environ, "get", env_get)
    assert service.main(["--service", "siliconflow.balance", "--scope", "synthetic",
                         "--observe", "--private-out", str(output)]) == 1
    result = json.loads(output.read_text())
    assert result["status"] == "unknown" and result["reason"] == "no_documented_working_api"
    public = json.loads(capsys.readouterr().out)
    assert public["status"] == "unknown" and "signals" not in public


def test_disabled_service_is_not_an_executable_reader():
    row = mapping.service_capability({"id": "siliconflow.balance"})
    assert row["reader"] is None
    assert row["status"] != "typed_reader"
