"""Contract tests for the host-B endpoint (issue #4965).

Pins apps/studysprint/tools/hostb-endpoint/app.py to the
strands-aws contract of record (endpoint.schema.json +
receipt.schema.json):

  * GET /health validates against the HealthResponse schema.
  * POST /plan ALWAYS returns a receipt (HTTP 200): live path
    (faked transport) = live-production + deployment=true +
    Bedrock model block + tool_trace; forced failure =
    offline-gate + fail_closed + the exact error; NO 5xx shape.
  * GET /receipt/{id} is byte-identical to the invocation's
    response; an unknown id is the endpoint's only 404.
  * The retired fit-test routes (/model, /wake, /) are absent.
  * The vendored core copies in the endpoint directory are
    byte-identical to the canonical apps/studysprint files
    (drift guard; skipped when the canonical tree is absent).

Hermetic: no network, no AWS credentials, no live model. The
live transport is faked at the app's _invoke_live_agent seam.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

ENDPOINT_DIR = Path(__file__).resolve().parents[1]
STUDYSPRINT_ROOT = Path(__file__).resolve().parents[4]
SCHEMAS_DIR = STUDYSPRINT_ROOT / "strands-aws" / "schemas"

os.environ.setdefault("STRANDS_MODEL_ID", "us.amazon.nova-lite-v1:0")
os.environ.pop("AWS_ACCESS_KEY_ID", None)
os.environ.pop("AWS_SECRET_ACCESS_KEY", None)

_spec = importlib.util.spec_from_file_location(
    "hostb_endpoint_app", ENDPOINT_DIR / "app.py")
app = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(app)

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
RECEIPT_REQUIRED = {
    "schema": str, "agent_version": str, "request_id": str,
    "decision_final": str, "tool_calls": dict,
    "strands_agent_available": bool, "deployment": bool,
    "generated_at": str, "receipt_sha256": str,
}


def assert_receipt_shape(receipt):
    for key, typ in RECEIPT_REQUIRED.items():
        assert key in receipt, f"receipt missing {key}"
        assert isinstance(receipt[key], typ), f"{key} wrong type"
    assert receipt["schema"] == "studysprint-agent-receipt/v1"
    assert receipt["decision_final"] in (
        "ABSTAIN", "ALLOW_RECOMMENDATION", "ESCALATE")
    assert SHA_RE.match(receipt["receipt_sha256"])
    body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True).encode()).hexdigest()
    assert digest == receipt["receipt_sha256"], (
        "receipt_sha256 must stamp the receipt content")


def fake_live(ref):
    return {
        "tool_calls": {"fetch_syllabus_evidence": 1, "make_plan": 1},
        "tool_trace": [
            {"tool": "fetch_syllabus_evidence", "order": 0,
             "output_sha256": hashlib.sha256(b"evidence").hexdigest()},
            {"tool": "make_plan", "order": 1,
             "output_sha256": hashlib.sha256(b"plan").hexdigest()},
        ],
        "reply_excerpt": "Plan built from the fetched syllabus.",
    }


def test_health_shape():
    payload = app.health_payload()
    assert payload["status"] == "ok"
    assert payload["deployment"] is True
    assert isinstance(payload["strands_agent_available"], bool)
    assert payload["model_id"] == "us.amazon.nova-lite-v1:0"
    try:
        import jsonschema
    except ImportError:
        return
    if SCHEMAS_DIR.exists():
        doc = json.loads(
            (SCHEMAS_DIR / "endpoint.schema.json").read_text())
        jsonschema.validate(payload, {
            "$defs": doc["$defs"],
            "$ref": "#/$defs/HealthResponse",
        })


def test_plan_live_path_faked_transport(monkeypatch):
    monkeypatch.setattr(app, "_preflight_missing", lambda: [])
    monkeypatch.setattr(app, "_invoke_live_agent", fake_live)
    raw = app.plan_response(
        json.dumps({"syllabus_ref": "examples/syllabus.json"}).encode())
    receipt = json.loads(raw)
    assert_receipt_shape(receipt)
    assert receipt["execution_class"] == "live-production"
    assert receipt["fail_closed"] is False
    assert receipt["deployment"] is True
    assert receipt["model"] == {
        "provider": "amazon-bedrock",
        "model_id": "us.amazon.nova-lite-v1:0",
        "sdk_version": receipt["model"]["sdk_version"],
    }
    assert receipt["tool_calls"] == {
        "fetch_syllabus_evidence": 1, "make_plan": 1}
    assert [t["tool"] for t in receipt["tool_trace"]] == [
        "fetch_syllabus_evidence", "make_plan"]
    assert receipt["plan"] is not None
    assert receipt["decision_final"] == "ALLOW_RECOMMENDATION"


def test_plan_inline_syllabus(monkeypatch):
    monkeypatch.setattr(app, "_preflight_missing", lambda: [])
    monkeypatch.setattr(app, "_invoke_live_agent", fake_live)
    doc = {"course": "TEST 101", "weeks": [
        {"week": 1, "topics": ["alpha"], "due": "quiz"}]}
    raw = app.plan_response(json.dumps({"syllabus": doc}).encode())
    receipt = json.loads(raw)
    assert_receipt_shape(receipt)
    assert receipt["execution_class"] == "live-production"
    assert receipt["plan"] is not None


def test_plan_forced_model_failure_is_fail_closed(monkeypatch):
    def boom(ref):
        raise RuntimeError("bedrock throttled exactly")
    monkeypatch.setattr(app, "_preflight_missing", lambda: [])
    monkeypatch.setattr(app, "_invoke_live_agent", boom)
    raw = app.plan_response(
        json.dumps({"syllabus_ref": "examples/syllabus.json"}).encode())
    receipt = json.loads(raw)
    assert_receipt_shape(receipt)
    assert receipt["execution_class"] == "offline-gate"
    assert receipt["fail_closed"] is True
    assert receipt["deployment"] is False
    assert receipt["error"] == "RuntimeError: bedrock throttled exactly"
    assert "model" not in receipt


def test_plan_preflight_failure_is_fail_closed():
    # No creds in env (see module top): pre-flight must degrade.
    raw = app.plan_response(
        json.dumps({"syllabus_ref": "examples/syllabus.json"}).encode())
    receipt = json.loads(raw)
    assert_receipt_shape(receipt)
    assert receipt["execution_class"] == "offline-gate"
    assert receipt["fail_closed"] is True
    assert "pre-flight" in receipt["error"]


def test_plan_malformed_body_abstains():
    raw = app.plan_response(b"{not json")
    receipt = json.loads(raw)
    assert_receipt_shape(receipt)
    assert receipt["execution_class"] == "offline-gate"
    assert receipt["fail_closed"] is True
    assert receipt["decision_final"] == "ABSTAIN"
    assert receipt["plan"] is None
    assert "malformed request body" in receipt["error"]


def test_plan_missing_syllabus_abstains():
    raw = app.plan_response(b"{}")
    receipt = json.loads(raw)
    assert_receipt_shape(receipt)
    assert receipt["decision_final"] == "ABSTAIN"
    assert receipt["plan"] is None


def test_receipt_roundtrip_byte_identical(monkeypatch):
    monkeypatch.setattr(app, "_preflight_missing", lambda: [])
    monkeypatch.setattr(app, "_invoke_live_agent", fake_live)
    raw = app.plan_response(
        json.dumps({"syllabus_ref": "examples/syllabus.json"}).encode())
    receipt_id = json.loads(raw)["receipt_sha256"]
    assert app.receipt_lookup(receipt_id) == raw
    assert app.receipt_lookup("0" * 64) is None


@pytest.fixture()
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), app.H)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def _call(method, url, body=None):
    req = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def test_http_surface(server, monkeypatch):
    monkeypatch.setattr(app, "_preflight_missing", lambda: [])
    monkeypatch.setattr(app, "_invoke_live_agent", fake_live)
    st, raw = _call("GET", server + "/health")
    assert st == 200
    assert json.loads(raw)["status"] == "ok"

    st, raw = _call("POST", server + "/plan", json.dumps(
        {"syllabus_ref": "examples/syllabus.json"}).encode())
    assert st == 200
    receipt = json.loads(raw)
    assert_receipt_shape(receipt)

    st, raw2 = _call("GET", server + "/receipt/"
                     + receipt["receipt_sha256"])
    assert st == 200
    assert raw2 == raw  # byte-identical round-trip

    st, _ = _call("GET", server + "/receipt/" + "f" * 64)
    assert st == 404  # the endpoint's ONLY 404


def test_retired_routes_absent(server):
    for method, path in [("GET", "/model"), ("POST", "/model"),
                         ("GET", "/wake"), ("GET", "/")]:
        st, _ = _call(method, server + path,
                      b"{}" if method == "POST" else None)
        assert st == 404, f"{method} {path} must be retired"


def test_vendored_copies_match_canonical():
    pairs = [
        ("agent.py", STUDYSPRINT_ROOT / "agent.py"),
        ("study_tools.py", STUDYSPRINT_ROOT / "study_tools.py"),
        ("foundation/oracle_kernel.py",
         STUDYSPRINT_ROOT / "foundation" / "oracle_kernel.py"),
        ("VERSION", STUDYSPRINT_ROOT / "VERSION"),
        ("examples/syllabus.json",
         STUDYSPRINT_ROOT / "examples" / "syllabus.json"),
    ]
    for rel, canonical in pairs:
        if not canonical.exists():
            pytest.skip("canonical tree absent (isolated run)")
        assert (ENDPOINT_DIR / rel).read_bytes() == \
            canonical.read_bytes(), f"vendored {rel} drifted"


def test_dockerfile_copies_the_vendored_set():
    dockerfile = (ENDPOINT_DIR / "Dockerfile").read_text()
    for token in ("app.py", "agent.py", "study_tools.py", "VERSION",
                  "foundation/", "examples/"):
        assert token in dockerfile
