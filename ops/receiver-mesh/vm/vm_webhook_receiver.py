#!/usr/bin/env python3
"""VM bounded webhook intake leg — Receiver Mesh extension (owner order 2026-10-30).

Scope (bounded, per docs/ops/VM-WEBHOOKS.md): intake ONLY.
- POST /webhook/<source>  HMAC-SHA256 verified, deduped, normalized to the
  Receiver Mesh allowlisted envelope, appended to a durable JSONL intake log.
- GET  /health            liveness + log counters (no payload data).
- Routing: envelope source is resolved at intake against the route
  table (routes.json / provider profile fleet.vm_webhooks) and the
  resolved route is recorded in the envelope as delivery_target +
  route_status, so the dispatch layer delivers to the specific side
  chat directly. Unknown source => logged, route_status=
  unrouted_flagged, never silently dropped. Resolution + recording is
  intake work; sending stays with the dispatch layer.
- No business logic, no commits, no standing daemon: the
  process runs only while launched (session / one-shot), never installed
  as a service. Forwarding/business logic stays in GitHub Actions
  (receiver-process.yml) per docs/ops/RECEIVER-MESH.md.

Secret: env VM_WEBHOOK_SECRET (names-only everywhere else; value never
logged, never in the intake log). Log: env VM_WEBHOOK_LOG, default
~/workspace/vm-webhooks/intake.jsonl. Port: env VM_WEBHOOK_PORT, default 8791.
Stdlib only.
"""
from __future__ import annotations
import hashlib, hmac, json, os, sys, threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ENVELOPE_FIELDS = ("source", "event", "delivery_id", "received_at", "repo", "action", "actor", "object_id", "delivery_target", "route_status")

def load_routes() -> dict:
    """Route table: VM_WEBHOOK_ROUTES file > routes.json next to this
    script > empty (everything unrouted_flagged)."""
    candidates = [os.environ.get("VM_WEBHOOK_ROUTES"),
                  str(Path(__file__).resolve().parent / "routes.json")]
    for cand in candidates:
        if cand and Path(cand).is_file():
            try:
                return json.loads(Path(cand).read_text(encoding="utf-8")).get("routes", {})
            except Exception:
                continue
    return {}

def resolve_route(routes: dict, source: str):
    """Returns (delivery_target|None, route_status)."""
    target = routes.get(source)
    if isinstance(target, dict) and target.get("chat_id"):
        return {"chat_id": target["chat_id"], "role": target.get("role")}, "routed"
    return None, "unrouted_flagged"
_lock = threading.Lock()

def verify_signature(secret: str, body: bytes, header: str | None) -> bool:
    if not secret or not header:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.strip())

def normalize(source: str, payload: dict, delivery_id: str, routes: dict | None = None) -> dict:
    delivery_target, route_status = resolve_route(routes or {}, source)
    env = {
        "source": source,
        "event": payload.get("event") or payload.get("type"),
        "delivery_id": delivery_id,
        "received_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": (payload.get("repository") or {}).get("full_name") if isinstance(payload.get("repository"), dict) else payload.get("repo"),
        "action": payload.get("action"),
        "actor": (payload.get("sender") or {}).get("login") if isinstance(payload.get("sender"), dict) else payload.get("actor"),
        "object_id": payload.get("object_id"),
        "delivery_target": delivery_target,
        "route_status": route_status,
    }
    return {k: env.get(k) for k in ENVELOPE_FIELDS}

class IntakeLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seen: set[str] = set()
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                try:
                    self._seen.add(json.loads(line)["delivery_id"])
                except Exception:
                    continue
    def append(self, envelope: dict) -> bool:
        """Returns True if new, False if duplicate delivery_id."""
        with _lock:
            if envelope["delivery_id"] in self._seen:
                return False
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(envelope, separators=(",", ":")) + "\n")
                fh.flush(); os.fsync(fh.fileno())
            self._seen.add(envelope["delivery_id"])
            return True
    def count(self) -> int:
        return len(self._seen)

def make_handler(secret: str, log: IntakeLog, routes: dict | None = None):
    routes = routes if routes is not None else load_routes()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # keep stdout clean; never log headers/body
            pass
        def _send(self, code: int, obj: dict):
            data = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def do_GET(self):
            if self.path == "/health":
                self._send(200, {"status": "ok", "surface": "vm-webhook-intake", "logged": log.count()})
            else:
                self._send(404, {"error": "not_found"})
        def do_POST(self):
            if not self.path.startswith("/webhook/"):
                self._send(404, {"error": "not_found"}); return
            source = self.path.split("/")[2].split("?")[0]
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else b""
            sig = self.headers.get("X-Hub-Signature-256") or self.headers.get("X-Receiver-Signature")
            if not verify_signature(secret, body, sig):
                self._send(401, {"error": "bad_signature"}); return
            try:
                payload = json.loads(body or b"{}")
            except Exception:
                self._send(400, {"error": "invalid_json"}); return
            delivery_id = self.headers.get("X-GitHub-Delivery") or payload.get("delivery_id")
            if not delivery_id:
                self._send(400, {"error": "missing_delivery_id"}); return
            envelope = normalize(source, payload, str(delivery_id), routes)
            if not envelope["event"]:
                self._send(400, {"error": "missing_event"}); return
            new = log.append(envelope)
            self._send(202 if new else 200, {"accepted": new, "duplicate": not new, "delivery_id": envelope["delivery_id"], "route_status": envelope["route_status"], "delivery_target": envelope["delivery_target"]})
    return Handler

def main() -> int:
    secret = os.environ.get("VM_WEBHOOK_SECRET", "")
    if not secret:
        print("VM_WEBHOOK_SECRET not set (names-only: provision locally, never commit)", file=sys.stderr); return 2
    log = IntakeLog(Path(os.environ.get("VM_WEBHOOK_LOG", os.path.expanduser("~/workspace/vm-webhooks/intake.jsonl"))))
    port = int(os.environ.get("VM_WEBHOOK_PORT", "8791"))
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(secret, log, load_routes()))
    print(f"vm-webhook-intake listening on 127.0.0.1:{port} (bounded intake only; Ctrl-C / session end stops it)")
    server.serve_forever()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
