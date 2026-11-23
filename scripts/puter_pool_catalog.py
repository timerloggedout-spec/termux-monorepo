#!/usr/bin/env python3
"""Harvest the locally hosted Puter Pool model catalog into the provider catalog contract.

The Puter Pool depot is an operator-owned local service. This reader only calls
GET /v1/models, accepts loopback HTTP(S) endpoints, and emits model metadata.
It never reads account tokens, account lists, balances, request history, or chat
payloads. Catalog visibility is discovery evidence, not inference admission.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "http://127.0.0.1:3000"
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
UA = "termux-monorepo-puter-pool-catalog/1"


def _catalog_url(base_url: str) -> str:
    parsed = urllib.parse.urlsplit(base_url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or host not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("puter_pool_endpoint_must_be_loopback")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("invalid_puter_pool_endpoint")
    if parsed.path not in {"", "/"}:
        raise ValueError("base_url_must_be_origin_only")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "/v1/models", "", ""))


def fetch_models(base_url: str, timeout: float = 8.0) -> list[dict[str, Any]]:
    url = _catalog_url(base_url)
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": UA})
    opener = urllib.request.build_opener(urllib.request.HTTPHandler(), urllib.request.HTTPSHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"puter_pool_http_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("puter_pool_unreachable") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("puter_pool_response_too_large")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("puter_pool_invalid_json") from None
    items = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise RuntimeError("puter_pool_invalid_response_shape")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        model_id = item.get("id")
        if not isinstance(model_id, str) or not model_id or len(model_id) > 256:
            continue
        if any(ord(ch) < 32 for ch in model_id) or model_id in seen:
            continue
        seen.add(model_id)
        rows.append({
            "provider": "g4f/Puter",
            "id": model_id,
            "name": item.get("name") if isinstance(item.get("name"), str) else None,
            "pricing": {},
            "pricing_classification": "unknown",
            "access_classification": "catalog_only",
            "entitlement_verification": "unknown",
            "cadence": "unknown",
            "free_suffix": False,
            "context_length": item.get("context_length") if isinstance(item.get("context_length"), int) else None,
            "max_output_tokens": item.get("max_output_tokens") if isinstance(item.get("max_output_tokens"), int) else None,
            "raw_source": "puter-pool-local:/v1/models",
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.environ.get("PUTER_POOL_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--output", default="/tmp/provider-catalog/puter-pool.json")
    parser.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args(argv)
    if not 0.1 <= args.timeout <= 30:
        parser.error("--timeout must be between 0.1 and 30 seconds")
    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows = fetch_models(args.base_url, args.timeout)
    document = {
        "schema": "provider-model-catalog/v5",
        "observed_at": observed_at,
        "providers": ["g4f/Puter"],
        "cadence_classes": ["hourly", "daily", "weekly", "monthly", "trial", "catalog", "unknown"],
        "promotion": {"status": "observe_only", "expiry": None, "note": "Catalog discovery never grants entitlement or inference admission."},
        "provider_observations": {"g4f/Puter": {"catalog_observed_at": observed_at, "catalog_authentication": "local_operator_service", "catalog_contract_source": "puter-pool-local-openai-compatible-api", "quota_manager": {"status": "unknown", "remaining": None, "reset": None}}},
        "models": rows,
        "errors": [],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".puter-pool-", suffix=".tmp", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, indent=2, sort_keys=True)
            stream.write(chr(10))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, output)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print(f"provider=g4f/Puter catalog_models={len(rows)} entitlement=unknown inference=not_invoked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
