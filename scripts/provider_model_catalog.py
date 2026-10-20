#!/usr/bin/env python3
"""Poll live provider model catalogs and normalize access/quota evidence.

Catalog state is evidence, not routing policy. Provider model pages may expose
free-trial/account-entitled routes that are not represented by /v1/models
pricing, so those routes are recorded separately with explicit provenance.

Documented cadence entitlements (hourly/daily/weekly/monthly/trial) are
attached as metadata. They never invent remaining account balance.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import tempfile
import urllib.error
import urllib.request
from urllib.parse import urlencode

try:
    from scripts import provider_catalog_protocols
except ImportError:
    import provider_catalog_protocols  # type: ignore

UA = "termux-monorepo-provider-catalog/5"
# Catalog-only public GETs; ModelScope is verified by a current provider response,
# not a published catalog specification. Inference still requires account admission.
PUBLIC_CATALOGS = frozenset({"llm7", "ovhcloud", "modelscope"})
ENDPOINTS = {
    "openrouter": "https://openrouter.ai/api/v1/models",
    "felo": "https://openapi.felo.ai/api/v1/models",
    "omni": "https://cloud.omniroute.online/v1/models",
    "huggingface": "https://router.huggingface.co/v1/models",
    "groq": "https://api.groq.com/openai/v1/models",
    "mistral": "https://api.mistral.ai/v1/models",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
    "cerebras": "https://api.cerebras.ai/v1/models",
    "nvidia": "https://integrate.api.nvidia.com/v1/models",
    "aion": "https://api.aionlabs.ai/v1/models",
    "llm7": "https://api.llm7.io/v1/models",
    "kilo": "https://ai-gateway.kilo.ai/api/v1/models",
    "siliconflow": "https://api.siliconflow.com/v1/models",
    "modelscope": "https://api-inference.modelscope.ai/v1/models",
    "ovhcloud": "https://catalog.endpoints.ai.ovh.net/rest/v1/models_v2",
    "sambanova": "https://api.sambanova.ai/v1/models",
}
SECRETS = {
    "openrouter": "OPENROUTER_API_KEY",
    "felo": "FELO_AI_API",
    "omni": "OMNI_API_KEY",
    "huggingface": "HUGGINGFACE_TOKEN",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "cerebras": "CEREBRAS_API_KEY",
    "nvidia": "NVIDIA_API_KEY",
    "aion": "AION_API_KEY",
    "llm7": "LLM7_API_TOKEN",
    "zai": "ZAI_API_KEY",
    "modelscope": "MODELSCOPE_TOKEN",
    "siliconflow": "SILICONFLOW_API_KEY",
    "kilo": "KILO_API_KEY",
    "ovhcloud": "OVHCLOUD_API_KEY",
    "sambanova": "SAMBANOVA_API_KEY",
}
ENDPOINTS.update(provider_catalog_protocols.ENDPOINTS)
SECRETS.update({p: names[0] for p, names in provider_catalog_protocols.SECRET_ENV.items()})
SECRET_ALIASES = {
    "huggingface": ("HUGGINGFACE_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HF_API_TOKEN", "HF_TOKEN"),
    "cerebras": ("CEREBRAS_API_KEY",),
    "nvidia": ("NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY"),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
}

# Module-level precomputed secret environment variable name tuples to avoid allocations in resolve_secret
RESOLVE_SECRET_NAMES = {
    p: SECRET_ALIASES.get(p) or (SECRETS.get(p),) for p in SECRETS
}

# Module-level tuples/sets for fast response header filtering in get_json
HEADER_PREFIXES = ("x-ratelimit-", "x-credit-", "x-quota-", "x-remaining-", "x-usage-")
HEADER_EXACT = {"retry-after", "x-request-id"}

DOCUMENTED_TRIAL_MODELS = {
    ("felo", "ox-alpha"): {
        "access_classification": "free_trial",
        "source": "https://openapi.felo.ai/models/stealth/ox-alpha",
        "source_observed": "2026-08-24",
        "max_output_tokens": 128_000,
        "context_length": 1_000_000,
        "cadence": "trial",
    }
}
# Public plan/page claims. Remaining balance is NEVER copied from these rows.
DOCUMENTED_ENTITLEMENTS = {
    "felo": [
        {
            "id": "search-api-free-standard",
            "cadence": "daily",
            "public_claim": "200 daily free credits (Free Standard Search API docs)",
            "source": "docs/ops/FREE-QUOTA-WINDOWS.md",
            "remaining_source": "authenticated_headers_or_account_api_only",
        },
        {
            "id": "ox-alpha",
            "cadence": "trial",
            "public_claim": "documented free-trial model page",
            "source": "https://openapi.felo.ai/models/stealth/ox-alpha",
            "remaining_source": "catalog_plus_invocation",
        },
    ],
    "openrouter": [
        {
            "id": ":free-suffix",
            "cadence": "catalog",
            "public_claim": "models whose id ends with :free",
            "source": "https://openrouter.ai/api/v1/models",
            "remaining_source": "catalog_pricing",
        }
    ],
    "huggingface": [
        {
            "id": "router-free-zero",
            "cadence": "catalog",
            "public_claim": "only when poll classifies free_zero_price or free_trial",
            "source": "https://router.huggingface.co/v1/models",
            "remaining_source": "catalog_plus_headers",
        }
    ],
    "omni": [
        {
            "id": "catalog-zero",
            "cadence": "catalog",
            "public_claim": "only when poll classifies free_zero_price",
            "source": "https://cloud.omniroute.online/v1/models",
            "remaining_source": "catalog_plus_headers",
        }
    ],
}


def resolve_secret(provider: str) -> tuple[str | None, str | None]:
    names = RESOLVE_SECRET_NAMES.get(provider) or SECRET_ALIASES.get(provider) or (SECRETS.get(provider),)
    for name in names:
        if not name:
            continue
        token = os.environ.get(name)
        if token:
            return token, name
    return None, SECRETS.get(provider)


def _request(url: str, token: str | None = None, header_name: str = "Authorization", page_token: str | None = None) -> tuple[dict, dict]:
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if token:
        headers[header_name] = f"Bearer {token}" if header_name == "Authorization" else token
    if page_token:
        # pageToken is a query parameter; only the credential belongs in a header.
        if url != ENDPOINTS["gemini"] or header_name != "x-goog-api-key":
            raise ValueError("invalid_pagination")
        url += "?" + urlencode({"pageToken": page_token})
    request = urllib.request.Request(url, headers=headers)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, response_headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=30) as response:
            body = response.read(8 * 1024 * 1024 + 1)
            if len(body) > 8 * 1024 * 1024:
                raise ValueError("response_too_large")
            payload = json.loads(body)
            if url == ENDPOINTS["ovhcloud"] and isinstance(payload, list):
                payload = {"data": payload}
            if not isinstance(payload, dict):
                raise ValueError("invalid_response_shape")
            metadata = {key.lower(): value for key, value in response.headers.items()
                        if key.lower().startswith(HEADER_PREFIXES) or key.lower() in HEADER_EXACT}
            return payload, metadata
    except urllib.error.HTTPError as exc:
        raise ValueError(f"http_status_{exc.code}") from None
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("invalid_json") from None


def _request_json(url: str, token: str | None = None, header_name: str = "Authorization", page_token: str | None = None):
    return _request(url, token, header_name, page_token)


def get_json(url: str, token: str | None = None) -> tuple[dict, dict]:
    return _request(url, token)


def _gemini_pages(token: str) -> tuple[dict, dict]:
    rows = []
    seen_tokens = set()
    page_token = None
    metadata = {}
    while True:
        payload, response_headers = _request(ENDPOINTS["gemini"], token, "x-goog-api-key", page_token)
        metadata.update(response_headers)
        batch = payload.get("models")
        if not isinstance(batch, list) or any(not isinstance(item, dict) for item in batch):
            raise ValueError("invalid_response_shape")
        rows.extend(batch)
        next_token = payload.get("nextPageToken")
        if next_token in (None, ""):
            return {"models": rows}, metadata
        if not isinstance(next_token, str) or next_token in seen_tokens:
            raise ValueError("invalid_pagination")
        seen_tokens.add(next_token)
        page_token = next_token


def price_classification(data: dict) -> str:
    pricing = data.get("pricing")
    if not isinstance(pricing, dict):
        return "unknown"
    values = []
    for key in ("prompt", "completion"):
        value = pricing.get(key)
        if isinstance(value, bool) or value is None:
            return "unknown"
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return "unknown"
        if not math.isfinite(number):
            return "unknown"
        values.append(number)
    if values == [0, 0]:
        return "free_zero_price"
    return "paid" if min(values) >= 0 else "unknown"


def _positive_int(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None

def poll(provider: str, token: str) -> tuple[list[dict], dict]:
    if provider in provider_catalog_protocols.PROVIDERS:
        return provider_catalog_protocols.poll(provider, token, get_json, os.environ.get("CLOUDFLARE_ACCOUNT_ID"))
    payload, response_headers = _gemini_pages(token) if provider == "gemini" else get_json(ENDPOINTS[provider], token)
    items = payload.get("models" if provider == "gemini" else "data")
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError("invalid_response_shape")
    rows = []
    seen: set[str] = set()
    raw_source = f"{provider}:/v1/models"

    for item in items:
        model_id = item.get("name") if provider == "gemini" else item.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError("invalid_model")
        if provider == "gemini" and model_id.startswith("models/"):
            model_id = model_id[7:]
        if not model_id or any(ord(char) < 32 for char in model_id):
            raise ValueError("invalid_model")
        if model_id in seen:
            continue
        seen.add(model_id)
        trial = DOCUMENTED_TRIAL_MODELS.get((provider, model_id))
        if trial:
            access_class = trial.get("access_classification", "catalog_pricing_only")
            access_src = trial.get("source")
            access_observed = trial.get("source_observed")
            cadence = trial.get("cadence", "catalog")
            ctx_len = item.get("context_length") or trial.get("context_length")
            max_out = item.get("max_output_tokens") or trial.get("max_output_tokens")
        else:
            access_class = "catalog_pricing_only"
            access_src = None
            access_observed = None
            cadence = "catalog"
            ctx_len = item.get("context_length")
            max_out = item.get("max_output_tokens")

        if provider == "gemini":
            ctx_len = item.get("inputTokenLimit")
            max_out = item.get("outputTokenLimit")
            pricing = {}
        elif provider == "mistral":
            ctx_len = item.get("max_context_length")
            max_out = item.get("max_output_tokens")
            pricing = {}
        elif provider == "groq":
            ctx_len = item.get("context_window")
            max_out = item.get("max_completion_tokens")
            pricing = {}
        elif provider == "sambanova":
            max_out = item.get("max_completion_tokens")
            pricing = item.get("pricing") if isinstance(item.get("pricing"), dict) else {}
        else:
            pricing = item.get("pricing") if isinstance(item.get("pricing"), dict) else {}
        ctx_len = _positive_int(ctx_len) or (trial.get("context_length") if trial else None)
        max_out = _positive_int(max_out) or (trial.get("max_output_tokens") if trial else None)
        rows.append({
            "provider": provider,
            "id": model_id,
            "name": item.get("displayName") if provider == "gemini" else item.get("name"),
            "pricing": pricing,
            "pricing_classification": price_classification({"pricing": pricing}),
            "access_classification": access_class,
            "access_source": access_src,
            "access_source_observed": access_observed,
            "cadence": cadence,
            "free_suffix": provider == "openrouter" and model_id.endswith(":free"),
            "context_length": ctx_len,
            "max_output_tokens": max_out,
            "capabilities": item.get("capabilities") if provider == "mistral" and isinstance(item.get("capabilities"), dict) else item.get("supportedGenerationMethods") if provider == "gemini" and isinstance(item.get("supportedGenerationMethods"), list) else None,
            "active": item.get("active") if provider == "groq" and isinstance(item.get("active"), bool) else None,
            "raw_source": raw_source,
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
            "cadence": trial.get("cadence", "trial"),
            "free_suffix": False,
            "context_length": trial["context_length"],
            "max_output_tokens": trial["max_output_tokens"],
            "raw_source": f"{provider}:/v1/models + documented-model-page",
        })
    return rows, response_headers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", default="openrouter,felo,omni,huggingface,cerebras")
    parser.add_argument("--output", default="/tmp/model-catalog/catalog.json")
    args = parser.parse_args(argv)

    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows: list[dict] = []
    errors: list[dict] = []
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    provider_observations: dict[str, dict] = {}

    for provider in providers:
        if provider not in ENDPOINTS:
            errors.append({"provider": provider, "error": "unsupported_provider"})
            continue
        token, env_name = (None, None) if provider in PUBLIC_CATALOGS else resolve_secret(provider)
        if not token and provider not in PUBLIC_CATALOGS:
            errors.append({"provider": provider, "error": "missing_secret", "secret_env": env_name, "aliases": list(SECRET_ALIASES.get(provider, ()))})
            continue
        try:
            provider_rows, headers = poll(provider, token)
            rows.extend(provider_rows)
            provider_observations[provider] = {
                "catalog_observed_at": observed_at,
                "response_headers": headers,
                "secret_env_resolved": env_name if token else None,
                "catalog_authentication": "credential" if token else ("observed_public_get" if provider == "modelscope" else "documented_public_get"),
                "catalog_contract_source": "provider_runtime_observation" if provider == "modelscope" else "official_documentation",
                "account_endpoint": None,
                "account_endpoint_status": "not_documented",
                "documented_entitlements": DOCUMENTED_ENTITLEMENTS.get(provider, []),
                "quota_note": "Account-level balance/quota is not asserted unless exposed by an authoritative provider endpoint or response metadata. Cadence entitlements are public claims only.",
            }
        except Exception as exc:
            safe_message = str(exc) if re.fullmatch(r"http_status_[1-5][0-9][0-9]|response_too_large|invalid_json|invalid_response_shape|invalid_pagination|invalid_model", str(exc)) else "request_failed"
            errors.append({"provider": provider, "error": type(exc).__name__, "message": safe_message})

    document = {
        "schema": "provider-model-catalog/v5",
        "observed_at": observed_at,
        "providers": providers,
        "cadence_classes": ["hourly", "daily", "weekly", "monthly", "trial", "catalog", "unknown"],
        "promotion": {
            "status": "observe_only",
            "expiry": None,
            "source": "docs/ops/FREE-QUOTA-WINDOWS.md",
            "note": "Promotion/quota expiry must be refreshed from authoritative provider evidence; model-page trial status is separate from account-level daily quota.",
        },
        "provider_observations": provider_observations,
        "models": rows,
        "errors": errors,
    }
    output_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(output_dir, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".catalog-", suffix=".tmp", dir=output_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(document, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, args.output)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    eligible = [r for r in rows if r["pricing_classification"] == "free_zero_price" or r["free_suffix"] or r["access_classification"] == "free_trial"]
    print(f"catalog_models={len(rows)} eligible_free_zero_trial={len(eligible)} errors={len(errors)}")
    for provider, observation in provider_observations.items():
        print(f"ACCOUNT_METADATA {provider}: {json.dumps(observation['response_headers'], sort_keys=True)}")
    for row in eligible:
        print(f"ELIGIBLE {row['provider']}/{row['id']} [{row['access_classification']}; cadence={row.get('cadence')}; max_output={row.get('max_output_tokens')}; context={row.get('context_length')}]")
    return 0 if rows or not providers else 1


if __name__ == "__main__":
    raise SystemExit(main())
