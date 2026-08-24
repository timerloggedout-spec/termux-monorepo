#!/usr/bin/env python3
"""Poll live provider model catalogs and normalize free/zero-price candidates.

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

UA = "termux-monorepo-provider-catalog/3"
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

# Explicit provider documentation is allowed to augment a catalog, but is
# never allowed to overwrite live pricing evidence. Felo currently documents
# OX Alpha as a free-trial model with public model id `ox-alpha` and 128K max
# output. This is an access classification, not a claim about account quota.
DOCUMENTED_TRIAL_MODELS = {
    ("felo", "ox-alpha"): {
        "access_classification": "free_trial",
        "source": "https://openapi.felo.ai/models/stealth/ox-alpha",
        "source_observed": "2026-08-24",
    }
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
            "context_length": item.get("context_length"),
            "raw_source": f"{provider}:/v1/models",
        })

    # Some provider documentation can advertise a trial route even when the
    # catalog omits it. Keep it as an explicit, provenance-bearing candidate.
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
            "context_length": 1_000_000,
            "max_output_tokens": 128_000,
            "raw_source": f"{provider}:/v1/models + documented-model-page",
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
        "schema": "provider-model-catalog/v3",
        "observed_at": observed_at,
        "providers": providers,
        "promotion": {
            "status": "observe_only",
            "expiry": None,
            "source": None,
            "note": "Promotion/quota expiry must be refreshed from authoritative provider evidence; model-page trial status is separate from account-level daily quota.",
        },
        "models": rows,
        "errors": errors,
    }
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(document, fh, indent=2, sort_keys=True)
        fh.write("\n")

    free = [r for r in rows if r["pricing_classification"] == "free_zero_price" or r["free_suffix"] or r["access_classification"] == "free_trial"]
    print(f"catalog_models={len(rows)} free_or_zero_or_trial={len(free)} errors={len(errors)}")
    for row in free:
        print(f"FREE/TRIAL {row['provider']}/{row['id']} [{row['access_classification']}]")
    return 0 if rows or not providers else 1


if __name__ == "__main__":
    raise SystemExit(main())
