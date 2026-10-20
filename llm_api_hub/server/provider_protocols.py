"""Pure helpers for the official account-scoped Cloudflare and Cohere APIs.

The caller owns exact-model admission and bounded, redirect-refusing transport.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

PROVIDER_KEYS = ("cloudflare", "cohere", "ollama")
SECRET_ENV = {"cloudflare": ("CLOUDFLARE_API_TOKEN",), "cohere": ("COHERE_API_KEY",), "ollama": ("OLLAMA_API_KEY",)}
CHAT_ENDPOINTS = {
    "cloudflare": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions",
    "cohere": "https://api.cohere.com/v2/chat",
    "ollama": "https://ollama.com/v1/chat/completions",
}


class ProtocolError(ValueError):
    """Fixed safe error codes only; never reflect upstream bodies."""


def validate_cloudflare_account_id(value: Any) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-fA-F]{32}", value) is None:
        raise ProtocolError("invalid_account_id")
    return value


def cloudflare_chat_url(account_id: str) -> str:
    return CHAT_ENDPOINTS["cloudflare"].format(account_id=validate_cloudflare_account_id(account_id))


def build_chat_request(provider: str, model: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    if provider not in PROVIDER_KEYS or not isinstance(payload, Mapping) or payload.get("model") != model:
        raise ProtocolError("invalid_request")
    if provider != "cohere":
        return dict(payload)
    if not isinstance(payload.get("messages"), list):
        raise ProtocolError("invalid_request")
    result = {k: v for k, v in payload.items() if k in {
        "messages", "max_tokens", "temperature", "seed", "frequency_penalty", "presence_penalty",
    }}
    result.update(model=model, stream=False)
    if "stop" in payload:
        result["stop_sequences"] = payload["stop"] if isinstance(payload["stop"], list) else [payload["stop"]]
    if "top_p" in payload:
        result["p"] = payload["top_p"]
    return result


def normalize_chat_response(provider: str, body: Any, model: str) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise ProtocolError("invalid_response_shape")
    if provider != "cohere":
        if provider not in PROVIDER_KEYS or not isinstance(body.get("choices"), list) or not body["choices"] or not all(isinstance(c, dict) for c in body["choices"]):
            raise ProtocolError("invalid_response_shape")
        return body
    message = body.get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), list):
        raise ProtocolError("invalid_response_shape")
    chunks = [p["text"] for p in message["content"] if isinstance(p, dict) and p.get("type") == "text" and isinstance(p.get("text"), str)]
    if not chunks:
        raise ProtocolError("invalid_response_shape")
    reason = {"COMPLETE": "stop", "STOP_SEQUENCE": "stop", "MAX_TOKENS": "length"}.get(body.get("finish_reason"), "stop")
    return {"id": body.get("id", "cohere-chat"), "object": "chat.completion", "model": model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "".join(chunks)}, "finish_reason": reason}]}
