#!/usr/bin/env python3
"""Minimal bounded HTTP adapter around Laya with optional bearer authentication.

Set LAYA_API_TOKEN in hosted environments to protect /decide. The health endpoint
is intentionally unauthenticated for platform health checks.
"""
from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from laya import Router

MAX_REQUEST_BYTES = 256 * 1024
API_TOKEN = os.getenv("LAYA_API_TOKEN", "")
router = Router(preload=os.getenv("LAYA_PRELOAD", "0").lower() in {"1", "true", "yes"})


class Handler(BaseHTTPRequestHandler):
    server_version = "LayaDecisionAdapter/1.1"
    sys_version = ""

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt: str, *args: Any) -> None:
        # Avoid logging request bodies, authorization headers, or user-provided paths.
        super().log_message("%s", "request handled")

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._json(200, {"ok": True, "engine": "laya", "mode": "system-one"})
        else:
            self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/decide":
            self._json(404, {"error": "not_found"})
            return
        if API_TOKEN:
            supplied = self.headers.get("Authorization", "")
            expected = "Bearer " + API_TOKEN
            if not hmac.compare_digest(supplied, expected):
                self._json(401, {"error": "unauthorized"})
                return
        elif os.getenv("LAYA_REQUIRE_AUTH", "0").lower() in {"1", "true", "yes"}:
            self._json(503, {"error": "auth_not_configured"})
            return

        try:
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                self._json(411, {"error": "content_length_required"})
                return
            size = int(raw_length)
            if size < 0:
                self._json(400, {"error": "invalid_content_length"})
                return
            if size > MAX_REQUEST_BYTES:
                self._json(413, {"error": "request_too_large"})
                return
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                self._json(400, {"error": "invalid_request"})
                return
            state, questions = body.get("state"), body.get("questions")
            if not isinstance(state, dict) or not isinstance(questions, dict) or not questions:
                self._json(400, {"error": "state_and_nonempty_questions_required"})
                return
            result = router.predict(state, questions)
            if not isinstance(result, dict):
                self._json(502, {"error": "invalid_engine_response"})
                return
            self._json(200, result)
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"error": "invalid_json_or_content_length"})
        except Exception:
            # Never return exception text or model/provider internals to callers.
            self._json(502, {"error": "decision_engine_error"})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "10000"))), Handler).serve_forever()
