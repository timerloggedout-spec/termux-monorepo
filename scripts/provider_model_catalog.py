#!/usr/bin/env python3
"""Poll live provider model catalogs and normalize access/quota evidence.

Catalog state is evidence, not routing policy. Provider model pages may expose
free-trial/account-entitled routes that are not represented by /v1/models
pricing, so those routes are recorded separately with explicit provenance.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import urllib.request

UA = "termux-monorepo-provider-catalog/4"
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
DOCUMENTED_TRIAL_MODELS = {
    ("felo", "ox-alpha"): {
        "access_classification": "free_trial",
        "source": "https://openapi.felo.ai/models/stealth/ox-alpha",
        "source_observed": "2026-08-24",
        "max_output_tokens": 128_000,
        "context_length": 1_000_000,
    }
}


def get_json(url: str, token: str | None = None) -> tuple[dict, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as response:
        # Preserve only operational quota/rate-limit metadata; never persist auth headers.
        headers = {}
        for key, value in response.headers.items():
            lower = key.lower()
            if lower.startswith(("x-ratelimit-", "x-credit-", "x-quota-", "x-remaining-", "x-usage-")) or lower in {"retry-after", "x-request-id"}:
                headers[lower] = value
        return json.load(response), headers


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


def poll(provider: str, token: str) -> tuple[list[dict], dict]:
    payload, response_headers = get_json(ENDPOINTS[provider], token)
    rows = []
    seen: set[str] = set()
    for item in payload.get("data", []):
        model_id = item.get("id")
        if not model_id:
            continue
        seen.add(model_id)
        trial = DOCUMENTED_TRIAL_MODELS.get((provider, model_id), {})
        rows.append({
            "provider": provider,
            "id": model_id,
            "name": item.get("name"),
            "pricing": item.get("pricing") or {},
            "pricing_classification": price_classification(item),
            "access_classification": trial.get("access_classification", "catalog_pricing_only"),
            "access_source": trial.get("source"),
            "access_source_observed": trial.get("source_observed"),
            "free_suffix": str(model_id).endswith(":free"),
            # Provider catalogs are authoritative when present; documented
            # trial metadata fills gaps rather than overriding live evidence.
            "context_length": item.get("context_length") or trial.get("context_length"),
            "max_output_tokens": item.get("max_output_tokens") or trial.get("max_output_tokens"),
            "raw_source": f"{provider}:/v1/models",
        })
    for (trial_provider, model_id), trial in DOCUMENTED_TRIAL_MODELS.items():
        if trial_provider != provider or model_id in seen:
            continue
        rows.append({
            "provider": provider,
            "id": model_id,
            "name": "OX Alpha",
            "pricing": {},
            "pricing_classification": "unknown",
            "access_classification": trial["access_classification"],
            "access_source": trial["source"],
            "access_source_observed": trial["source_observed"],
            "free_suffix": False,
            "context_length": trial["context_length"],
            "max_output_tokens": trial["max_output_tokens"],
            "raw_source": f"{provider}:/v1/models + documented-model-page",
        })
    return rows, response_headers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", default="openrouter,felo,omni")
    parser.add_argument("--output", default="/tmp/model-catalog/catalog.json")
    args = parser.parse_args()

    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows: list[dict] = []
    errors: list[dict] = []
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    provider_observations: dict[str, dict] = {}

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
            provider_rows, headers = poll(provider, token)
            rows.extend(provider_rows)
            provider_observations[provider] = {
                "catalog_observed_at": observed_at,
                "response_headers": headers,
                "account_endpoint": None,
                "account_endpoint_status": "not_documented",
                "quota_note": "Account-level balance/quota is not asserted unless exposed by an authoritative provider endpoint or response metadata.",
            }
        except Exception as exc:
            errors.append({"provider": provider, "error": type(exc).__name__, "message": str(exc)[:500]})

    document = {
        "schema": "provider-model-catalog/v4",
        "observed_at": observed_at,
        "providers": providers,
        "promotion": {
            "status": "observe_only",
            "expiry": None,
            "source": None,
            "note": "Promotion/quota expiry must be refreshed from authoritative provider evidence; model-page trial status is separate from account-level daily quota.",
        },
        "provider_observations": provider_observations,
        "models": rows,
        "errors": errors,
    }
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(document, fh, indent=2, sort_keys=True)
        fh.write("\n")

    eligible = [r for r in rows if r["pricing_classification"] == "free_zero_price" or r["free_suffix"] or r["access_classification"] == "free_trial"]
    print(f"catalog_models={len(rows)} eligible_free_zero_trial={len(eligible)} errors={len(errors)}")
    for provider, observation in provider_observations.items():
        print(f"ACCOUNT_METADATA {provider}: {json.dumps(observation['response_headers'], sort_keys=True)}")
    for row in eligible:
        print(f"ELIGIBLE {row['provider']}/{row['id']} [{row['access_classification']}; max_output={row.get('max_output_tokens')}; context={row.get('context_length')}]")
    return 0 if rows or not providers else 1


if __name__ == "__main__":
    raise SystemExit(main())
