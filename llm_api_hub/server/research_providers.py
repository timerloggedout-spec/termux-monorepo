"""Explicitly admitted native free-account inference providers."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

try:
    from llm_api_hub.server import provider_protocols
except ImportError:
    import provider_protocols  # type: ignore

SCHEMA = "research-provider-admission/v1"
ENDPOINTS = {
    "groq": ("https://api.groq.com/openai/v1/chat/completions", ("GROQ_API_KEY",)),
    "huggingface": ("https://router.huggingface.co/v1/chat/completions", ("HUGGINGFACE_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HF_API_TOKEN", "HF_TOKEN")),
    "cerebras": ("https://api.cerebras.ai/v1/chat/completions", ("CEREBRAS_API_KEY",)),
    "mistral": ("https://api.mistral.ai/v1/chat/completions", ("MISTRAL_API_KEY",)),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", ("GEMINI_API_KEY", "GOOGLE_API_KEY")),
    "nvidia": ("https://integrate.api.nvidia.com/v1/chat/completions", ("NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY")),
    "aion": ("https://api.aionlabs.ai/v1/chat/completions", ("AION_API_KEY",)),
    "llm7": ("https://api.llm7.io/v1/chat/completions", ("LLM7_API_TOKEN",)),
    "zai": ("https://api.z.ai/api/paas/v4/chat/completions", ("ZAI_API_KEY",)),
    "modelscope": ("https://api-inference.modelscope.ai/v1/chat/completions", ("MODELSCOPE_TOKEN",)),
    "siliconflow": ("https://api.siliconflow.com/v1/chat/completions", ("SILICONFLOW_API_KEY",)),
    "kilo": ("https://ai-gateway.kilo.ai/api/v1/chat/completions", ("KILO_API_KEY",)),
    "ovhcloud": ("https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions", ("OVHCLOUD_API_KEY",)),
    "sambanova": ("https://api.sambanova.ai/v1/chat/completions", ("SAMBANOVA_API_KEY",)),
}
ENDPOINTS.update({p: (provider_protocols.CHAT_ENDPOINTS[p], provider_protocols.SECRET_ENV[p]) for p in provider_protocols.PROVIDER_KEYS})
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class ProviderAdmissionError(Exception):
    def __init__(self, status: int, message: str, code: str, retry_after: str | None = None):
        self.status, self.message, self.code, self.retry_after = status, message, code, retry_after


def _policy() -> Mapping[str, Any]:
    path = os.environ.get("LLM_API_HUB_PROVIDER_POLICY")
    if not path:
        raise ProviderAdmissionError(403, "native research provider is not admitted", "provider_not_admitted")
    try:
        with Path(path).open(encoding="utf-8") as f:
            value = json.load(f)
    except (OSError, ValueError):
        raise ProviderAdmissionError(403, "native provider policy is unavailable or invalid", "provider_policy_invalid")
    if not isinstance(value, dict) or value.get("schema") != SCHEMA or not isinstance(value.get("entries"), list):
        raise ProviderAdmissionError(403, "native provider policy is unavailable or invalid", "provider_policy_invalid")
    return value


def _valid_model(model: Any) -> bool:
    return (isinstance(model, str) and bool(model) and model != "<model>" and
            not any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in model) and
            not any(c in model for c in "*?#\\") and
            all(part not in ("", ".", "..") for part in model.split("/")))


def _entry_valid(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    provider, model = entry.get("provider"), entry.get("model")
    return isinstance(provider, str) and provider in ENDPOINTS and _valid_model(model)


def admitted_models() -> list[str]:
    try:
        policy = _policy()
    except ProviderAdmissionError:
        return []
    entries = policy["entries"]
    identities = [(e.get("provider"), e.get("model")) for e in entries if _entry_valid(e)]
    # Any duplicate identity is ambiguous, so never let first/last entry win.
    duplicates = {identity for identity in identities if identities.count(identity) > 1}
    now, result = datetime.now(timezone.utc), []
    for entry in entries:
        if not _entry_valid(entry):
            continue
        provider, model = entry["provider"], entry["model"]
        if (provider, model) in duplicates or not any(os.environ.get(k) for k in ENDPOINTS[provider][1]):
            continue
        try:
            _validate_entry(entry, provider, model, now)
        except ProviderAdmissionError:
            continue
        result.append(f"{provider}/{model}")
    return result


def _validate_entry(entry: Mapping[str, Any], provider: str, model: str, now: datetime) -> None:
    if entry.get("provider") != provider or entry.get("model") != model:
        raise ProviderAdmissionError(403, "native provider model is not admitted", "provider_not_admitted")
    if entry.get("free_account_verified") is not True or entry.get("terms_accepted") is not True or entry.get("data_class") != "public":
        raise ProviderAdmissionError(403, "native provider admission requirements are not satisfied", "provider_not_admitted")
    for field in ("account_type", "plan", "account_status"):
        if field in entry:
            value = entry[field]
            if not isinstance(value, str) or value not in {"free", "free_tier", "free_account", "active_free"}:
                raise ProviderAdmissionError(403, "native provider account is not verified free", "provider_not_admitted")
    raw = entry.get("expires_at")
    if not isinstance(raw, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z", raw):
        raise ProviderAdmissionError(403, "native provider admission is expired or invalid", "provider_not_admitted")
    try:
        expires = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        raise ProviderAdmissionError(403, "native provider admission is expired or invalid", "provider_not_admitted")
    if expires <= now:
        raise ProviderAdmissionError(403, "native provider admission is expired or invalid", "provider_not_admitted")

    if provider == "cloudflare":
        try:
            provider_protocols.validate_cloudflare_account_id(os.environ.get("CLOUDFLARE_ACCOUNT_ID"))
        except provider_protocols.ProtocolError:
            raise ProviderAdmissionError(503, "native provider account is not configured", "provider_unconfigured")


def authorize(provider: str, model: str) -> str:
    if not isinstance(provider, str) or provider not in ENDPOINTS or not _valid_model(model):
        raise ProviderAdmissionError(403, "native provider model is not admitted", "provider_not_admitted")
    entries = _policy()["entries"]
    matches = [e for e in entries if isinstance(e, dict) and e.get("provider") == provider and e.get("model") == model]
    if len(matches) != 1:
        raise ProviderAdmissionError(403, "native provider model is not admitted", "provider_not_admitted")
    _validate_entry(matches[0], provider, model, datetime.now(timezone.utc))
    key = next((os.environ.get(k) for k in ENDPOINTS[provider][1] if os.environ.get(k)), None)
    if not key:
        raise ProviderAdmissionError(503, "native provider credential is not configured", "provider_unconfigured")
    return key


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def post_json(url: str, payload: dict[str, Any], key: str, timeout: float, *, response_provider: str | None = None, model: str = "") -> dict[str, Any]:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"})
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as res:
            body = res.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise ProviderAdmissionError(502, "native provider response is too large", "upstream_invalid_response")
            value = json.loads(body.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        retry = exc.headers.get("Retry-After") if exc.code == 429 else None
        if retry is not None and not re.fullmatch(r"\d{1,6}", retry):
            retry = None
        if exc.code == 429:
            raise ProviderAdmissionError(429, "native provider rate limit reached", "upstream_rate_limited", retry)
        if exc.code in (301, 302, 303, 307, 308):
            raise ProviderAdmissionError(502, "native provider redirect refused", "upstream_redirect")
        raise ProviderAdmissionError(502, "native provider request failed", "upstream_error")
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ProviderAdmissionError(502, "native provider is unreachable", "upstream_unreachable")
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProviderAdmissionError(502, "native provider returned invalid JSON", "upstream_invalid_response")
    if response_provider:
        try:
            value = provider_protocols.normalize_chat_response(response_provider, value, model)
        except provider_protocols.ProtocolError:
            raise ProviderAdmissionError(502, "native provider returned an invalid response", "upstream_invalid_response")
    if not isinstance(value, dict) or not isinstance(value.get("choices"), list) or not value["choices"]:
        raise ProviderAdmissionError(502, "native provider returned an invalid response", "upstream_invalid_response")
    return value


def complete(provider: str, model: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    key = authorize(provider, model)
    if not isinstance(payload, dict) or payload.get("model") != model:
        raise ProviderAdmissionError(403, "request model does not match admitted model", "provider_not_admitted")
    if provider == "cloudflare":
        return post_json(provider_protocols.cloudflare_chat_url(os.environ.get("CLOUDFLARE_ACCOUNT_ID")), payload, key, timeout)
    if provider == "cohere":
        try:
            payload = provider_protocols.build_chat_request(provider, model, payload)
        except provider_protocols.ProtocolError:
            raise ProviderAdmissionError(400, "invalid native provider request", "invalid_request")
        return post_json(ENDPOINTS[provider][0], payload, key, timeout, response_provider=provider, model=model)
    # URLs come only from the reviewed map; model identities stay in JSON bodies.
    return post_json(ENDPOINTS[provider][0], payload, key, timeout)
