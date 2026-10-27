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


def _fake_dns(monkeypatch, mapping):
    import socket as socket_mod

    def fake(host, port, *a, **k):
        ip = mapping[host]
        return [(socket_mod.AF_INET, socket_mod.SOCK_STREAM, 6, "", (ip, 0))]

    monkeypatch.setattr(socket_mod, "getaddrinfo", fake)


def test_fetch_url_barrier_chain(monkeypatch):
    from ops.web_adapter_foundry import waf
    _fake_dns(monkeypatch, {"ok.example": "93.184.216.34",
                            "sneaky.example": "10.0.0.5"})
    allow = ["ok.example", "sneaky.example"]
    assert waf._validate_fetch_url("https://ok.example/x", allow) is None
    assert "not in allowlist" in waf._validate_fetch_url("https://other.example/x", allow)
    assert "non-public" in waf._validate_fetch_url("https://sneaky.example/x", allow)
    assert "scheme" in waf._validate_fetch_url("file:///etc/passwd", allow)
    assert waf._validate_fetch_url(None, allow)


def test_redirect_hop_revalidated(monkeypatch):
    import urllib.error
    import urllib.request as urlreq

    from ops.web_adapter_foundry import waf
    _fake_dns(monkeypatch, {"ok.example": "93.184.216.34"})
    handler = waf._AllowlistRedirectHandler(["ok.example"])
    req = urlreq.Request("http://ok.example/start")
    with pytest.raises(urllib.error.URLError):
        handler.redirect_request(req, None, 302, "Found", {}, "http://169.254.169.254/latest")
    with pytest.raises(urllib.error.URLError):
        handler.redirect_request(req, None, 302, "Found", {}, "http://not-allowed.example/")


def test_direct_http_url_prefix_barrier(monkeypatch):
    from ops.web_adapter_foundry import waf
    _fake_dns(monkeypatch, {"ok.example": "93.184.216.34"})
    op = {"operation_id": "docs.get", "side_effect": "read", "status": "verified",
          "executor": "direct-http", "allowlist": ["ok.example"],
          "url_prefixes": ["https://ok.example/docs/"]}
    reg = {"provider": "t", "operations": [op]}
    out = waf.handle_request({"id": "p1", "operation": "docs.get",
                              "input": {"url": "https://ok.example/admin"}}, reg)
    assert not out["ok"] and out["error"]["code"] == "not_allowlisted"
    assert "url_prefix" in out["error"]["message"]
    # Stub the opener so NO real network happens: reaching the stub proves
    # the request passed every barrier and arrived at the network step.
    import urllib.error
    import urllib.request as urlreq

    class _StubOpener:
        def open(self, request, timeout=None):
            raise urllib.error.URLError("offline-stub")

    monkeypatch.setattr(urlreq, "build_opener", lambda *a, **k: _StubOpener())
    out = waf.handle_request({"id": "p2", "operation": "docs.get",
                              "input": {"url": "https://ok.example/docs/x"}},
                             reg)
    assert not out["ok"] and out["error"]["code"] == "upstream"
    assert "offline-stub" in out["error"]["message"]


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


def test_http_surface_submission_matches_direct_plan(base):
    """The canonical template filed over HTTP /invoke produces the identical
    plan as the same brief planned directly (CLI/JSON surface) — one
    validator, many renderings."""
    from ops.web_adapter_foundry import waf
    brief = json.loads((ROOT / "ops" / "web_adapter_foundry" / "examples"
                        / "target-brief.example.json").read_text())
    status, resp = call(base, "/invoke", {"id": "sub1", "operation": "foundry.intake",
                                          "input": {"brief": brief}})
    assert status == 200 and resp["ok"] is True
    assert resp["data"] == waf.plan_from_brief(brief, waf.load_taxonomy())
    assert resp["data"]["submitter"] == "inventory{atlas}"
    bad = dict(brief, surfaces=["smoke-signal"])
    status, resp = call(base, "/invoke", {"id": "sub2", "operation": "foundry.intake",
                                          "input": {"brief": bad}})
    assert resp["ok"] is False and "surfaces" in resp["error"]["message"]
