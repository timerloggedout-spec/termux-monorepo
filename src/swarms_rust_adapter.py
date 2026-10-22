"""Optional pinned swarms-rs worker boundary (THUB-015).

No cargo invocation, SDK import, or model request occurs during a dry-run.
This is process/state isolation for a trusted SDK, not a security sandbox.
"""
from __future__ import annotations

import ipaddress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from src.swarms_adapter import validate_config
from src.telemetry import TermuxTelemetryLogger

DEFAULT_BASE = "http://127.0.0.1:8787/v1"


def validate_base(base: str) -> str:
    """Require TLS off loopback; never accept URL-embedded credentials."""
    try:
        parsed = urlsplit(base)
        port = parsed.port  # Validate malformed ports before spawning the worker.
        host = parsed.hostname
        if not host or parsed.username is not None or parsed.password is not None:
            raise ValueError
        if parsed.query or parsed.fragment or parsed.scheme not in {"http", "https"}:
            raise ValueError
        if port is not None and not 1 <= port <= 65535:
            raise ValueError
        loopback = host == "localhost"
        try:
            loopback = loopback or ipaddress.ip_address(host).is_loopback
        except ValueError:
            pass
        if parsed.scheme == "http" and not loopback:
            raise ValueError
        if any(char.isspace() for char in base) or "\\" in base:
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        raise ValueError("LLM_API_HUB_BASE must be HTTPS (or HTTP loopback), without credentials, query, or fragment") from None
    return base.rstrip("/") + "/"


def _positive_integer(name: str, value: Any) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


class _HubBridge:
    """Short-lived loopback proxy: SDK traffic can reach only the configured hub route."""
    MAX_BODY = 2 * 1024 * 1024
    MAX_RESPONSE = 8 * 1024 * 1024
    UPSTREAM_TIMEOUT = 30

    def __init__(self, base: str, correlation: Mapping[str, Any]):
        self.target = base.rstrip("/") + "/chat/completions"
        self.correlation = dict(correlation)
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                self.connection.settimeout(5)
                if self.path != "/v1/chat/completions":
                    self.send_error(404)
                    return
                try:
                    size = int(self.headers.get("Content-Length", "-1"))
                    if size < 0 or size > owner.MAX_BODY:
                        self.send_error(413)
                        return
                    body = self.rfile.read(size)
                    payload = json.loads(body)
                    if not isinstance(payload, dict):
                        self.send_error(400)
                        return
                    child_id, attempt_id = str(uuid.uuid4()), str(uuid.uuid4())
                    headers = {"Content-Type": "application/json"}
                    auth = self.headers.get("Authorization")
                    if auth:
                        headers["Authorization"] = auth
                    values = {**owner.correlation, "request_id": child_id,
                              "attempt_id": attempt_id,
                              "parent_id": owner.correlation.get("parent_id") or owner.correlation.get("request_id") or owner.correlation.get("attempt_id"),
                              "adapter": "swarms-rs"}
                    for key, value in values.items():
                        if value is not None and isinstance(value, (str, int, float)):
                            headers["X-Termux-" + "-".join(p.title() for p in key.split("_"))] = str(value)
                    request = Request(owner.target, data=json.dumps(payload).encode(), headers=headers, method="POST")
                    try:
                        class NoRedirect(HTTPRedirectHandler):
                            def redirect_request(self, *_args, **_kwargs):
                                return None
                        response = build_opener(NoRedirect).open(request, timeout=owner.UPSTREAM_TIMEOUT)
                    except HTTPError as err:
                        response = err
                    with response:
                        data = response.read(owner.MAX_RESPONSE + 1)
                        if len(data) > owner.MAX_RESPONSE:
                            self.send_error(502)
                            return
                        self.send_response(response.status)
                        self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                        self.send_header("Content-Length", str(len(data)))
                        retry = response.headers.get("Retry-After")
                        if retry and retry.isdigit() and len(retry) <= 6:
                            self.send_header("Retry-After", retry)
                        self.end_headers()
                        self.wfile.write(data)
                except (ValueError, OSError, URLError, socket.timeout):
                    try:
                        self.send_error(502)
                    except OSError:
                        pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return f"http://127.0.0.1:{self.server.server_address[1]}/v1/"

    def __exit__(self, *_exc):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def run(config: Mapping[str, Any], *, binary: str | os.PathLike[str] | None = None,
        timeout_seconds: int = 120, max_tokens: int = 8192) -> dict[str, Any]:
    """Execute only an explicitly installed trusted worker in a fresh private cwd.

    Upstream prints on stdout despite quiet settings, so result.json is a separate
    child-to-parent channel. Child diagnostic streams are never forwarded.
    The outer deadline includes a small grace period for the worker's own deadline.
    """
    cfg = validate_config(config)
    # Parent-provided correlation is passed to the worker as metadata only.
    for key in ("run_id", "job_id", "request_id", "attempt_id", "parent_id", "source_revision", "provider"):
        if key in config:
            cfg[key] = config[key]
    timeout_seconds = _positive_integer("timeout_seconds", timeout_seconds)
    max_tokens = _positive_integer("max_tokens", max_tokens)
    result: dict[str, Any] = {
        "status": "dry_run", "backend": "swarms-rs", **cfg,
        "timeout_seconds": timeout_seconds, "max_tokens": max_tokens,
        "state_policy": "temporary subprocess workspace, removed after execution",
    }
    if not cfg["execute"]:
        result["note"] = "Offline dry-run; an installed worker, execute=true, and explicit model are required for model calls."
        return result

    base = validate_base(os.environ.get("LLM_API_HUB_BASE", DEFAULT_BASE))
    requested = os.fspath(binary) if binary is not None else os.environ.get("SWARMS_RS_BINARY", "")
    if not requested:
        raise ValueError("Set SWARMS_RS_BINARY or --binary to an explicitly installed Rust worker; no automatic build or download")
    located = shutil.which(requested)
    if located is None:
        raise ValueError("Rust worker is missing or not executable")
    executable = str(Path(located).resolve())
    payload = {**cfg, "timeout_seconds": timeout_seconds, "max_tokens": max_tokens}
    cfg["run_id"] = cfg.get("run_id") or uuid.uuid4().hex
    cfg["job_id"] = cfg.get("job_id") or cfg["run_id"]
    cfg["request_id"] = cfg.get("request_id") or uuid.uuid4().hex
    cfg["attempt_id"] = cfg.get("attempt_id") or uuid.uuid4().hex
    cfg["source_revision"] = "ee1e74cb6e2c94775db88dddb311f2235e3fe9e3"
    cfg["provider"] = cfg["model"].split("/", 1)[0]
    corr = {k: cfg.get(k) for k in ("run_id", "job_id", "request_id", "attempt_id", "parent_id", "source_revision", "provider")}
    corr.update(adapter="swarms-rs", model=cfg.get("model"), event="request", outcome="UNKNOWN")
    TermuxTelemetryLogger.notify("INFO", "swarms-rs", "Worker request started", context=corr)
    with tempfile.TemporaryDirectory(prefix="termux-swarms-rs-") as state:
        with _HubBridge(base, {k: cfg.get(k) for k in ("run_id", "job_id", "request_id", "attempt_id", "parent_id", "source_revision")} | {"provider": cfg.get("provider")}) as bridge_url:
            env = dict(os.environ)
            env.update({"LLM_API_HUB_BASE": bridge_url, "HOME": state, "TMPDIR": state})
            try:
                proc = subprocess.run([executable], input=json.dumps(payload), text=True,
                                      capture_output=True, cwd=state, env=env,
                                      timeout=timeout_seconds + 5, check=False)
            except subprocess.TimeoutExpired:
                TermuxTelemetryLogger.notify("CRITICAL", "swarms-rs", "Worker cancelled at deadline", context={**corr, "event": "cancelled", "outcome": "cancel"})
                raise RuntimeError("Rust worker exceeded its execution deadline and was terminated") from None
        # Worker stdout/stderr may contain prompts, credentials, or upstream output. Never forward it.
        path = Path(state) / "result.json"
        try:
            response = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            TermuxTelemetryLogger.notify("CRITICAL", "swarms-rs", "Worker returned invalid result", context={**corr, "event": "error", "outcome": "failure"})
            raise RuntimeError("Rust worker returned no valid JSON result") from None
        if not isinstance(response, dict):
            raise RuntimeError("Rust worker returned an invalid result object")
        if proc.returncode != 0 or response.get("status") != "complete":
            status = str(response.get("status", "")).lower()
            outcome = "deny" if "deny" in status else ("cancel" if "cancel" in status else "failure")
            TermuxTelemetryLogger.notify("CRITICAL", "swarms-rs", "Worker execution did not complete", context={**corr, "event": "error", "outcome": outcome})
            raise RuntimeError("Rust worker execution failed")
        if response.get("backend") != "swarms-rs" or "output" not in response:
            raise RuntimeError("Rust worker returned an incomplete success result")
        result.update(response)
        result["provider"] = "llm_api_hub OpenAI-compatible endpoint"
    TermuxTelemetryLogger.notify("SUCCESS", "swarms-rs", "Worker returned; task outcome UNKNOWN", context={**corr, "event": "response", "outcome": "UNKNOWN"})
    return result
