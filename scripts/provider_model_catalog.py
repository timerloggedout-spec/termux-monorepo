#!/usr/bin/env python3
"""Poll live provider model catalogs and normalize free/zero-price candidates.

Catalog state is evidence, not routing policy. Promotional/account-level quota
is never inferred from a public price field alone.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request

UA = "termux-monorepo-provider-catalog/2"
ENDPOINTS = {
    "openrouter": "https://openrouter.ai/api/v1/models",
    "felo": "https://openapi.felo.ai/api/v1/models",
    "omni": "https://cloud.omniroute.online/v1/models",
}
SECRETS = {
    "openrouter": "OPENROUTER_API_KEY",
    "felo": "FELO_AI_API",
    "omni": "OMNI_API_KEY",
}


def get_json(url: str, token: str | None = None) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def price_classification(data: dict) -> str:
    pricing = data.get("pricing") or {}
    try:
        prompt = float(pricing.get("prompt", "nan"))
        completion = float(pricing.get("completion", "nan"))
    except (TypeError, ValueError):
        return "unknown"
    if prompt == 0 and completion == 0:
        return "free_zero_price"
    if prompt >= 0 and completion >= 0:
        return "paid"
    return "unknown"


def poll(provider: str, token: str) -> list[dict]:
    payload = get_json(ENDPOINTS[provider], token)
    rows = []
    for item in payload.get("data", []):
        model_id = item.get("id")
        if not model_id:
            continue
        rows.append({
            "provider": provider,
            "id": model_id,
            "name": item.get("name"),
            "pricing": item.get("pricing") or {},
            "pricing_classification": price_classification(item),
            "free_suffix": str(model_id).endswith(":free"),
            "context_length": item.get("context_length"),
            "raw_source": f"{provider}:/v1/models",
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", default="openrouter,felo,omni")
    parser.add_argument("--output", default="/tmp/model-catalog/catalog.json")
    args = parser.parse_args()

    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows: list[dict] = []
    errors: list[dict] = []
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]

    for provider in providers:
        env_name = SECRETS.get(provider)
        if provider not in ENDPOINTS:
            errors.append({"provider": provider, "error": "unsupported_provider"})
            continue
        token = os.environ.get(env_name or "")
        if not token:
            errors.append({"provider": provider, "error": "missing_secret", "secret_env": env_name})
            continue
        try:
            rows.extend(poll(provider, token))
        except Exception as exc:
            errors.append({"provider": provider, "error": type(exc).__name__, "message": str(exc)[:500]})

    document = {
        "schema": "provider-model-catalog/v2",
        "observed_at": observed_at,
        "providers": providers,
        "promotion": {
            "status": "observe_only",
            "expiry": None,
            "source": None,
            "note": "Populate expiry only from an authoritative provider announcement/API observation; never hardcode promotional expiry.",
        },
        "models": rows,
        "errors": errors,
    }
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(document, fh, indent=2, sort_keys=True)
        fh.write("\n")

    free = [r for r in rows if r["pricing_classification"] == "free_zero_price" or r["free_suffix"]]
    print(f"catalog_models={len(rows)} free_or_zero={len(free)} errors={len(errors)}")
    for row in free:
        print(f"FREE {row['provider']}/{row['id']}")
    return 0 if rows or not providers else 1


if __name__ == "__main__":
    sys.exit(main())
