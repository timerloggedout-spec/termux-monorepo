#!/usr/bin/env python3
"""HTTP bridge: Termux <-> Firefox Tampermonkey for Mistral"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, sys, threading, time, os
from pathlib import Path

PORT = 9876
prompt_queue = None
response_data = None
response_event = threading.Event()
token_file = Path.home() / ".multi-ai-tokens" / "mistral_token.txt"

def _write_token_securely(token: str, target_file: Path = token_file) -> None:
    parent = target_file.parent
    if parent.is_symlink():
        raise ValueError(f"Symlink token directory rejected for security: {parent}")
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if target_file.is_symlink():
        raise ValueError(f"Symlink token file rejected for security: {target_file}")

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(target_file, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(token)

class BridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global prompt_queue, response_data
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        data = json.loads(body)
        if data.get("type") == "token":
            _write_token_securely(data["token"])
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
            print("[bridge] Token saved")
        elif data.get("type") == "prompt":
            prompt_queue = data["text"]
            response_event.clear()
            # Wait for response from the browser (polling)
            for _ in range(240):  # wait up to 120 seconds
                if response_event.is_set():
                    break
                time.sleep(0.5)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response_data or ""}).encode())
        elif data.get("type") == "response":
            response_data = data["text"]
            response_event.set()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
        else:
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        if self.path == "/poll":
            # Browser polls for new prompts
            if prompt_queue and not response_event.is_set():
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"prompt": prompt_queue}).encode())
                # Keep prompt until response received
            else:
                self.send_response(204)  # No content
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[bridge] {args[0]}")

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), BridgeHandler)
    print(f"[bridge] HTTP bridge on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
