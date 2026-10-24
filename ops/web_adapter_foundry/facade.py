"""HTTP/SSE facade over the Web Adapter Foundry core.

One more fold of the origami: the same `handle_request` that serves the
CLI and the JSONL transport, behind plain HTTP so any surface can drive
the stack — a Buildkite step, a Supabase edge function, another agent,
the phone-as-orchestrator.

Endpoints:
  GET  /health   -> {"ok": true, "version": ..., "operations": [...]}
  GET  /         -> facade info (endpoints + transports)
  POST /invoke   -> one Foundry envelope (JSON) in, one response out.
                    Every response is also published once to the bus.
  GET  /events   -> Server-Sent Events: each invoke's response is fanned
                    out to all subscribers (publish-once; streaming never
                    re-executes an operation). Heartbeat comment every
                    15 s. Late subscribers get no replay — by design.

Stdlib only (http.server), no credentials accepted or required: envelopes
still pass the core's credential-in-body refusal, and operations carry
account_ref only — exactly as on every other transport.

Run:  python3 -m ops.web_adapter_foundry.facade [--host 127.0.0.1]
      [--port 8787] [--registry path/to/registry.json]
"""
from __future__ import annotations

import argparse
import json
import queue as queue_mod
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .waf import VERSION, EventBus, handle_request, load_registry

MAX_BODY = 64 * 1024  # envelopes are small; refuse anything larger
BUILTINS = ("foundry.ping", "foundry.list_operations", "foundry.describe",
            "foundry.promote", "foundry.intake")


def operations_of(registry: dict | None) -> list[str]:
    ops = list(BUILTINS)
    if registry:
        ops += [op["operation_id"] for op in registry.get("operations", [])]
    return ops


def make_server(host: str, port: int, registry: dict | None = None,
                bus: EventBus | None = None) -> ThreadingHTTPServer:
    bus = bus or EventBus()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):  # keep stdout protocol-clean
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

        def _json(self, status: int, obj: dict) -> None:
            body = json.dumps(obj).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self._json(200, {"ok": True, "version": VERSION,
                                 "operations": operations_of(registry)})
            elif self.path == "/":
                self._json(200, {"name": "web-adapter-foundry facade",
                                 "version": VERSION,
                                 "endpoints": {"POST /invoke": "one envelope -> one response (also published to /events)",
                                               "GET /events": "SSE fan-out of invoke responses",
                                               "GET /health": "liveness + operation list"},
                                 "transports": ["cli", "stdin-jsonl", "http", "sse"]})
            elif self.path == "/events":
                self._events()
            else:
                self._json(404, {"ok": False, "error": {"code": "not_found",
                                                        "message": f"no route {self.path}"}})

        def _events(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q = bus.subscribe()
            try:
                self.wfile.write(b": subscribed\n\n")
                self.wfile.flush()
                while True:
                    try:
                        frame = q.get(timeout=15)
                        self.wfile.write(frame.encode())
                    except queue_mod.Empty:
                        self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                bus.unsubscribe(q)

        def do_POST(self):
            if self.path != "/invoke":
                self._json(404, {"ok": False, "error": {"code": "not_found",
                                                        "message": f"no route {self.path}"}})
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                self._json(413, {"ok": False, "error": {"code": "too_large",
                                                        "message": f"envelope exceeds {MAX_BODY} bytes"}})
                return
            raw = self.rfile.read(length) if length else b""
            try:
                req = json.loads(raw.decode("utf-8"))
                if not isinstance(req, dict):
                    raise ValueError("envelope must be a JSON object")
            except (ValueError, UnicodeDecodeError) as exc:
                self._json(400, {"ok": False, "error": {"code": "bad_json",
                                                        "message": str(exc)}})
                return
            resp = handle_request(req, registry)
            bus.publish(resp, event="invoke")
            self._json(200, resp)

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.foundry_bus = bus  # exposed for tests/embedders
    return server


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="waf-facade",
                                 description="Web Adapter Foundry HTTP/SSE facade")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--registry")
    a = ap.parse_args(argv)
    registry = load_registry(a.registry) if a.registry else None
    server = make_server(a.host, a.port, registry)
    sys.stderr.write(f"facade on http://{a.host}:{a.port} "
                     f"({len(operations_of(registry))} operations)\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
