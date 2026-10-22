"""Optional end-to-end tests for the swarms-rs worker through the real hub.

Set SWARMS_RS_TEST_BINARY to an already-built worker executable to enable these;
tests deliberately never invoke Cargo or contact a live inference provider.
"""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time

import pytest
import uvicorn
from hub_quota_fixture import seed_quota
from src import telemetry


ROOT = Path(__file__).resolve().parents[1]
BINARY = os.environ.get("SWARMS_RS_TEST_BINARY")
pytestmark = pytest.mark.skipif(not BINARY, reason="set SWARMS_RS_TEST_BINARY to a prebuilt worker")


@pytest.fixture
def live_hub(monkeypatch, tmp_path):
    """Serve the actual app on loopback, with every inference route stubbed/blocked."""
    monkeypatch.syspath_prepend(str(ROOT))
    hub = importlib.import_module("llm_api_hub.server.app")
    monkeypatch.setattr(hub, "admission", seed_quota(tmp_path / "quota.json", ["wrapper/deepseek"]))
    destination = str(tmp_path / "telemetry.jsonl")
    monkeypatch.setenv("TERMUX_TELEMETRY_LOG", destination)
    monkeypatch.setitem(telemetry.TermuxTelemetryLogger.notify.__globals__, "TELEMETRY_LOG", destination)
    calls: list[dict] = []
    requests: list[str] = []

    def complete(provider, request):
        assert provider == "deepseek"
        body = request.model_dump() if hasattr(request, "model_dump") else dict(request)
        calls.append(body)
        return f"fixture-response-{len(calls)}"

    def forbidden(*args, **kwargs):
        raise AssertionError("live inference is forbidden in this test")

    monkeypatch.setattr(hub.runtime, "complete_wrapper", complete)
    monkeypatch.setattr(hub.runtime, "complete_upstream", forbidden)
    monkeypatch.setattr(hub.runtime, "_get_dispatcher", forbidden)
    monkeypatch.setattr(hub.research_providers, "complete", forbidden)

    async def recorder(scope, receive, send):
        if scope.get("type") == "http" and scope.get("path") == "/v1/chat/completions":
            requests.append(scope["path"])
        await hub.app(scope, receive, send)

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    monkeypatch.setenv("LLM_API_HUB_KEY", "fixture-key")
    server = uvicorn.Server(uvicorn.Config(recorder, log_level="critical", lifespan="off"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 5
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert server.started, "hub did not start"
        yield f"http://127.0.0.1:{port}/v1/", calls, requests
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()
        assert not thread.is_alive(), "hub server thread did not stop"


def _load_adapter():
    path = ROOT / "src" / "swarms_rust_adapter.py"
    spec = importlib.util.spec_from_file_location("swarms_rust_adapter_test", path)
    assert spec and spec.loader, f"adapter not found: {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _run(monkeypatch, tmp_path, base_url, task, *, agents=1, passes=1, key="fixture-key", timeout=30):
    adapter = _load_adapter()
    monkeypatch.setenv("LLM_API_HUB_BASE", base_url)
    monkeypatch.setenv("LLM_API_HUB_KEY", key)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    config = {"task": task, "model": "wrapper/deepseek", "max_loops": passes,
              "number_agents": agents, "execute": True}
    return adapter.run(config, binary=BINARY, timeout_seconds=timeout, max_tokens=32)


def _assert_hub_contract(calls):
    assert calls
    for body in calls:
        assert body["model"] == "wrapper/deepseek"
        assert body["stream"] is False
        assert not body.get("tools")
        assert body["max_tokens"] == 32
        assert any(message.get("role") == "system" for message in body["messages"])


def _assert_clean_workspace(parent):
    assert not list(parent.glob("termux-swarms-rs-*"))


def test_single_agent_calls_real_hub_and_preserves_conversation(monkeypatch, tmp_path, live_hub):
    base, calls, requests = live_hub
    result = _run(monkeypatch, tmp_path, base, "fixture-input")
    assert result["status"] == "complete"
    assert result["backend"] == "swarms-rs"
    assert "fixture-input" in str(result["output"])
    assert "fixture-response-1" in str(result["output"])
    assert isinstance(result["passes"], list)
    assert len(requests) == len(calls) == 1
    assert "fixture-input" in json.dumps(calls[0]["messages"])
    _assert_hub_contract(calls)
    _assert_clean_workspace(tmp_path)


def test_two_agents_handoff_uses_prior_response(monkeypatch, tmp_path, live_hub):
    base, calls, requests = live_hub
    result = _run(monkeypatch, tmp_path, base, "fixture-input", agents=2)
    assert result["status"] == "complete"
    assert len(requests) == len(calls) == 2
    assert "fixture-input" in json.dumps(calls[0]["messages"])
    assert "fixture-response-1" in json.dumps(calls[1]["messages"])
    _assert_hub_contract(calls)
    _assert_clean_workspace(tmp_path)


def test_one_agent_two_passes_repeat_with_prior_result(monkeypatch, tmp_path, live_hub):
    base, calls, requests = live_hub
    result = _run(monkeypatch, tmp_path, base, "fixture-input", agents=1, passes=2)
    assert result["status"] == "complete"
    assert len(requests) == len(calls) == 2
    assert "fixture-response-1" in json.dumps(calls[1]["messages"])
    _assert_hub_contract(calls)
    _assert_clean_workspace(tmp_path)


def test_bad_hub_auth_fails_without_inference_or_workspace_leak(monkeypatch, tmp_path, live_hub):
    base, calls, requests = live_hub
    # The in-process hub reads os.environ per request. Override only the child
    # environment; changing the parent's key would change the expected key too.
    original_run = subprocess.run
    def wrong_child_key(*args, **kwargs):
        kwargs["env"] = {**kwargs["env"], "LLM_API_HUB_KEY": "wrong-fixture-key"}
        return original_run(*args, **kwargs)
    monkeypatch.setattr(subprocess, "run", wrong_child_key)
    with pytest.raises(RuntimeError) as error:
        _run(monkeypatch, tmp_path, base, "fixture-input")
    # Do not constrain upstream error wording; ensure no credential-bearing details escape.
    assert "wrong-fixture-key" not in str(error.value)
    assert len(requests) == 1 and calls == []
    _assert_clean_workspace(tmp_path)


def test_slow_stub_deadline_cancels_worker_and_cleans_workspace(monkeypatch, tmp_path, live_hub):
    base, calls, requests = live_hub
    # A very short adapter deadline bounds the subprocess even when inference is slow.
    hub = importlib.import_module("llm_api_hub.server.app")
    entered = threading.Event()

    def slow(provider, request):
        entered.set()
        time.sleep(2)
        calls.append(request.model_dump())
        return "late-fixture-response"

    monkeypatch.setattr(hub.runtime, "complete_wrapper", slow)
    with pytest.raises((TimeoutError, RuntimeError, subprocess.TimeoutExpired)):
        _run(monkeypatch, tmp_path, base, "fixture-input", timeout=1)
    assert entered.wait(timeout=2)
    _assert_clean_workspace(tmp_path)


def test_cli_keeps_json_stdout_and_diagnostics_stderr(monkeypatch, tmp_path, live_hub):
    base, calls, requests = live_hub
    cli = ROOT / "scripts" / "swarms" / "run-rust.py"
    monkeypatch.setenv("LLM_API_HUB_BASE", base)
    monkeypatch.setenv("LLM_API_HUB_KEY", "fixture-key")
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    proc = subprocess.run([sys.executable, str(cli), "--task", "fixture-input",
                           "--model", "wrapper/deepseek", "--number-agents", "2",
                           "--max-tokens", "32", "--binary", BINARY, "--execute"],
                          cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["status"] == "complete"
    assert "fixture-response-2" in proc.stdout
    assert len(requests) == len(calls) == 2
    _assert_hub_contract(calls)
    _assert_clean_workspace(tmp_path)
