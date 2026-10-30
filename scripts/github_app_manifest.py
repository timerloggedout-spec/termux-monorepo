#!/usr/bin/env python3
"""GitHub App creation, the programmatic route: the App Manifest flow.

GitHub has NO REST endpoint that creates an app from nothing. The manifest
flow is the programmatic bootstrap:
  1. POST a manifest (form field `manifest`, urlencoded) to
     https://github.com/settings/apps/new — the ONE step that needs an
     authenticated web session (any signed-in tab; a single Create click).
  2. GitHub redirects to the manifest's redirect_url with ?code=<temporary>.
  3. POST https://api.github.com/app-manifests/{code}/conversions
     (unauthenticated, code is single-use, ~15 min) -> returns id, slug,
     client_id, client_secret, webhook_secret and a freshly generated
     private key (pem). From here EVERYTHING is API (see GITHUB-APP-ROUTES).

stdin-driven modes:
  form    : manifest JSON on stdin -> HTML submission form on stdout.
  serve   : manifest JSON on stdin -> localhost server: GET / serves the
            form, GET /callback catches the code and converts immediately.
            Env: APP_OUT_DIR (default ./app-out) receives 0600 secret files.
  convert : conversion code on stdin -> conversion POST; prints ONLY
            non-secret ids (id, slug, client_id); secrets land in
            APP_OUT_DIR as 0600 files (app.pem, client_secret.txt,
            webhook_secret.txt) whose paths are printed, values never.
"""
import html
import json
import os
import sys
import urllib.request

SETTINGS_NEW = "https://github.com/settings/apps/new"
CONVERSIONS = "https://api.github.com/app-manifests/{code}/conversions"


def form_html(manifest: dict) -> str:
    m = html.escape(json.dumps(manifest), quote=True)
    return ("<!doctype html><meta charset=utf-8><title>Create GitHub App</title>"
            f'<form action="{SETTINGS_NEW}" method="post">'
            f'<input type="hidden" name="manifest" value="{m}">'
            '<button type="submit">Create GitHub App from manifest</button>'
            "</form>")


def convert(code: str) -> dict:
    req = urllib.request.Request(
        CONVERSIONS.format(code=code.strip()), method="POST",
        headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def store(result: dict) -> dict:
    out = os.environ.get("APP_OUT_DIR", "./app-out")
    os.makedirs(out, mode=0o700, exist_ok=True)
    files = {}
    for key, fname in (("pem", "app.pem"),
                       ("client_secret", "client_secret.txt"),
                       ("webhook_secret", "webhook_secret.txt")):
        if result.get(key):
            path = os.path.join(out, fname)
            with open(path, "w") as fh:
                fh.write(result[key])
            os.chmod(path, 0o600)
            files[key] = path
    return {"id": result["id"], "slug": result["slug"],
            "name": result["name"], "client_id": result["client_id"],
            "owner": result["owner"]["login"], "secret_files": files,
            "install_url": f"https://github.com/apps/{result['slug']}/installations/new"}


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "form"
    if mode == "form":
        print(form_html(json.load(sys.stdin)))
        return 0
    if mode == "convert":
        print(json.dumps(store(convert(sys.stdin.read())), indent=1))
        return 0
    if mode == "serve":
        from http.server import BaseHTTPRequestHandler, HTTPServer
        manifest = json.load(sys.stdin)
        port = int(os.environ.get("APP_PORT", "8765"))
        if "redirect_url" not in manifest:
            manifest["redirect_url"] = f"http://localhost:{port}/callback"

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith("/callback"):
                    from urllib.parse import urlparse, parse_qs
                    code = parse_qs(urlparse(self.path).query)["code"][0]
                    result = store(convert(code))
                    self.send_response(200); self.end_headers()
                    self.wfile.write(json.dumps(result, indent=1).encode())
                    print(json.dumps(result, indent=1), flush=True)
                else:
                    self.send_response(200); self.end_headers()
                    self.wfile.write(form_html(manifest).encode())

            def log_message(self, *a):
                pass

        print(f"open http://localhost:{port}/ and click Create once",
              file=sys.stderr, flush=True)
        HTTPServer(("127.0.0.1", port), H).serve_forever()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
