"""Official catalog protocols: fixed hosts, bounded pagination, unknown prices."""
from __future__ import annotations

import re
from typing import Any, Callable
from urllib.parse import urlencode

PROVIDERS = ("cloudflare", "cohere", "ollama")
SECRET_ENV = {"cloudflare": ("CLOUDFLARE_API_TOKEN",), "cohere": ("COHERE_API_KEY",), "ollama": ("OLLAMA_API_KEY",)}
ENDPOINTS = {
    "cloudflare": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/models/search",
    "cohere": "https://api.cohere.com/v1/models",
    "ollama": "https://ollama.com/api/tags",
}
MAX_PAGES = 20


def endpoint(provider: str, account_id: str | None = None) -> str:
    if provider not in ENDPOINTS:
        raise ValueError("unsupported_provider")
    if provider == "cloudflare":
        if not isinstance(account_id, str) or re.fullmatch(r"[0-9a-fA-F]{32}", account_id) is None:
            raise ValueError("invalid_account_id")
        return ENDPOINTS[provider].format(account_id=account_id)
    return ENDPOINTS[provider]


def normalize_models(provider: str, body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        raise ValueError("invalid_response_shape")
    if provider == "cloudflare":
        # format=openrouter is documented; IDs are invocation identities, not UUIDs.
        items = body.get("data")
    elif provider in ("cohere", "ollama"):
        items = body.get("models")
    else:
        raise ValueError("unsupported_provider")
    if not isinstance(items, list) or any(not isinstance(x, dict) for x in items):
        raise ValueError("invalid_response_shape")
    output, seen = [], set()
    for item in items:
        model_id = item.get("id") if provider == "cloudflare" else item.get("name")
        if not isinstance(model_id, str) or not model_id.strip() or any(ord(c) < 32 for c in model_id):
            raise ValueError("invalid_model")
        if model_id in seen:
            continue
        seen.add(model_id)
        output.append({"provider": provider, "id": model_id, "name": item.get("name"),
                       "pricing": {}, "pricing_classification": "unknown", "access_classification": "catalog_pricing_only",
                       "access_source": None, "access_source_observed": None, "cadence": "catalog", "free_suffix": False,
                       "context_length": item.get("context_length") if isinstance(item.get("context_length"), int) and not isinstance(item.get("context_length"), bool) and item["context_length"] > 0 else None,
                       "max_output_tokens": None, "raw_source": f"{provider}:official_catalog"})
    return output


def poll(provider: str, token: str, get_json: Callable, account_id: str | None = None) -> tuple[list[dict], dict]:
    base = endpoint(provider, account_id)
    rows, headers, seen, seen_pages = [], {}, set(), set()
    next_token = None
    for page in range(1, MAX_PAGES + 1):
        params = {}
        if provider == "cohere":
            params = {"page_size": 1000, "endpoint": "chat"}
            if next_token is not None:
                params["page_token"] = next_token
        elif provider == "cloudflare":
            params = {"format": "openrouter", "page": page, "per_page": 100}
        url = base + ("?" + urlencode(params) if params else "")
        body, response_headers = get_json(url, token)
        headers.update(response_headers)
        batch = normalize_models(provider, body)
        for row in batch:
            if row['id'] not in seen:
                rows.append(row)
                seen.add(row['id'])
        if provider == "ollama" or (provider == "cloudflare" and len(body['data']) < 100):
            return rows, headers
        if provider == "cloudflare":
            identities = tuple(row['id'] for row in batch)
            if identities in seen_pages:
                raise ValueError("invalid_pagination")
            seen_pages.add(identities)
            continue
        next_token = body.get("next_page_token")
        if next_token in (None, ""):
            return rows, headers
        if not isinstance(next_token, str) or len(next_token) > 2048 or next_token in seen_pages or any(ord(c) < 32 for c in next_token):
            raise ValueError("invalid_pagination")
        seen_pages.add(next_token)
    raise ValueError("invalid_pagination")
