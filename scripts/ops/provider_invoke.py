#!/usr/bin/env python3
"""Bounded per-provider invoke for the class-corrected inference batch.

Resolves the provider's chat endpoint + secret env names from the repo's own
reviewed sources at runtime (llm_api_hub research_providers / provider_extensions
/ provider_protocols + the MSM catalog secret map) — no hard-pinned routes, so
the wiring can move without touching this script. Picks a chat model from the
provider's live /models catalog (dispatch-time resolution), fires ONE bounded
chat completion carrying a production-work prompt, and emits a verdict line:

  INVOKE_VERDICT {"provider": ..., "ok": bool, "diagnosis": ..., ...}

Exit code is 0 whenever a verdict was produced (provider outcomes live in the
verdict, not the exit code); nonzero only on harness misuse.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from llm_api_hub.server import research_providers, provider_extensions, provider_protocols

try:
    from scripts import provider_catalog_protocols
except Exception:  # pragma: no cover - catalog protocols are an optional resolver aid
    provider_catalog_protocols = None

NON_CHAT_HINTS = ("embed", "whisper", "tts", "rerank", "moderation", "asr", "translate")


def resolve_provider(name: str):
    """Return (chat_url, secret_env_names, catalog_url_or_None, note)."""
    if name in research_providers.ENDPOINTS:
        url, secrets = research_providers.ENDPOINTS[name]
        return url, secrets, url.replace("/chat/completions", "/models"), ""
    if name in provider_extensions.ENDPOINTS:
        url, secrets = provider_extensions.ENDPOINTS[name]
        catalog = provider_extensions.CATALOG_ENDPOINTS.get(name)
        return url, secrets, catalog, ""
    if name in provider_protocols.SECRET_ENV:
        secrets = provider_protocols.SECRET_ENV[name]
        account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        if name == "cloudflare" and not account:
            return None, secrets, None, "account-scope-unresolved: CLOUDFLARE_ACCOUNT_ID not present in job env"
        catalog = None
        if provider_catalog_protocols is not None:
            try:
                catalog = provider_catalog_protocols.endpoint(name, account or None)
            except Exception:
                catalog = None
        if name == "cloudflare":
            return provider_protocols.cloudflare_chat_url(account), secrets, catalog, ""
        return provider_protocols.CHAT_ENDPOINTS[name], secrets, catalog, ""
    return None, (), None, "no reviewed chat endpoint in repo sources (catalog-only provider)"


def http_json(method: str, url: str, token: str, payload=None, timeout=90):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            body = {}
        return e.code, body
    except Exception as e:  # DNS, TLS, egress blocks, timeouts
        return None, {"transport_error": type(e).__name__}


def pick_model(catalog: dict) -> str | None:
    ids = [m.get("id") for m in catalog.get("data", []) if isinstance(m, dict) and m.get("id")]
    chat = [i for i in ids if not any(h in i.lower() for h in NON_CHAT_HINTS)]
    return (chat or ids or [None])[0]


def is_verified_no_cost_model(model: dict) -> bool:
    """Require explicit zero-price evidence or a verified free-trial entitlement."""
    if not isinstance(model, dict):
        return False
    pricing = model.get("pricing_classification")
    if pricing == "free_zero_price":
        return True
    return (model.get("access_classification") == "free_trial"
            and model.get("entitlement_verification") == "verified"
            and pricing in (None, "unknown"))

def select_free_chat_model(models: list[dict], requested_model: str | None = None) -> str | None:
    """Select an exact, verified no-cost chat model; never fall back to paid/unknown.

    The selector intentionally does not require provider quota fields. Pool
    allocation and provider quota are separate admission dimensions.
    """
    eligible = []
    for model in models if isinstance(models, list) else []:
        if not isinstance(model, dict):
            continue
        model_id = model.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            continue
        if any(hint in model_id.lower() for hint in NON_CHAT_HINTS):
            continue
        if is_verified_no_cost_model(model):
            eligible.append(model_id)
    if requested_model is not None:
        return requested_model if requested_model in eligible else None
    return eligible[0] if eligible else None

def _policy_evidence_issue(entry: dict) -> str | None:
    if entry.get("no_cost_verified") is not True:
        return "policy_no_cost_not_verified"
    for key in ("pricing_source", "terms_source", "capability_source"):
        value = entry.get(key)
        if not isinstance(value, str) or not value.startswith("https://"):
            return f"policy_{key}_missing"
    for key in ("pricing_verified_at", "terms_verified_at", "capability_verified_at"):
        value = entry.get(key)
        if not isinstance(value, str):
            return f"policy_{key}_missing"
        try:
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return f"policy_{key}_invalid"
        if parsed.tzinfo is None or parsed > dt.datetime.now(dt.timezone.utc):
            return f"policy_{key}_invalid"
    quota_class = entry.get("quota_class")
    allowed = {"provider_quota_backed", "daily_pool_no_provider_quota", "quota_unknown", "quota_not_applicable"}
    if quota_class not in allowed:
        return "policy_quota_class_missing"
    if quota_class == "daily_pool_no_provider_quota":
        if not entry.get("pool_id") or not str(entry.get("pool_evidence_ref", "")).startswith("https://"):
            return "policy_daily_pool_evidence_missing"
    if quota_class in {"provider_quota_backed", "quota_not_applicable"}:
        if not str(entry.get("quota_evidence_ref", "")).startswith("https://"):
            return "policy_quota_evidence_missing"
    return None

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-tokens", type=int, default=300)
    parser.add_argument("--free-only", action="store_true")
    parser.add_argument("--catalog-only", action="store_true")
    args = parser.parse_args()
    provider = args.provider.lower()
    if args.catalog_only:
        catalog_verdict = {"provider": provider, "models": None, "free_model_count": 0,
                           "catalog_ok": False, "inference_status": "not_attempted", "diagnosis": None}
        if provider not in provider_model_catalog.ENDPOINTS:
            catalog_verdict["diagnosis"] = "no_canonical_model_catalog"
        else:
            token, _env_name = provider_model_catalog.resolve_secret(provider)
            if not token and provider not in provider_model_catalog.PUBLIC_CATALOGS:
                catalog_verdict["diagnosis"] = "missing_secret"
            else:
                try:
                    models, _headers = provider_model_catalog.poll(provider, token)
                    catalog_verdict["models"] = len(models)
                    catalog_verdict["free_model_count"] = sum(1 for model in models if is_verified_no_cost_model(model))
                    catalog_verdict["catalog_ok"] = bool(models)
                    catalog_verdict["diagnosis"] = "catalog_ok" if models else "empty_catalog"
                except Exception as exc:
                    catalog_verdict["diagnosis"] = "catalog_unavailable_" + type(exc).__name__
        print("CATALOG_VERDICT", json.dumps(catalog_verdict, sort_keys=True))
        return 0
    verdict = {"provider": provider, "model": args.model, "ok": False,    verdict = {"provider": provider, "model": args.model, "ok": False,
               "no_cost_verified": False, "policy_admitted": False,
               "terms_accepted": "not_verified", "entitlement_verified": "not_verified",
               "dispatch_eligible": False, "validation_scope": "policy_gated_no_cost_inference_smoke",
               "quota_class": "unclassified", "pool_id": None,
               "model_pricing_classification": None, "model_access_classification": None,
               "credential_env_resolved": None, "latency_ms": None, "diagnosis": None}
    def finish():
        print("INVOKE_VERDICT", json.dumps(verdict, sort_keys=True))
        return 0
    if not args.free_only:
        verdict["diagnosis"] = "free_only_required"
        return finish()
    url, secret_names, _catalog_url, note = resolve_provider(provider)
    token_name = next((name for name in secret_names if os.environ.get(name)), None)
    token = os.environ.get(token_name) if token_name else None
    verdict["credential_env_resolved"] = token_name
    if not url:
        verdict["diagnosis"] = note or "provider_not_configured"
        return finish()
    if not token:
        verdict["diagnosis"] = "missing_secret"
        return finish()
    try:
        admitted = set(research_providers.admitted_models())
    except research_providers.ProviderAdmissionError as exc:
        verdict["diagnosis"] = getattr(exc, "code", "provider_policy_unavailable")
        return finish()
    admitted_ids = {item.split("/", 1)[1] for item in admitted if isinstance(item, str) and item.startswith(provider + "/") and "/" in item}
    if not admitted_ids:
        verdict["diagnosis"] = "provider_model_not_admitted"
        return finish()
    try:
        models, _headers = provider_model_catalog.poll(provider, token)
    except Exception as exc:
        verdict["diagnosis"] = "catalog_unavailable_" + type(exc).__name__
        return finish()
    admitted_free_rows = [row for row in models if isinstance(row, dict) and row.get("id") in admitted_ids and is_verified_no_cost_model(row)]
    if not admitted_free_rows:
        verdict["diagnosis"] = "admitted_model_not_verified_no_cost"
        return finish()
    selected = select_free_chat_model(admitted_free_rows, args.model)
    if not selected:
        verdict["diagnosis"] = "no_verified_no_cost_chat_model"
        return finish()
    selected_row = next(row for row in admitted_free_rows if row.get("id") == selected)
    try:
        entry = research_providers.admission_entry(provider, selected)
    except research_providers.ProviderAdmissionError as exc:
        verdict["diagnosis"] = getattr(exc, "code", "provider_not_admitted")
        return finish()
    verdict.update({
        "model": selected,
        "policy_admitted": True,
        "terms_accepted": "policy_asserted",
        "entitlement_verified": "policy_asserted",
        "quota_class": entry.get("quota_class", "unclassified"),
        "pool_id": entry.get("pool_id"),
        "model_pricing_classification": selected_row.get("pricing_classification"),
        "model_access_classification": selected_row.get("access_classification"),
    })
    policy_issue = _policy_evidence_issue(entry)
    if policy_issue:
        verdict["diagnosis"] = policy_issue
        return finish()
    verdict["no_cost_verified"] = True
    try:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    except OSError:
        verdict["diagnosis"] = "prompt_file_unavailable"
        return finish()
    payload = {"model": selected, "messages": [{"role": "user", "content": prompt}],
               "max_tokens": args.max_tokens, "temperature": 0}
    started = time.monotonic()
    try:
        response = research_providers.complete(provider, selected, payload, timeout=90)
        verdict["latency_ms"] = int((time.monotonic() - started) * 1000)
        message = (response.get("choices") or [{}])[0].get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            verdict["diagnosis"] = "empty_inference_response"
            return finish()
        Path(args.out).write_text(content, encoding="utf-8")
        verdict["ok"] = True
        verdict["diagnosis"] = "inference_ok"
        verdict["completion_chars"] = len(content)
        usage = response.get("usage") or {}
        verdict["input_tokens"] = usage.get("prompt_tokens")
        verdict["output_tokens"] = usage.get("completion_tokens")
    except research_providers.ProviderAdmissionError as exc:
        verdict["latency_ms"] = int((time.monotonic() - started) * 1000)
        verdict["diagnosis"] = getattr(exc, "code", "provider_inference_failed")
        verdict["http_status"] = getattr(exc, "status", None)
    except Exception as exc:
        verdict["latency_ms"] = int((time.monotonic() - started) * 1000)
        verdict["diagnosis"] = type(exc).__name__
    return finish()

if __name__ == "__main__":
    raise SystemExit(main())
