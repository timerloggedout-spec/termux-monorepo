"""P1 pull-queue device poller contracts; no Cloudflare account, no device.

Runs scripts/termux/devices/queue-poll.sh in bash against a sandbox HOME and
a python stub implementing the Worker API shape ({task: row} claim, receipt
POST). The sandbox carries a stub resource snapshot emitting controlled free
space and a stub run-deepagent-task.sh emitting a schema-1 receipt.
Covers spec §8: (a) heartbeat-only claim + receipt with storage_free_mb,
(b) below the adaptive floor nothing is claimed, (c) missing queue.env exits
0 silently (unprovisioned-node discipline).
"""
import json
import os
import subprocess
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLLER = ROOT / "scripts/termux/devices/queue-poll.sh"


class Stub:
    def __init__(self):
        self.tasks = {}
        self.claims = 0
        self.receipts = {}

    def handler(self):
        stub = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, obj=None):
                body = json.dumps(obj).encode() if obj is not None else b""
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path.startswith("/tasks/next"):
                    for t in stub.tasks.values():
                        if t["state"] == "queued":
                            t["state"] = "claimed"
                            stub.claims += 1
                            return self._send(200, {"task": t})
                    return self._send(204)
                return self._send(404, {"error": "not_found"})

            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                if self.path.startswith("/tasks/") and self.path.endswith("/receipt"):
                    tid = self.path.split("/")[2]
                    stub.receipts[tid] = body
                    state = "done" if body["receipt"]["completion_status"] == "completed" else "failed"
                    stub.tasks[tid]["state"] = state
                    return self._send(200, {"id": tid, "state": state})
                return self._send(404, {"error": "not_found"})

        return H


def future_iso():
    return (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


def sandbox(tmp_path, free_mb, with_queue_env=True):
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    (home / ".config/tmx-device").mkdir(parents=True)
    (repo / "scripts/termux").mkdir(parents=True)
    (repo / "scripts/termux-resource-snapshot.sh").write_text(
        f"#!/bin/sh\nprintf 'storage_available_mib={free_mb}\\nstatus=OK\\n'\n")
    (repo / "scripts/termux/run-deepagent-task.sh").write_text(
        "#!/bin/sh\necho '{\"schema_version\":1,\"completion_status\":\"completed\",\"exit_code\":0}'\n")
    (home / ".config/tmx-device/identity.env").write_text(
        f"TERMUX_DEVICE_ID=tmx-node-test1\nTERMUX_MONOREPO_ROOT={repo}\n")
    if with_queue_env:
        (home / ".config/tmx-device/queue.env").write_text("PLACEHOLDER\n")
    return home, repo


def run_poller(home, url=None):
    if url:
        (home / ".config/tmx-device/queue.env").write_text(
            f"DEVICE_QUEUE_URL={url}\nDEVICE_QUEUE_DEVICE_TOKEN=test-device-token\n"
            "DEVICE_QUEUE_ROLE=engineer\nTMX_POLL_RETRY_DELAY=0\n")
    env = {**os.environ, "HOME": str(home)}
    return subprocess.run(["bash", str(POLLER)], capture_output=True, text=True, env=env, timeout=60)


def serve(stub):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), stub.handler())
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def queued_task(tid="dq-test-1"):
    return {"id": tid, "kind": "heartbeat-only", "role": "engineer", "payload": "{}",
            "state": "queued", "expires_at": future_iso()}


def test_heartbeat_claim_and_receipt_with_storage(tmp_path):
    stub = Stub()
    stub.tasks["dq-test-1"] = queued_task()
    srv, url = serve(stub)
    try:
        home, _ = sandbox(tmp_path, free_mb=5000)
        r = run_poller(home, url)
        assert r.returncode == 0, r.stderr
        assert stub.claims == 1
        w = stub.receipts["dq-test-1"]
        assert w["schema_version"] == 1 and w["device_id"] == "tmx-node-test1"
        assert w["storage_free_mb"] == 5000
        assert w["receipt"]["completion_status"] == "completed"
        assert stub.tasks["dq-test-1"]["state"] == "done"
    finally:
        srv.shutdown()


def test_below_floor_claims_nothing(tmp_path):
    stub = Stub()
    stub.tasks["dq-test-1"] = queued_task()
    srv, url = serve(stub)
    try:
        home, _ = sandbox(tmp_path, free_mb=100)
        r = run_poller(home, url)
        assert r.returncode == 0, r.stderr
        assert stub.claims == 0 and stub.receipts == {}
        assert stub.tasks["dq-test-1"]["state"] == "queued"
    finally:
        srv.shutdown()


def test_missing_queue_env_exits_zero_silently(tmp_path):
    home, _ = sandbox(tmp_path, free_mb=5000, with_queue_env=False)
    r = run_poller(home)
    assert r.returncode == 0
    assert r.stdout == "" and r.stderr == ""
