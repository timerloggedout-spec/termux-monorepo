#!/usr/bin/env python3
"""
llm-api-hub standalone server (NO multi-ai-cli ChatDispatcher dependency).

Listens on :8787, speaks OpenAI Chat Completions.
Backends: OpenRouter | DeepSeek | Google native generateContent.
"""

from __future__ import annotations

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from uuid import uuid4

HOST = os.environ.get("LLM_API_HUB_HOST", "127.0.0.1")
PORT = int(os.environ.get("LLM_API_HUB_PORT", "8787"))
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE = os.environ.get("DEEPSEEK_BASE", "https://api.deepseek.com")
GOOGLE_AI_STUDIO_KEY = os.environ.get("GOOGLE_AI_STUDIO_KEY") or os.environ.get("GEMINI_API_KEY", "")
GOOGLE_NATIVE_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _json_response(handler: BaseHTTPRequestHandler, code: int, body: dict[str, Any]) -> None:
    data = json.dumps(body).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _http_json(method: str, url: str, headers: dict[str, str], payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def route_model(model: str) -> tuple[str, str]:
    m = (model or "hub/default").lower()
    if m.startswith("hub/"):
        m = m[4:]
    if "deepseek" in m:
        return "deepseek", m.replace("deepseek/", "") or "deepseek-chat"
    if "gemini" in m or "google" in m:
        return "google_native", m.replace("google/", "").replace("gemini/", "") or "gemini-2.5-flash"
    return "openrouter", m if "/" in m else f"openai/{m}" if m != "default" else "openai/gpt-4o-mini"


def openai_to_gemini_contents(messages: list[dict]) -> list[dict]:
    contents = []
    for msg in messages:
        role = msg.get("role", "user")
        if role == "system":
            role = "user"
        elif role == "assistant":
            role = "model"
        text = msg.get("content") or ""
        if isinstance(text, list):
            text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
        contents.append({"role": role, "parts": [{"text": str(text)}]})
    return contents


def gemini_to_openai_response(g: dict, model: str) -> dict:
    text = ""
    try:
        text = g["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        text = json.dumps(g)
    return {
        "id": f"chatcmpl-{uuid4().hex[:12]}",
        "object": "chat.completion",
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def dispatch_chat_completions(body: dict) -> dict:
    model = body.get("model") or "hub/default"
    backend, upstream = route_model(model)
    messages = body.get("messages") or []
    if backend == "openrouter":
        if not OPENROUTER_KEY:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://llm-api-hub.local"}
        return _http_json("POST", f"{OPENROUTER_BASE}/chat/completions", headers, {**body, "model": upstream})
    if backend == "deepseek":
        if not DEEPSEEK_KEY:
            raise RuntimeError("DEEPSEEK_API_KEY not set")
        headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
        return _http_json("POST", f"{DEEPSEEK_BASE}/chat/completions", headers, {**body, "model": upstream})
    if backend == "google_native":
        if not GOOGLE_AI_STUDIO_KEY:
            raise RuntimeError("GOOGLE_AI_STUDIO_KEY / GEMINI_API_KEY not set")
        url = f"{GOOGLE_NATIVE_BASE}/models/{upstream}:generateContent"
        headers = {"x-goog-api-key": GOOGLE_AI_STUDIO_KEY, "Content-Type": "application/json"}
        payload = {
            "contents": openai_to_gemini_contents(messages),
            "generationConfig": {
                "temperature": body.get("temperature", 1.0),
                "maxOutputTokens": body.get("max_tokens") or body.get("max_completion_tokens") or 2048,
            },
        }
        return gemini_to_openai_response(_http_json("POST", url, headers, payload), model)
    raise RuntimeError(f"Unknown backend for model={model}")


class HubHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(f"[hub] {self.address_string()} - {fmt % args}")

    def do_GET(self) -> None:
        if self.path in ("/health", "/v1/health"):
            _json_response(self, 200, {"status": "ok", "mode": "standalone", "port": PORT})
            return
        if self.path in ("/v1/models", "/models"):
            _json_response(self, 200, {"object": "list", "data": [
                {"id": "hub/default", "object": "model"},
                {"id": "hub/deepseek-chat", "object": "model"},
                {"id": "hub/gemini-2.5-flash", "object": "model"},
            ]})
            return
        _json_response(self, 404, {"error": {"message": "not found", "type": "invalid_request_error"}})

    def do_POST(self) -> None:
        if self.path not in ("/v1/chat/completions", "/chat/completions"):
            _json_response(self, 404, {"error": {"message": "not found", "type": "invalid_request_error"}})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            _json_response(self, 400, {"error": {"message": "invalid json", "type": "invalid_request_error"}})
            return
        try:
            _json_response(self, 200, dispatch_chat_completions(body))
        except Exception as e:
            _json_response(self, 502, {"error": {"message": str(e), "type": "upstream_error"}})


def main() -> None:
    server = HTTPServer((HOST, PORT), HubHandler)
    print(f"llm-api-hub STANDALONE listening on http://{HOST}:{PORT}")
    print("  mode: independent process (no ChatDispatcher)")
    print("  contract: OpenAI Chat Completions")
    print("  backends: openrouter | deepseek | google_native (generateContent)")
    server.serve_forever()


if __name__ == "__main__":
    main()
