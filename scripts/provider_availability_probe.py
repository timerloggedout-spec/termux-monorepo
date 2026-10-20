#!/usr/bin/env python3
"""Continuously probe provider availability without exposing credentials."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request

TIMEOUT = 30
MAX_RESPONSE_BYTES = 1_048_576
UA = "termux-monorepo-provider-availability/1"
HF_TOKEN_ALIASES = ("HUGGINGFACE_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HF_API_TOKEN", "HF_TOKEN")


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def request(url, *, token=None, method="GET", payload=None, auth_header="Authorization"):
    headers = {"User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers[auth_header] = f"Bearer {token}" if auth_header == "Authorization" else token
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with _OPENER.open(req, timeout=TIMEOUT) as resp:
        raw = resp.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("response_too_large")
        return resp.status, json.loads(raw.decode("utf-8")) if raw else {}


def result(provider):
    return {"provider": provider, "credential_present": False, "auth_mode": "unconfigured",
            "catalog_probe_required": False, "catalog_ok": False, "inference_ok": False,
            "model": None, "observed_at": now(), "error_class": None}



def catalog_provider_probe(provider, row, catalog_module=None):
    """Observe one provider through the canonical catalog adapters; never infer here."""
    if catalog_module is None:
        from scripts import provider_model_catalog as catalog_module

    token, _env_name = catalog_module.resolve_secret(provider)
    public = provider in catalog_module.PUBLIC_CATALOGS
    row["credential_present"] = bool(token)
    row["auth_mode"] = "credential" if token else ("public" if public else "unconfigured")
    row["catalog_probe_required"] = bool(token) or public
    if not token and not public:
        row["error_class"] = "missing_secret"
        return

    try:
        models, _headers = catalog_module.poll(provider, token)
        row["catalog_ok"] = bool(models)
        row["model_count"] = len(models)
        if not models:
            row["error_class"] = "empty_catalog"
            return
        if provider == "openrouter":
            free = [model.get("id") for model in models if model.get("free_suffix")]
            preferred = os.environ.get("OPENROUTER_HEALTH_MODEL", "").strip()
            row["free_model_count"] = len(free)
            row["model"] = preferred if preferred and preferred in free else (free[0] if free else None)
        else:
            row["model"] = models[0].get("id")
    except Exception as exc:
        # The catalog adapter already sanitizes HTTP errors; retain only a
        # narrow error vocabulary and never serialize upstream bodies/headers.
        safe = str(exc)
        if re.fullmatch(r"http_status_[1-5][0-9][0-9]|response_too_large|invalid_json|invalid_response_shape|invalid_pagination|invalid_model|invalid_account_id", safe):
            row["error_class"] = safe
        else:
            row["error_class"] = type(exc).__name__


def probe_catalog(provider, url, token, row):
    row["credential_present"] = bool(token)
    if not token:
        row["error_class"] = "missing_secret"
        return
    try:
        status, payload = request(url, token=token)
        models = payload.get("data", []) if isinstance(payload, dict) else []
        row["catalog_ok"] = 200 <= status < 300 and isinstance(models, list)
        row["model_count"] = len(models)
        if provider == "openrouter":
            free = [m.get("id") for m in models if str(m.get("id", "")).endswith(":free")]
            preferred = os.environ.get("OPENROUTER_HEALTH_MODEL", "").strip()
            row["free_model_count"] = len(free)
            row["model"] = preferred if preferred and preferred in free else (free[0] if free else None)
        elif models:
            row["model"] = models[0].get("id")
    except urllib.error.HTTPError as e:
        row["error_class"] = f"http_{e.code}"
    except Exception as e:
        row["error_class"] = type(e).__name__


def openrouter_inference(row, token):
    model = row.get("model")
    if not token or not model or not row.get("catalog_ok"):
        return
    try:
        status, _ = request("https://openrouter.ai/api/v1/chat/completions", token=token, method="POST",
                            payload={"model": model, "messages": [{"role": "user", "content": "Reply with exactly: PROVIDER_HEALTH_OK"}], "max_tokens": 8})
        row["inference_ok"] = 200 <= status < 300
        if not row["inference_ok"]:
            row["error_class"] = f"inference_http_{status}"
    except urllib.error.HTTPError as e:
        row["error_class"] = f"inference_http_{e.code}"
    except Exception as e:
        row["error_class"] = f"inference_{type(e).__name__}"


def gemini_probe(row, token):
    row["credential_present"] = bool(token)
    row["auth_mode"] = "credential" if token else "unconfigured"
    row["catalog_probe_required"] = bool(token)
    if not token:
        row["error_class"] = "missing_secret"
        return
    try:
        status, payload = request("https://generativelanguage.googleapis.com/v1beta/models", token=token, auth_header="x-goog-api-key")
    except urllib.error.HTTPError as e:
        row["error_class"] = f"http_{e.code}"
        return
    except Exception as e:
        row["error_class"] = type(e).__name__
        return
    models = payload.get("models", []) if isinstance(payload, dict) else []
    usable = [m for m in models if "generateContent" in (m.get("supportedGenerationMethods") or [])]
    preferred = os.environ.get("GEMINI_HEALTH_MODEL", "").strip()
    chosen = next((m for m in usable if m.get("name", "").endswith("/" + preferred)), None)
    chosen = chosen or next((m for m in usable if "flash" in m.get("name", "").lower()), None) or (usable[0] if usable else None)
    if not chosen:
        row["error_class"] = "no_generate_content_model"
        return
    model_name = chosen.get("name", "").split("/")[-1]
    row["catalog_ok"] = True
    row["model"] = model_name
    try:
        status, _ = request(f"https://generativelanguage.googleapis.com/v1beta/{chosen['name']}:generateContent",
                            token=token, auth_header="x-goog-api-key", method="POST",
                            payload={"contents": [{"parts": [{"text": "Reply with exactly: PROVIDER_HEALTH_OK"}]}]})
        row["inference_ok"] = 200 <= status < 300
        if not row["inference_ok"]:
            row["error_class"] = f"inference_http_{status}"
    except urllib.error.HTTPError as e:
        row["error_class"] = f"inference_http_{e.code}"
    except Exception as e:
        row["error_class"] = f"inference_{type(e).__name__}"


def resolve_huggingface_token(environ=None):
    env = os.environ if environ is None else environ
    return next((env.get(name, "") for name in HF_TOKEN_ALIASES if env.get(name, "")), "")


def main():
    from scripts import provider_model_catalog

    observed = now()
    rows = []
    # Keep the two existing inference probes explicitly bounded. All other
    # providers receive catalog-only observations; catalog discovery never
    # activates native routing or sends a completion request.
    for provider in sorted(provider_model_catalog.ENDPOINTS):
        row = result(provider)
        if provider == "gemini":
            gemini_probe(row, os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", ""))
        else:
            catalog_provider_probe(provider, row, provider_model_catalog)
            if provider == "openrouter" and row["credential_present"] and row["catalog_ok"]:
                openrouter_inference(row, os.environ.get("OPENROUTER_API_KEY", ""))
        rows.append(row)

    document = {"schema": "provider-availability/v1", "observed_at": observed,
                "semantics": {"credential_present": "workflow secret resolved; does not prove validity",
                              "auth_mode": "credential, public, or unconfigured; public does not imply entitlement",
                              "catalog_probe_required": "true for configured providers and explicitly public catalogs",
                              "catalog_ok": "provider catalog endpoint responded with usable model metadata",
                              "inference_ok": "minimal live inference succeeded only for the established OpenRouter/Gemini probes"}, "providers": rows}
    with open(os.environ.get("OUTPUT", "/tmp/provider-availability.json"), "w", encoding="utf-8") as fh:
        json.dump(document, fh, indent=2, sort_keys=True)
        fh.write("\n")
    for row in rows:
        print(f"{row['provider']}: auth={row['auth_mode']} credential={row['credential_present']} catalog={row['catalog_ok']} inference={row['inference_ok']} model={row.get('model') or '-'} error={row.get('error_class') or '-'}")


if __name__ == "__main__":
    main()
