"""Offline-only, pure protocol helpers for reviewing Typhoon's chat contract.

This module deliberately has no transport, runtime registration, environment/key
lookup, or authorization-header construction. Legal review is still required.
Sources: https://docs.opentyphoon.ai/en/ ;
https://docs.opentyphoon.ai/en/faq/ ; https://docs.opentyphoon.ai/en/rate-limits/ ;
https://docs.opentyphoon.ai/en/api-reference/ ; https://opentyphoon.ai/tac
"""
from __future__ import annotations

from typing import Any, Mapping
import math
import re
from datetime import datetime

ENDPOINT = "https://api.opentyphoon.ai/v1/chat/completions"
MODELS = ("typhoon-v2.5-30b-a3b-instruct", "typhoon-v2.1-12b-instruct")
API_KEY_ENV_NAME = "OPENTYPHOON_API_KEY"  # Name only: never read here.
REQUEST_FIELDS = frozenset({
    "model", "messages", "max_tokens", "temperature", "top_p", "n",
    "stream", "stop", "presence_penalty", "frequency_penalty",
    "repetition_penalty", "user",
})


class TyphoonProtocolError(ValueError):
    """An error with a fixed safe code; untrusted values are never included."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _fail(code: str) -> None:
    raise TyphoonProtocolError(code)


def build_chat_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the conservative non-streaming text subset and return JSON body."""
    if not isinstance(payload, Mapping):
        _fail("invalid_request")
    if set(payload) - REQUEST_FIELDS:
        _fail("unsupported_property")
    model = payload.get("model")
    if not isinstance(model, str) or model not in MODELS:
        _fail("unsupported_model")
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        _fail("invalid_messages")
    normalized = []
    for message in messages:
        if not isinstance(message, Mapping) or set(message) != {"role", "content"}:
            _fail("invalid_message")
        if message.get("role") not in {"system", "user", "assistant"} or not isinstance(message.get("content"), str):
            _fail("invalid_message")
        normalized.append({"role": message["role"], "content": message["content"]})
    result: dict[str, Any] = {"model": model, "messages": normalized, "stream": False}
    for field in ("max_tokens", "n"):
        if field in payload:
            value = payload[field]
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                _fail("invalid_value")
            result[field] = value
    for field in ("temperature", "top_p", "presence_penalty", "frequency_penalty", "repetition_penalty"):
        if field in payload:
            value = payload[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                _fail("invalid_value")
            bounds = {
                "temperature": (0, 2), "top_p": (0, 1),
                "presence_penalty": (-2, 2), "frequency_penalty": (-2, 2),
                "repetition_penalty": (1, 2),
            }[field]
            if not bounds[0] <= value <= bounds[1]:
                _fail("invalid_value")
            result[field] = value
    if "stop" in payload:
        value = payload["stop"]
        if not (isinstance(value, str) or isinstance(value, list) and 1 <= len(value) <= 4 and all(isinstance(v, str) for v in value)):
            _fail("invalid_value")
        result["stop"] = value
    if "user" in payload:
        if not isinstance(payload["user"], str):
            _fail("invalid_value")
        result["user"] = payload["user"]
    if payload.get("stream", False) is not False:
        _fail("streaming_unsupported")
    return result


def normalize_chat_response(body: Any, requested_model: str) -> dict[str, Any]:
    """Validate OpenAI-shaped nonstream response and return a minimal safe form."""
    if not isinstance(requested_model, str) or requested_model not in MODELS:
        _fail("unsupported_model")
    if not isinstance(body, dict):
        _fail("invalid_response")
    if body.get("model") != requested_model:
        _fail("response_model_mismatch")
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        _fail("invalid_response")
    clean_choices = []
    seen_indices = set()
    for choice in choices:
        if not isinstance(choice, dict) or not isinstance(choice.get("index"), int) or isinstance(choice.get("index"), bool):
            _fail("invalid_response")
        if choice["index"] < 0 or choice["index"] in seen_indices:
            _fail("invalid_response")
        seen_indices.add(choice["index"])
        message = choice.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("role"), str) or message.get("role") != "assistant" or not isinstance(message.get("content"), str):
            _fail("invalid_response")
        reason = choice.get("finish_reason")
        if reason is not None and (not isinstance(reason, str) or reason not in ("stop", "length", "content_filter")):
            _fail("invalid_response")
        clean_choices.append({"index": choice["index"], "message": {"role": "assistant", "content": message["content"]}, "finish_reason": reason})
    usage = body.get("usage")
    clean_usage = None
    if usage is not None:
        if not isinstance(usage, dict) or any(isinstance(usage.get(k), bool) or not isinstance(usage.get(k), int) or usage[k] < 0 for k in ("prompt_tokens", "completion_tokens", "total_tokens")):
            _fail("invalid_response")
        if usage["total_tokens"] != usage["prompt_tokens"] + usage["completion_tokens"]:
            _fail("invalid_response")
        clean_usage = {k: usage[k] for k in ("prompt_tokens", "completion_tokens", "total_tokens")}
    result = {"object": "chat.completion", "model": requested_model, "choices": clean_choices}
    if isinstance(body.get("id"), str):
        result["id"] = body["id"]
    if clean_usage is not None:
        result["usage"] = clean_usage
    return result


def normalize_provider_error(status: int, body: Any) -> dict[str, Any]:
    """Return fixed errors and an ISO retry timestamp only for documented 429 shape."""
    if status == 429:
        out = {"code": "rate_limited"}
        if isinstance(body, dict):
            err = body.get("error")
            if isinstance(err, dict) and err.get("type") == "rate_limit_error" and err.get("code") == "rate_limit_exceeded":
                message = err.get("message")
                match = re.fullmatch(r"Rate limit exceeded\. Please retry after (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", message) if isinstance(message, str) else None
                if match:
                    timestamp = match.group(1)
                    try:
                        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        pass
                    else:
                        out["retry_hint"] = timestamp
        return out
    return {"code": "provider_error"}


def public_documentation_contract() -> dict[str, Any]:
    """Fresh evidence-backed contract. Documented free means $0, not credits."""
    return {
        "status": "offline_protocol_only",
        "endpoint": ENDPOINT,
        "method": "POST",
        "auth_scheme": "Bearer",
        "credential_env_name": API_KEY_ENV_NAME,
        "models": list(MODELS),
        "documented_public_rate_caps": {"requests_per_second": 5, "requests_per_minute": 200},
        "price_statement": "Official docs describe light usage and research showcase as free ($0); this does not establish credits or quota entitlement.",
        "quota_unknowns": ["daily reset", "account scope", "remaining quota headers", "retry hint semantics"],
        "context_and_output_caps": "unknown; tokens documentation says 8K for all models while overview says 128K/56K",
        "runtime_eligible": False,
        "live_state": "not checked; no request is sent",
        "legal_hold_reasons": [
            "Terms section 2 restricts personal data, training, competitive benchmarking and account sharing without written consent; bot wording is ambiguous.",
            "Terms section 4 grants a perpetual license over input content for training.",
            "No legal terms are accepted by this offline adapter.",
        ],
        "sources": [
            "https://docs.opentyphoon.ai/en/", "https://docs.opentyphoon.ai/en/faq/",
            "https://docs.opentyphoon.ai/en/rate-limits/", "https://docs.opentyphoon.ai/en/api-reference/",
            "https://docs.opentyphoon.ai/en/authentication/", "https://docs.opentyphoon.ai/en/tokens/",
            "https://opentyphoon.ai/tac",
        ],
    }
