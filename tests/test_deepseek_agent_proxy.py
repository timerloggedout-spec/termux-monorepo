import json
import socket
from urllib.error import HTTPError, URLError
from unittest.mock import patch

import pytest

from scripts import deepseek_agent_proxy as proxy


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self.body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit=-1):
        return self.body


def test_preflight_is_authenticated_read_only_api_check():
    response = FakeResponse(200, {"jobs": []})
    with patch.object(proxy.socket, "getaddrinfo", return_value=[("address",)]), patch.object(
        proxy, "urlopen", return_value=response
    ) as open_url:
        assert proxy.check_proxy("https://origin.example", "token") == (True, "available")
    request = open_url.call_args.args[0]
    assert request.full_url == "https://origin.example/v1/agent/list"
    assert request.get_header("Authorization") == "Bearer token"
    assert request.get_method() == "GET"


def test_missing_or_unresolved_proxy_skips_without_requesting_an_agent():
    with patch.object(proxy, "urlopen") as open_url:
        result = proxy.run_agent(None, "token", {"task": "test"})
    assert result["skipped"] is True
    assert result["reason"] == "proxy-url-unset"
    open_url.assert_not_called()

    with patch.object(proxy.socket, "getaddrinfo", side_effect=socket.gaierror("not found")), patch.object(
        proxy, "urlopen"
    ) as open_url:
        result = proxy.run_agent("https://origin.example", "token", {"task": "test"})
    assert result["skipped"] is True
    assert result["reason"] == "proxy-dns-unresolved"
    open_url.assert_not_called()


def test_run_uses_start_and_status_contract_only():
    responses = [
        FakeResponse(200, {"jobs": []}),
        FakeResponse(202, {"invocation_id": "abc123", "phase": "running"}),
        FakeResponse(200, {"invocation_id": "abc123", "phase": "done", "rc": 0, "tail": ["finished"]}),
    ]
    payload = {"task": "test task", "source": "github:test", "context": {"repo": "example/repo"}}
    with patch.object(proxy.socket, "getaddrinfo", return_value=[("address",)]), patch.object(
        proxy, "urlopen", side_effect=responses
    ) as open_url, patch.object(proxy.time, "sleep"):
        result = proxy.run_agent("https://origin.example", "token", payload, max_polls=2, poll_interval=0)

    assert result["skipped"] is False
    assert result["start"] == {"invocation_id": "abc123", "phase": "running"}
    assert result["status"]["phase"] == "done"
    requests = [call.args[0] for call in open_url.call_args_list]
    assert [request.full_url for request in requests] == [
        "https://origin.example/v1/agent/list",
        "https://origin.example/v1/agent",
        "https://origin.example/v1/agent/status/abc123",
    ]
    assert all(request.get_header("Authorization") == "Bearer token" for request in requests)
    assert json.loads(requests[1].data)["task"] == "test task"


def test_unavailable_proxy_is_a_skip_but_authentication_errors_are_failures():
    with patch.object(proxy.socket, "getaddrinfo", return_value=[("address",)]), patch.object(
        proxy, "urlopen", side_effect=URLError(ConnectionRefusedError("offline"))
    ):
        assert proxy.check_proxy("https://origin.example", "token") == (False, "proxy-unreachable")

    unauthorized = HTTPError("https://origin.example/v1/agent/list", 401, "unauthorized", {}, None)
    with patch.object(proxy.socket, "getaddrinfo", return_value=[("address",)]), patch.object(
        proxy, "urlopen", side_effect=unauthorized
    ):
        with pytest.raises(proxy.ProxyContractError, match="proxy-http-401"):
            proxy.check_proxy("https://origin.example", "token")


def test_unavailable_proxy_after_start_marks_the_route_skipped():
    responses = [
        FakeResponse(200, {"jobs": []}),
        FakeResponse(202, {"invocation_id": "abc123", "phase": "running"}),
    ]
    responses.append(URLError(ConnectionResetError("tunnel lost")))
    with patch.object(proxy.socket, "getaddrinfo", return_value=[("address",)]), patch.object(
        proxy, "urlopen", side_effect=responses
    ):
        result = proxy.run_agent("https://origin.example", "token", {"task": "test"}, max_polls=1)
    assert result["skipped"] is True
    assert result["reason"] == "proxy-lost"
    assert result["status"]["invocation_id"] == "abc123"


def test_workflow_triggers_remain_and_deepseek_ci_uses_proxy_only():
    workflow = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "deepseek-ci.yml"
    ).read_text(encoding="utf-8")
    for trigger in (
        "  pull_request:",
        "  issue_comment:",
        "  pull_request_review_comment:",
        "  workflow_dispatch:",
    ):
        assert trigger in workflow
    assert "secrets.DEEPSEEK_AGENT_URL" in workflow
    assert "secrets.DEEPSEEK_AGENT_TOKEN" in workflow
    assert "needs.proxy-preflight.outputs.available == 'true'" in workflow
    assert "deepcli.ci_mode" not in workflow
    assert "DEEPSEEK_API_KEY" not in workflow
