"""catalog-api: read-only blueprint catalog service (Platform201 Pilot 1).

Bounded per plan §6.4: GET-only, no writes, no external calls, no model
calls. Serves the bundled blueprints.json catalog. Stdlib only.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "blueprints.json").read_text())
BY_ID = {b["id"]: b for b in DATA["blueprints"]}


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "ok", "service": "catalog-api"})
        elif self.path == "/blueprints":
            self._json(200, DATA)
        elif self.path.startswith("/blueprints/"):
            entry = BY_ID.get(self.path[len("/blueprints/"):])
            if entry:
                self._json(200, entry)
            else:
                self._json(404, {"error": "not_found"})
        else:
            self._json(404, {"error": "not_found"})

    def do_POST(self):
        self._json(405, {"error": "writes_disabled"})

    do_PUT = do_DELETE = do_PATCH = do_POST

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
