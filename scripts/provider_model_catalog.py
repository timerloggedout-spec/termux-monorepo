#!/usr/bin/env python3
"""Poll provider model catalogs and normalize free/zero-price candidates.

No model is hardcoded as a routing rule. Provider catalogs are evidence; the
scheduler may select from them. Pricing is classified conservatively:
OpenRouter exposes prompt/completion pricing, while Felo's public model
catalog may omit pricing, so those entries remain `unknown` rather than being
mislabelled free.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request


UA = "termux-monorepo-provider-catalog/1"


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


def openrouter(token: str) -> list[dict]:
    payload = get_json("https://openrouter.ai/api/v1/models", token)
    rows = []
    for item in payload.get("data", []):
        rows.append({
            "provider": "openrouter",
            "id": item.get("id"),
            "name": item.get("name"),
            "pricing": item.get("pricing") or {},
            "pricing_classification": price_classification(item),
            "free_suffix": str(item.get("id", "")).endswith(":free"),
            "context_length": item.get("context_length"),
            "raw_source": "openrouter:/api/v1/models",
        })
    return rows


def felo(token: str) -> list[dict]:
    payload = get_json("https://openapi.felo.ai/api/v1/models", token)
    rows = []
    for item in payload.get("data", []):
        rows.append({
            "provider": "felo",
            "id": item.get("id"),
            "name": item.get("name"),
            "pricing": item.get("pricing") or {},
            "pricing_classification": price_classification(item),
            "free_suffix": str(item.get("id", "")).endswith(":free"),
            "context_length": item.get("context_length"),
            "raw_source": "felo:/api/v1/models",
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", default="openrouter,felo")
    parser.add_argument("--output", default="/tmp/model-catalog/catalog.json")
    args = parser.parse_args()

    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows: list[dict] = []
    errors: list[dict] = []
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]

    for provider in providers:
        env_name = {"openrouter": "OPENROUTER_API_KEY", "felo": "FELO_AI_API"}.get(provider)
        token = os.environ.get(env_name or "")
        if not token:
            errors.append({"provider": provider, "error": "missing_secret", "secret_env": env_name})
            continue
        try:
            rows.extend(openrouter(token) if provider == "openrouter" else felo(token))
        except Exception as exc:  # catalog polling must remain observable
            errors.append({"provider": provider, "error": type(exc).__name__, "message": str(exc)[:500]})

    document = {
        "schema": "provider-model-catalog/v1",
        "observed_at": observed_at,
        "providers": providers,
        "promotion": {
            "status": "observe_only",
            "expiry": None,
            "source": None,
            "note": "Do not hardcode promotional expiry; populate only from an authoritative provider announcement/API observation.",
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
