import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from scripts.services import firecrawl_public_research as service


class FakeResponse:
    def __init__(self, data):
        self.data = data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def read(self, size=-1):
        return self.data[:size]


class FakeOpener:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.calls = response, error, []
    def open(self, request, timeout):
        self.calls.append((request, timeout))
        if self.error:
            raise self.error
        return self.response


def payload(markdown="# Public data", code=200):
    return json.dumps({"success": True, "data": {"markdown": markdown, "metadata": {"statusCode": code}}}).encode()


def test_allowlist_endpoint_payload_and_keyless_headers(monkeypatch):
    opener = FakeOpener(FakeResponse(payload()))
    monkeypatch.setattr(service, "build_opener", lambda handler: opener)
    monkeypatch.setenv("FIRECRAWL_API_KEY", "DO_NOT_LEAK_FC_SECRET")
    monkeypatch.setenv("GH_TOKEN", "DO_NOT_LEAK_GH_SECRET")
    result = service.scrape("freellmapi")
    request, timeout = opener.calls[0]
    assert request.full_url == service.ENDPOINT == "https://api.firecrawl.dev/v2/scrape"
    assert request.get_header("Content-type") == "application/json"
    assert not any(k.lower() == "authorization" for k in request.headers)
    assert json.loads(request.data) == {"url": service.SOURCES["freellmapi"], "formats": ["markdown"], "onlyMainContent": True}
    assert set(service.SOURCES.values()) == {"https://github.com/mnfst/awesome-free-llm-apis", "https://github.com/tashfeenahmed/freellmapi"}
    assert timeout <= 60 and len(opener.calls) == 1
    assert result["status"] == "observed" and result["markdown"] == "# Public data"
    assert result["authentication"] == "none" and result["schema"] == "public-research-service/v1"


def test_bad_source_fails_without_request():
    with pytest.raises(KeyError):
        service.scrape("https://attacker.example")


@pytest.mark.parametrize("raw,reason", [
    (b"not json", "invalid_json"),
    (b"[]", "invalid_response_shape"),
    (b'{"success":true,"data":[]}', "invalid_response_shape"),
    (b'{"success":true,"data":{"markdown":"hi","metadata":{"statusCode":402}}}', "source_http_error"),
    (b'{"success":true,"data":{"markdown":"hi","metadata":{"statusCode":500}}}', "source_http_error"),
    (b'{"success":false,"error":"TOP_SECRET upstream response"}', "upstream_unsuccessful"),
    (b'{"success":true,"data":{"markdown":"  "}}', "empty_markdown"),
])
def test_invalid_or_unsuccessful_results_are_sanitized(monkeypatch, raw, reason):
    opener = FakeOpener(FakeResponse(raw))
    monkeypatch.setattr(service, "build_opener", lambda handler: opener)
    result = service.scrape("awesome-free-llm-apis")
    assert result["status"] == "unavailable" and result["reason"] == reason
    assert "markdown" not in result and "TOP_SECRET" not in json.dumps(result)
    assert len(opener.calls) == 1


@pytest.mark.parametrize("code,reason", [(429, "upstream_http_429"), (402, "upstream_http_402"), (307, "redirect_blocked")])
def test_http_errors_and_redirect_never_retry_or_reflect_body(monkeypatch, code, reason):
    secret = "UPSTREAM_SECRET"
    error = HTTPError(service.ENDPOINT, code, secret, {}, None)
    opener = FakeOpener(error=error)
    monkeypatch.setattr(service, "build_opener", lambda handler: opener)
    result = service.scrape("freellmapi")
    assert result["reason"] == reason and result["status"] == "unavailable"
    assert secret not in json.dumps(result) and len(opener.calls) == 1
    assert isinstance(opener.calls[0][0], __import__("urllib.request", fromlist=["Request"]).Request)


def test_redirect_handler_blocks_redirect():
    assert service._NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://elsewhere") is None


def test_response_cap(monkeypatch):
    opener = FakeOpener(FakeResponse(b"x" * (service.MAX_RESPONSE_BYTES + 1)))
    monkeypatch.setattr(service, "build_opener", lambda handler: opener)
    result = service.scrape("freellmapi")
    assert result["reason"] == "response_too_large"
    assert len(opener.calls) == 1


def test_atomic_output_and_cli_exit_status(monkeypatch, tmp_path):
    dest = tmp_path / "nested" / "result.json"
    monkeypatch.setattr(service, "scrape", lambda source: service._envelope(source, "observed", "ok", "markdown"))
    assert service.main(["--source", "freellmapi", "--output", str(dest)]) == 0
    assert json.loads(dest.read_text())["markdown"] == "markdown"
    assert list(dest.parent.iterdir()) == [dest]
    monkeypatch.setattr(service, "scrape", lambda source: service._envelope(source, "unavailable", "network_error"))
    assert service.main(["--source", "freellmapi", "--output", str(dest)]) == 1
    assert json.loads(dest.read_text())["status"] == "unavailable"


def test_cli_invalid_source_exit_2(tmp_path):
    script = Path(service.__file__)
    result = subprocess.run([sys.executable, str(script), "--source", "https://evil", "--output", str(tmp_path / "x")], capture_output=True, text=True)
    assert result.returncode == 2 and not (tmp_path / "x").exists()
