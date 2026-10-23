"""HTTP/SSE facade tests: real server on an ephemeral port, real HTTP."""
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from ops.web_adapter_foundry import facade  # noqa: E402
from ops.web_adapter_foundry.waf import load_registry  # noqa: E402

EXAMPLE = ROOT / "ops" / "web_adapter_foundry" / "examples" / "example.registry.json"


@pytest.fixture(scope="module")
def base():
    server = facade.make_server("127.0.0.1", 0, load_registry(str(EXAMPLE)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def call(base, path, payload=None, raw=None):
    data = raw if raw is not None else (
        json.dumps(payload).encode() if payload is not None else None)
    req = urllib.request.Request(base + path, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_health_and_info(base):
    status, body = call(base, "/health")
    assert status == 200 and body["ok"]
    assert "foundry.ping" in body["operations"]
    status, body = call(base, "/")
    assert status == 200 and "sse" in body["transports"]


def test_invoke_round_trip_and_builtin(base):
    status, body = call(base, "/invoke",
                        {"id": "1", "operation": "foundry.ping", "input": {}})
    assert status == 200 and body["ok"] and body["id"] == "1"
    assert body["data"]["pong"] is True
    status, body = call(base, "/invoke",
                        {"id": "2", "operation": "foundry.list_operations", "input": {}})
    assert status == 200 and body["ok"] and body["data"]["operations"]


def test_invoke_refuses_credential_bodies(base):
    # The core's credential-in-body refusal must hold on this transport too.
    status, body = call(base, "/invoke",
                        {"id": "3", "operation": "foundry.ping",
                         "input": {"note": "cookie: session=abc"}})
    assert status == 200 and body["ok"] is False
    assert body["error"]["code"] == "bad_envelope"


def test_bad_inputs(base):
    status, _ = call(base, "/invoke", raw=b"{not json")
    assert status == 400
    status, _ = call(base, "/nope")
    assert status == 404
    status, _ = call(base, "/invoke", raw=b"x" * (facade.MAX_BODY + 1))
    assert status == 413


def test_sse_fanout_receives_invoke(base):
    req = urllib.request.Request(base + "/events")
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert "text/event-stream" in resp.headers["Content-Type"]
        first = resp.readline()
        assert b"subscribed" in first
        status, _ = call(base, "/invoke",
                         {"id": "sse-1", "operation": "foundry.ping", "input": {}})
        assert status == 200
        seen = b""
        for _ in range(40):
            line = resp.readline()
            if not line:
                break
            seen += line
            if b'"id": "sse-1"' in seen or b'"id":"sse-1"' in seen:
                break
        assert b"event: invoke" in seen
        assert b"sse-1" in seen
