#!/usr/bin/env python3
"""OpenAI-compatible local adapter for Google's Gemini Interactions API.

The existing standalone hub remains the generateContent path. This server adds
an Interactions API surface for stateful conversations and AI Studio observability.

Environment:
  GEMINI_API_KEY              required
  GEMINI_INTERACTIONS_HOST    default 127.0.0.1
  GEMINI_INTERACTIONS_PORT    default 8788
  GEMINI_INTERACTIONS_BASE    default https://generativelanguage.googleapis.com/v1beta
  GEMINI_INTERACTIONS_STORE   default false
  GEMINI_INTERACTIONS_MODEL   default gemini-flash-latest
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
import urllib.error
import urllib.request
from uuid import uuid4

HOST = os.environ.get("GEMINI_INTERACTIONS_HOST", "127.0.0.1")
PORT = int(os.environ.get("GEMINI_INTERACTIONS_PORT", "8788"))
API_KEY = os.environ.get("GEMINI_API_KEY", "")
BASE_URL = os.environ.get(
    "GEMINI_INTERACTIONS_BASE",
    "https://generativelanguage.googleapis.com/v1beta",
).rstrip("/")
DEFAULT_STORE = os.environ.get("GEMINI_INTERACTIONS_STORE", "false").lower() == "true"
DEFAULT_MODEL = os.environ.get("GEMINI_INTERACTIONS_MODEL", "gemini-flash-latest")


def _json_response(handler: BaseHTTPRequestHandler, code: int, body: dict[str, Any],
                   extra_headers: dict[str, str] | None = None) -> None:
    data = json.dumps(body).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    for key, value in (extra_headers or {}).items():
        handler.send_header(key, value)
    handler.end_headers()
    handler.wfile.write(data)


def _http_json(payload: dict[str, Any]) -> dict[str, Any]:
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")
    req = urllib.request.Request(
        f"{BASE_URL}/interactions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-goog-api-key": API_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini Interactions API HTTP {exc.code}: {detail}") from exc


def _messages_to_input(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        if isinstance(content, list):
            text = " ".join(
                str(part.get("text", ""))
                for part in content
                if isinstance(part, dict) and part.get("type") in (None, "text")
            ).strip()
        else:
            text = str(content)
        if role == "system":
            continue
        step_type = "model_output" if role == "assistant" else "user_input"
        steps.append({
            "type": step_type,
            "content": [{"type": "text", "text": text}],
        })
    return steps


def build_payload(body: dict[str, Any]) -> dict[str, Any]:
    model = body.get("model") or DEFAULT_MODEL
    if model.startswith("gemini-interactions/"):
        model = model[len("gemini-interactions/"):]

    messages = body.get("messages") or []
    system_messages = [
        str(m.get("content", ""))
        for m in messages
        if isinstance(m, dict) and m.get("role") == "system"
    ]
    previous_id = body.get("previous_interaction_id")
    store = body.get("store", DEFAULT_STORE)

    if previous_id and not store:
        raise ValueError("previous_interaction_id requires store=true")

    payload: dict[str, Any] = {
        "model": model,
        "input": _messages_to_input(messages) or str(body.get("input", "")),
        "store": bool(store),
    }

    if previous_id:
        payload["previous_interaction_id"] = str(previous_id)
    if system_messages:
        payload["system_instruction"] = "\n\n".join(system_messages)

    generation_config: dict[str, Any] = {}
    if body.get("max_tokens") is not None:
        generation_config["max_output_tokens"] = int(body["max_tokens"])
    if body.get("max_completion_tokens") is not None:
        generation_config["max_output_tokens"] = int(body["max_completion_tokens"])
    if body.get("thinking_level") is not None:
        generation_config["thinking_level"] = body["thinking_level"]
    if generation_config:
        payload["generation_config"] = generation_config

    labels = body.get("labels")
    if isinstance(labels, dict) and labels:
        payload["labels"] = labels

    return payload


def _extract_text(interaction: dict[str, Any]) -> str:
    chunks: list[str] = []
    for step in interaction.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for content in step.get("content", []):
            if isinstance(content, dict) and content.get("type") == "text":
                chunks.append(str(content.get("text", "")))
    return "".join(chunks)


def normalize_response(interaction: dict[str, Any], requested_model: str) -> dict[str, Any]:
    usage = interaction.get("usage") or {}
    return {
        "id": f"chatcmpl-{uuid4().hex[:12]}",
        "object": "chat.completion",
        "model": requested_model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": _extract_text(interaction)},
            "finish_reason": "stop"
            if interaction.get("status") == "completed"
            else interaction.get("status", "unknown"),
        }],
        "usage": {
            "prompt_tokens": int(usage.get("total_input_tokens", 0) or 0),
            "completion_tokens": int(usage.get("total_output_tokens", 0) or 0),
            "total_tokens": int(usage.get("total_tokens", 0) or 0),
        },
        "provider_metadata": {
            "provider": "google",
            "api": "interactions",
            "interaction_id": interaction.get("id"),
            "status": interaction.get("status"),
        },
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[gemini-interactions] {self.address_string()} - {fmt % args}")

    def do_GET(self) -> None:
        if self.path in ("/health", "/v1/health"):
            _json_response(self, 200, {
                "status": "ok",
                "provider": "google",
                "api": "interactions",
                "store_default": DEFAULT_STORE,
                "port": PORT,
            })
            return
        _json_response(self, 404, {"error": {"message": "not found"}})

    def do_POST(self) -> None:
        if self.path not in ("/v1/chat/completions", "/chat/completions"):
            _json_response(self, 404, {"error": {"message": "not found"}})
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
            if body.get("stream"):
                raise ValueError("streaming is not implemented by this adapter yet")
            if body.get("background"):
                raise ValueError("background interactions are not implemented by this adapter yet")
            payload = build_payload(body)
            interaction = _http_json(payload)
            normalized = normalize_response(interaction, body.get("model") or DEFAULT_MODEL)
            headers = {}
            if interaction.get("id"):
                headers["X-Gemini-Interaction-ID"] = str(interaction["id"])
            _json_response(self, 200, normalized, headers)
        except ValueError as exc:
            _json_response(self, 400, {"error": {"message": str(exc), "type": "invalid_request_error"}})
        except Exception as exc:
            _json_response(self, 502, {"error": {"message": str(exc), "type": "upstream_error"}})


def main() -> None:
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Gemini Interactions adapter listening on http://{HOST}:{PORT}")
    print("  provider: google")
    print("  api: interactions")
    print(f"  default store: {DEFAULT_STORE}")
    server.serve_forever()


if __name__ == "__main__":
    main()
