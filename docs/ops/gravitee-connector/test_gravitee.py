#!/usr/bin/env python3
"""Mock-mAPI integration test for gravitee.py. Stubs the credential module
(test-token only, never a real credential) and serves documented v2 shapes
from a local HTTP server. Asserts paths, Bearer auth, write guard."""
import importlib.util, json, sys, threading, types
from http.server import BaseHTTPRequestHandler, HTTPServer

stub = types.ModuleType("dynamic_credentials")
def add_surrogate_to_request(req, provider, allowed_hosts=None):
    assert provider == "custom.gravitee"
    req.add_header("Authorization", "Bearer test-token")
def read_json_response(resp):
    return json.loads(resp.read().decode() or "{}")
stub.add_surrogate_to_request = add_surrogate_to_request
stub.read_json_response = read_json_response
sys.modules["dynamic_credentials"] = stub

seen = []
class H(BaseHTTPRequestHandler):
    def _reply(self):
        seen.append((self.command, self.path, self.headers.get("Authorization")))
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if body: seen.append(("BODY", body.decode()))
        out = {"id": "x1", "name": "mock"}
        if self.path.endswith("/apis") and self.command == "GET":
            out = {"data": [{"id": "a1", "name": "Echo API"}]}
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.end_headers(); self.wfile.write(json.dumps(out).encode())
    do_GET = do_POST = do_PUT = do_DELETE = _reply
    def log_message(self, *a): pass

srv = HTTPServer(("127.0.0.1", 0), H); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://localhost:{port}/management/v2"

spec = importlib.util.spec_from_file_location("gravitee", sys.argv[1])
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

def run(argv):
    sys.argv = ["gravitee.py"] + argv
    try: g.main()
    except SystemExit as e: return e.code
    return 0

import io, contextlib
def cap(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): code = run(argv)
    return code, buf.getvalue()

fails = []
code, out = cap(["--base-url", BASE, "ping"]);        assert code == 0 and '"x1"' in out, out
code, out = cap(["--base-url", BASE, "apis"]);        assert code == 0 and "Echo API" in out
code, out = cap(["--base-url", BASE, "api", "a1"]);   assert code == 0
code, out = cap(["--base-url", BASE, "api-start", "a1"]); assert code == 3, code  # write guard
code, out = cap(["--base-url", BASE, "api-start", "a1", "--yes"]); assert code == 0
code, out = cap(["--base-url", BASE, "plan-publish", "a1", "pl1", "--yes"]); assert code == 0
code, out = cap(["mcp-config", "--base-url", BASE]);  assert "@gravitee/apim-mcp-server" in out and "test-token" not in out
code, out = cap(["ping"]);                            assert code == 2  # BLOCKED, no base
paths = [p for m, p, a in seen if m in ("GET", "POST")]
expect = ["/management/v2/organizations/DEFAULT",
          "/management/v2/organizations/DEFAULT/environments/DEFAULT/apis",
          "/management/v2/organizations/DEFAULT/environments/DEFAULT/apis/a1",
          "/management/v2/organizations/DEFAULT/environments/DEFAULT/apis/a1/_start",
          "/management/v2/organizations/DEFAULT/environments/DEFAULT/apis/a1/plans/pl1/_publish"]
assert paths == expect, paths
assert all(a == "Bearer test-token" for m, p, a in seen if m in ("GET", "POST"))
print(f"MOCK-TEST PASS: {len(seen)} calls, paths+auth+guards verified")
srv.shutdown()
