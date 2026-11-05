"""Host-B live Strands endpoint -- contract-aligned build.

Serves the strands-aws endpoint contract of record
(apps/studysprint/strands-aws/schemas/endpoint.schema.json) from
the persisting hostb-fit-test container:

  GET  /health        -> HealthResponse {status: "ok",
                         strands_agent_available, deployment: true,
                         model_id}
  POST /plan          -> ALWAYS HTTP 200 with a receipt
                         (receipt.schema.json). Live success:
                         the shipped Strands agent
                         (agent.build_strands_agent) runs its tool
                         chain on Amazon Bedrock and the receipt
                         carries execution_class=live-production,
                         deployment=true, the Bedrock model block
                         and the tool_trace. ANY failure (pre-flight,
                         transport, model, malformed body) degrades
                         to the deterministic gate loop
                         (agent.run_agent) and the receipt carries
                         execution_class=offline-gate +
                         fail_closed=true + the exact error.
                         There is NO 5xx /plan shape.
  GET  /receipt/{id}  -> the stored receipt, byte-identical to the
                         one the invocation returned (receipts are
                         content-stamped by receipt_sha256). An
                         unknown id is the endpoint's ONLY 404.

Retired fit-test routes (/, /wake, /model) are absent.

The client side already speaks this contract (apps/studysprint/
live.py + web/live.js, PR #4962); the schemas and the client are
the contract of record and are NOT changed here.

Packaging: the container build context is THIS directory. The
/plan path drives the shipped agent machinery, so the core
modules it needs are vendored into this directory as byte-
identical copies of the canonical apps/studysprint files
(agent.py, study_tools.py, foundation/oracle_kernel.py, VERSION,
examples/syllabus.json). tests/test_endpoint_contract.py carries
a drift guard: vendored == canonical, checked in the full repo.

A1 fail-fast credential chain (retained from the staged build):
  * IMDS is disabled before boto3/strands load (env + Dockerfile).
  * Credentials come ONLY from explicit env (AWS_ACCESS_KEY_ID /
    AWS_SECRET_ACCESS_KEY) or an optional bundled creds.env file
    (fire-time baking path; real env wins).
  * Pre-flight runs before any Agent invocation: absent or
    placeholder credentials, or an empty model slot, degrade
    /plan to the fail-closed receipt -- never a boto3 chain stall
    behind the platform proxy.
  * The Bedrock client config is fail-fast: connect_timeout 2s,
    bounded read timeout, max 2 attempts.
  * The model swap follows the DoE-verified proof pattern
    (tools/strands_proof.py): build_strands_agent() eagerly
    constructs a default BedrockModel; the endpoint swaps in the
    slotted BedrockModel (env STRANDS_MODEL_ID, verbatim) before
    invocation.

Region: env AWS_REGION (default us-east-1).
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

# A1: IMDS off BEFORE boto3/strands load.
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

STARTED_AT = time.time()
MODEL_ID = os.environ.get("STRANDS_MODEL_ID", "")
REGION = os.environ.get("AWS_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", REGION)
os.environ.setdefault("AWS_DEFAULT_REGION", REGION)
PLACEHOLDER = "placeholder"

_RECEIPTS: dict[str, bytes] = {}
_RECEIPTS_LOCK = threading.Lock()
_CORE = None
_AGENT_AVAILABLE: bool | None = None


def _load_creds_env():
    """Optional fire-time baking path: creds.env next to app.py
    (KEY=VALUE lines). Real environment always wins."""
    path = BASE_DIR / "creds.env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_creds_env()
MODEL_ID = os.environ.get("STRANDS_MODEL_ID", MODEL_ID)


def creds_state():
    ak = os.environ.get("AWS_ACCESS_KEY_ID", "")
    sk = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    present = bool(ak and sk)
    real = present and ak != PLACEHOLDER and sk != PLACEHOLDER
    return {"present": present, "real": real}


def build_model_config():
    """Pure config (dry-checkable): exactly what the live call
    will use, minus the call itself."""
    return {
        "provider": "amazon-bedrock",
        "model_id": MODEL_ID or None,
        "region_name": REGION,
        "boto_client_config": {
            "connect_timeout": 2,
            "read_timeout": 120,
            "retries": {"max_attempts": 2, "mode": "standard"},
        },
    }


def _preflight_missing():
    missing = []
    if not MODEL_ID:
        missing.append("STRANDS_MODEL_ID (model slot)")
    if not creds_state()["real"]:
        missing.append("real AWS credentials (env or creds.env; "
                       "absent/placeholder rejected)")
    return missing


def _sdk_version():
    from importlib.metadata import version as _v
    try:
        return _v("strands-agents")
    except Exception:
        return "unknown"


def _load_core():
    """Load the vendored shipped agent machinery (agent.py) under
    a private module name, so the endpoint never collides with
    the canonical `agent` module in a host test suite."""
    global _CORE
    if _CORE is None:
        spec = importlib.util.spec_from_file_location(
            "hostb_endpoint_core_agent", BASE_DIR / "agent.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _CORE = mod
    return _CORE


def _agent_available():
    global _AGENT_AVAILABLE
    if _AGENT_AVAILABLE is None:
        try:
            _AGENT_AVAILABLE = _load_core().build_strands_agent() is not None
        except Exception:
            _AGENT_AVAILABLE = False
    return _AGENT_AVAILABLE


def health_payload():
    payload = {
        "status": "ok",
        "strands_agent_available": _agent_available(),
        "deployment": True,
    }
    if MODEL_ID:
        payload["model_id"] = MODEL_ID
    return payload


def _run_core(request, root):
    return _load_core().run_agent(request, root=root)


def _emergency_receipt(request_id, error):
    """A schema-valid ABSTAIN receipt built without the core --
    the last-resort floor if the core itself cannot run."""
    try:
        agent_version = (BASE_DIR / "VERSION").read_text().strip()
    except OSError:
        agent_version = "unknown"
    receipt = {
        "schema": "studysprint-agent-receipt/v1",
        "agent_version": agent_version,
        "request_id": request_id,
        "action": "build_study_plan",
        "decision_on_asserted_evidence": "ABSTAIN",
        "decision_final": "ABSTAIN",
        "decision_accessible": "Abstain",
        "plain_language_explanation":
            "The endpoint could not run its planning core.",
        "trust_receipt": None,
        "evidence_set": None,
        "plan": None,
        "today_view": None,
        "quiz": None,
        "replan": None,
        "tool_calls": {},
        "strands_agent_available": False,
        "deployment": False,
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "error": f"{type(error).__name__}: {error}",
    }
    receipt["receipt_sha256"] = hashlib.sha256(
        json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    return receipt


def _safe_core(request, root):
    """The deterministic gate loop, with an emergency floor: a
    core failure never propagates out of /plan."""
    try:
        return _run_core(request, root)
    except Exception as exc:
        try:
            asserted = {"id": request["id"],
                        "action": request["action"], "asserted": True}
            receipt = _run_core(asserted, root)
            receipt["_core_error"] = f"{type(exc).__name__}: {exc}"
            return receipt
        except Exception:
            return _emergency_receipt(request["id"], exc)


def _tool_count(value):
    if hasattr(value, "call_count"):
        return int(value.call_count)
    if isinstance(value, dict):
        return int(value.get("call_count") or value.get("count") or 1)
    return 1


def _extract_tool_trace(agent):
    """One entry per tool invocation, in execution order, from
    the agent's conversation: toolResult blocks carry the output
    that gets content-stamped; toolUse blocks carry the name."""
    uses = {}
    trace = []
    for msg in getattr(agent, "messages", None) or []:
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if "toolUse" in block:
                tu = block["toolUse"] or {}
                uses[tu.get("toolUseId")] = tu.get("name")
            if "toolResult" in block:
                tr = block["toolResult"] or {}
                payload = json.dumps(tr.get("content"),
                                     sort_keys=True, default=str)
                trace.append({
                    "tool": uses.get(tr.get("toolUseId"), "unknown"),
                    "order": len(trace),
                    "output_sha256": hashlib.sha256(
                        payload.encode()).hexdigest(),
                })
    return trace


def _invoke_live_agent(syllabus_ref):
    """Drive the shipped agent machinery on Bedrock. Returns the
    live extension {tool_calls, tool_trace, reply_excerpt}.
    Raises on ANY failure -- the caller degrades fail-closed."""
    core = _load_core()
    agent = core.build_strands_agent()
    if agent is None:
        raise RuntimeError("build_strands_agent() returned None "
                           "(Strands SDK unavailable)")
    from botocore.config import Config as BotoConfig
    from strands.models.bedrock import BedrockModel
    cfg = build_model_config()
    agent.model = BedrockModel(
        model_id=cfg["model_id"],
        region_name=cfg["region_name"],
        boto_client_config=BotoConfig(
            connect_timeout=2, read_timeout=120,
            retries={"max_attempts": 2, "mode": "standard"}))
    prompt = (f"Fetch the syllabus evidence for {syllabus_ref} "
              "using fetch_syllabus_evidence, then call make_plan "
              "with the fetched course JSON, then summarize the "
              "plan in one paragraph.")
    result = agent(prompt)
    metrics = getattr(result, "metrics", None)
    tool_metrics = getattr(metrics, "tool_metrics", {}) or {}
    tool_calls = {name: _tool_count(m)
                  for name, m in tool_metrics.items()}
    if not tool_calls:
        raise RuntimeError("live agent returned no tool calls")
    trace = _extract_tool_trace(agent)
    if not trace:
        raise RuntimeError("live agent tool trace unavailable")
    return {
        "tool_calls": tool_calls,
        "tool_trace": trace,
        "reply_excerpt": str(getattr(result, "message", result))[:600],
    }


def _finalize(receipt, *, execution_class, fail_closed, deployment,
              error=None, live=None):
    r = copy.deepcopy(receipt)
    core_error = r.pop("_core_error", None)
    r["execution_class"] = execution_class
    r["fail_closed"] = fail_closed
    r["deployment"] = deployment
    if error is not None:
        r["error"] = error
    elif core_error is not None:
        r["error"] = core_error
    if live is not None:
        r["model"] = {
            "provider": "amazon-bedrock",
            "model_id": MODEL_ID,
            "sdk_version": _sdk_version(),
        }
        r["tool_calls"] = live["tool_calls"]
        r["tool_trace"] = live["tool_trace"]
        r["reply_excerpt"] = live["reply_excerpt"]
    r.pop("receipt_sha256", None)
    r["receipt_sha256"] = hashlib.sha256(
        json.dumps(r, sort_keys=True).encode()).hexdigest()
    return r


def _store(receipt):
    body = json.dumps(receipt, sort_keys=True).encode()
    with _RECEIPTS_LOCK:
        _RECEIPTS[receipt["receipt_sha256"]] = body
    return body


def receipt_lookup(receipt_id):
    with _RECEIPTS_LOCK:
        return _RECEIPTS.get(receipt_id)


def plan_response(raw_body: bytes) -> bytes:
    """POST /plan: ALWAYS a receipt (the fail-closed floor).
    Returns the exact bytes to serve with HTTP 200."""
    request_id = uuid.uuid4().hex
    error = None
    syllabus = None
    syllabus_ref = None
    try:
        body = json.loads(raw_body) if raw_body else {}
        if not isinstance(body, dict):
            raise ValueError("request body must be a JSON object")
    except Exception as exc:
        body = {}
        error = f"malformed request body: {type(exc).__name__}: {exc}"
    if error is None:
        request_id = str(body.get("request_id") or body.get("id")
                         or request_id)
        if "syllabus" in body:
            if isinstance(body["syllabus"], dict):
                syllabus = body["syllabus"]
            else:
                error = "syllabus must be a course document object"
        elif "syllabus_ref" in body:
            if isinstance(body["syllabus_ref"], str):
                syllabus_ref = body["syllabus_ref"]
            else:
                error = "syllabus_ref must be a string"
        else:
            error = ("PlanRequest requires one of: "
                     "syllabus, syllabus_ref")

    inline_path = None
    try:
        if syllabus is not None:
            inline_path = (BASE_DIR / "examples"
                           / f"__inline_{request_id}.json")
            inline_path.write_text(json.dumps(syllabus))
            syllabus_ref = f"examples/{inline_path.name}"
        request = {"id": request_id, "action": "build_study_plan",
                   "asserted": syllabus_ref is None}
        if syllabus_ref is not None:
            request["artifact"] = {"kind": "syllabus",
                                   "ref": syllabus_ref}
        receipt = _safe_core(request, BASE_DIR)

        if error is not None:
            final = _finalize(receipt, execution_class="offline-gate",
                              fail_closed=True, deployment=False,
                              error=error)
        else:
            missing = _preflight_missing()
            if missing:
                final = _finalize(
                    receipt, execution_class="offline-gate",
                    fail_closed=True, deployment=False,
                    error="pre-flight (staged, awaiting fire "
                          "inputs): " + "; ".join(missing))
            else:
                try:
                    live = _invoke_live_agent(syllabus_ref)
                    final = _finalize(
                        receipt,
                        execution_class="live-production",
                        fail_closed=False, deployment=True,
                        live=live)
                except Exception as exc:
                    final = _finalize(
                        receipt, execution_class="offline-gate",
                        fail_closed=True, deployment=False,
                        error=f"{type(exc).__name__}: {exc}")
        return _store(final)
    finally:
        if inline_path is not None:
            try:
                inline_path.unlink()
            except OSError:
                pass


class H(BaseHTTPRequestHandler):
    def _send(self, code, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj).encode())

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, health_payload())
        elif path.startswith("/receipt/"):
            stored = receipt_lookup(path[len("/receipt/"):])
            if stored is None:
                self._json(404, {"ok": False,
                                 "error": "unknown receipt id"})
            else:
                self._send(200, stored)
        else:
            self._json(404, {"ok": False, "error": "unknown path"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/plan":
            try:
                n = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                n = 0
            raw = self.rfile.read(n) if n > 0 else b""
            self._send(200, plan_response(raw))
        else:
            self._json(404, {"ok": False, "error": "unknown path"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(
        ("0.0.0.0", int(os.environ.get("PORT", "8080"))), H
    ).serve_forever()
