"""Branch (a) surface live-mode wiring (staging): live.py client
contract + the web mirror's static contract + TUI hooks.

The transport is faked throughout -- no test makes a network
call. What is asserted is the fail-closed semantics: a live
receipt passes through verbatim; ANY transport-class failure
becomes the surface-local offline-gate receipt, never a dressed-
up live one."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import live  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

LIVE_RECEIPT = {
    "execution_class": "live-production",
    "deployment": True,
    "model": {"provider": "amazon-bedrock",
              "model_id": "us.amazon.nova-lite-v1:0",
              "sdk_version": "strands-agents 1.63.0"},
    "plan": {"weeks": []},
}


class FakeOpener:
    def __init__(self, result=None, exc=None):
        self.result = result
        self.exc = exc
        self.calls = []

    def __call__(self, method, url, body, timeout):
        self.calls.append((method, url, body))
        if self.exc:
            raise self.exc
        return self.result


def _on(monkeypatch):
    monkeypatch.setenv("STRANDS_LIVE", "1")


def test_endpoint_is_the_host_b_contract_url():
    assert live.ENDPOINT == ("https://hostb-live-5b9d7"
                             ".containers.snapdeploy.app")


def test_live_mode_is_opt_in(monkeypatch):
    monkeypatch.delenv("STRANDS_LIVE", raising=False)
    assert live.enabled() is False
    opener = FakeOpener(result=(200, b"{}"))
    receipt = live.plan(opener=opener)
    assert opener.calls == []          # nothing was called
    assert receipt["execution_class"] == "offline-gate"
    assert receipt["fail_closed"] is True
    assert receipt["deployment"] is False


def test_plan_passes_a_live_receipt_through_verbatim(monkeypatch):
    _on(monkeypatch)
    opener = FakeOpener(
        result=(200, json.dumps(LIVE_RECEIPT).encode()))
    receipt = live.plan(opener=opener)
    assert receipt == LIVE_RECEIPT
    method, url, body = opener.calls[0]
    assert method == "POST" and url.endswith("/plan")
    assert body == {"syllabus_ref": "examples/syllabus.json"}


def test_plan_transport_failure_falls_closed(monkeypatch):
    _on(monkeypatch)
    opener = FakeOpener(exc=TimeoutError("read timed out"))
    receipt = live.plan(opener=opener)
    assert receipt["execution_class"] == "offline-gate"
    assert receipt["fail_closed"] is True
    assert receipt["deployment"] is False
    assert receipt["model"] is None
    assert receipt["source"] == "surface-local"
    assert "TimeoutError" in receipt["error"]


def test_plan_platform_5xx_falls_closed(monkeypatch):
    _on(monkeypatch)
    opener = FakeOpener(result=(503, b"platform"))
    receipt = live.plan(opener=opener)
    assert receipt["fail_closed"] is True
    assert receipt["source"] == "surface-local"


def test_plan_malformed_body_falls_closed(monkeypatch):
    _on(monkeypatch)
    opener = FakeOpener(result=(200, b'{"no_class": true}'))
    receipt = live.plan(opener=opener)
    assert receipt["fail_closed"] is True


def test_health_and_wake(monkeypatch):
    _on(monkeypatch)
    ok = FakeOpener(result=(200, json.dumps(
        {"status": "ok", "strands_agent_available": True,
         "deployment": True, "model_id": "us.amazon.nova-lite-v1:0"}
    ).encode()))
    assert live.health(opener=ok)["deployment"] is True
    assert live.wake(opener=ok)["awake"] is True
    down = FakeOpener(exc=OSError("connection refused"))
    w = live.wake(opener=down)
    assert w["awake"] is False and "OSError" in w["error"]


def test_web_mirror_contract():
    js = (ROOT / "web" / "live.js").read_text()
    for needle in ("hostb-live-5b9d7.containers.snapdeploy.app",
                   '"/plan"', '"/health"', "offline-gate",
                   "fail_closed", "ss.live_mode", "surface-local"):
        assert needle in js, needle
    index = (ROOT / "web" / "index.html").read_text()
    assert index.index("live.js") < index.index("app.js")
    sw = (ROOT / "web" / "sw.js").read_text()
    assert '"live.js"' in sw
    if shutil.which("node"):
        subprocess.run(["node", "--check", str(ROOT / "web" / "live.js")],
                       check=True)


def test_tui_hooks_present():
    tui = (ROOT / "tui.py").read_text()
    for needle in ('id="live-plan"', 'id="live-receipt"',
                   "STRANDS_LIVE=1", "_live_receipt_text",
                   "_live_wake"):
        assert needle in tui, needle


def test_no_live_call_sites_outside_the_clients():
    # The endpoint may only be named by the two client modules;
    # no other surface file may grow its own call path.
    for path in ROOT.rglob("*"):
        if path.suffix not in (".py", ".js", ".html"):
            continue
        if "evidence" in path.parts or "tests" in path.parts:
            continue
        if path.name in ("live.py", "live.js"):
            continue
        assert "containers.snapdeploy.app" not in \
            path.read_text(errors="ignore"), path
