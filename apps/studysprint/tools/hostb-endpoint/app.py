"""Branch-(a) live Strands endpoint -- host B (SnapDeploy) build.

STAGED: code complete, only credentials missing. Serves the
StudySprint branch-(a) receipt contract from the persisting
hostb-fit-test container base:

  GET  /       status (versions, rss, creds presence, slot state)
  GET  /wake   wake-ping target (addendum A2: surfaces ping this
               on load; the free container's cold wake measured
               34.2s, so first-response latency <= ~60s is the
               wake envelope, not an error)
  POST /model  {prompt?} -> live Strands/Bedrock invocation with a
               deployment receipt; GET /model uses a fixed prompt.

Addendum A1 (fail-fast credential chain) is structural here:
  * IMDS is disabled before boto3 loads (env + Dockerfile ENV).
  * Credentials come ONLY from explicit env (AWS_ACCESS_KEY_ID /
    AWS_SECRET_ACCESS_KEY) or an optional bundled creds.env file
    (fire-time baking path; real env wins).
  * Pre-flight runs before any Agent() construction: absent or
    placeholder credentials, or an empty model slot, return the
    app's own receipt-shaped 503 IMMEDIATELY -- no boto3 chain
    stall, no platform-proxy death (the fit test's failure mode).
  * The Bedrock client config is fail-fast: connect_timeout 2s,
    bounded read timeout, max 2 attempts.

The model id is a SLOT: env STRANDS_MODEL_ID, filled verbatim at
fire time (Nova-class). Region: env AWS_REGION (default
us-east-1). No live call is possible in the staged state.
"""
import json
import os
import time

# A1: IMDS off BEFORE boto3/strands load.
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")

STARTED_AT = time.time()
MODEL_ID = os.environ.get("STRANDS_MODEL_ID", "")
REGION = os.environ.get("AWS_REGION", "us-east-1")
PLACEHOLDER = "placeholder"
DEFAULT_PROMPT = "Reply with one short sentence confirming you are live."


def _load_creds_env():
    """Optional fire-time baking path: creds.env next to app.py
    (KEY=VALUE lines). Real environment always wins."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "creds.env")
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_creds_env()


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


def preflight_missing():
    missing = []
    if not MODEL_ID:
        missing.append("STRANDS_MODEL_ID (model slot)")
    if not creds_state()["real"]:
        missing.append("real AWS credentials (env or creds.env; "
                       "absent/placeholder rejected)")
    return missing


def base_receipt():
    import boto3
    import strands  # noqa: F401  (import proves the SDK is resident)
    from importlib.metadata import version as _v
    try:
        sdk = f"strands-agents {_v('strands-agents')}"
    except Exception:
        sdk = "unknown"
    return {
        "deployment": True,
        "provider": "amazon-bedrock",
        "model": MODEL_ID or None,
        "region": REGION,
        "run": os.environ.get("RUN_ID"),
        "commit": os.environ.get("BUILD_COMMIT"),
        "sdk": sdk,
        "boto3": boto3.__version__,
        "tools": [],
        "tools_called": [],
    }


def rss_mb():
    try:
        for line in open("/proc/self/status"):
            if line.startswith("VmRSS:"):
                return round(int(line.split()[1]) / 1024, 1)
    except Exception:
        return None


# Warm the SDK at startup (A2: wake latency must not compound
# with import time on the first /model hit).
_T0 = time.time()
import boto3  # noqa: E402,F401
import strands  # noqa: E402,F401
IMPORT_S = round(time.time() - _T0, 2)

from http.server import BaseHTTPRequestHandler, HTTPServer  # noqa: E402


class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _status(self):
        self._json(200, {
            "service": "studysprint-strands-endpoint",
            "status": "up",
            "uptime_s": round(time.time() - STARTED_AT, 1),
            "rss_mb": rss_mb(),
            "sdk_import_s": IMPORT_S,
            "aws_creds_present": creds_state()["present"],
            "aws_creds_real": creds_state()["real"],
            "model_slot_set": bool(MODEL_ID),
            "region": REGION,
        })

    def _model(self, prompt):
        missing = preflight_missing()
        if missing:
            # A1: immediate, app-shaped, receipt-carrying 503.
            self._json(503, {
                "ok": False,
                "fail_closed": True,
                "error_type": "PreflightError",
                "error": "staged, awaiting fire inputs: "
                         + "; ".join(missing),
                "receipt": base_receipt(),
            })
            return
        try:
            from botocore.config import Config as BotoConfig
            from strands import Agent
            from strands.models.bedrock import BedrockModel
            cfg = build_model_config()
            model = BedrockModel(
                model_id=cfg["model_id"],
                region_name=cfg["region_name"],
                boto_client_config=BotoConfig(
                    connect_timeout=2, read_timeout=120,
                    retries={"max_attempts": 2, "mode": "standard"}))
            agent = Agent(model=model)
            result = agent(prompt)
            receipt = base_receipt()
            metrics = getattr(result, "metrics", None)
            tool_metrics = getattr(metrics, "tool_metrics", {}) or {}
            receipt["tools_called"] = sorted(tool_metrics.keys())
            self._json(200, {
                "ok": True,
                "reply_excerpt":
                    str(getattr(result, "message", result))[:600],
                "receipt": receipt,
            })
        except Exception as e:
            self._json(503, {
                "ok": False,
                "fail_closed": True,
                "error_type": type(e).__name__,
                "error": str(e)[:400],
                "receipt": base_receipt(),
            })

    def do_GET(self):
        if self.path == "/wake":
            self._json(200, {"ok": True, "awake": True,
                             "uptime_s": round(time.time() - STARTED_AT, 1)})
        elif self.path == "/model":
            self._model(DEFAULT_PROMPT)
        else:
            self._status()

    def do_POST(self):
        if self.path == "/model":
            try:
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b""
                prompt = (json.loads(raw).get("prompt")
                          if raw else None) or DEFAULT_PROMPT
            except Exception:
                prompt = DEFAULT_PROMPT
            self._model(prompt)
        else:
            self._json(404, {"ok": False, "error": "unknown path"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), H).serve_forever()
