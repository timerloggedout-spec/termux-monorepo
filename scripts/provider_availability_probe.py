#!/usr/bin/env python3
"""Continuously probe provider availability without exposing credentials.

The probe distinguishes:
- credential_present: secret is available to the workflow
- catalog_ok: provider model/catalog endpoint responds
- inference_ok: a real, minimal inference succeeds
- model: exact model observed/used
- observed_at: UTC evidence timestamp

Provider credentials are never printed or persisted.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import ssl
import urllib.error
import urllib.request

TIMEOUT = 30
UA = "termux-monorepo-provider-availability/1"
OUT = os.environ.get("OUTPUT", "/tmp/provider-availability.json")


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def request(url, *, token=None, method="GET", payload=None):
    headers = {"User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
        return resp.status, json.loads(raw.decode("utf-8")) if raw else {}


def result(provider):
    return {
        "provider": provider,
        "credential_present": False,
        "catalog_ok": False,
        "inference_ok": False,
        "model": None,
        "observed_at": now(),
        "error_class": None,
    }


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
            row["free_model_count"] = len(free)
            preferred = os.environ.get("OPENROUTER_HEALTH_MODEL", "").strip()
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
        status, _ = request(
            "https://openrouter.ai/api/v1/chat/completions",
            token=token,
            method="POST",
            payload={
                "model": model,
                "messages": [{"role": "user", "content": "Reply with exactly: PROVIDER_HEALTH_OK"}],
                "max_tokens": 8,
            },
        )
        row["inference_ok"] = 200 <= status < 300
        if not row["inference_ok"]:
            row["error_class"] = f"inference_http_{status}"
    except urllib.error.HTTPError as e:
        row["error_class"] = f"inference_http_{e.code}"
    except Exception as e:
        row["error_class"] = f"inference_{type(e).__name__}"


def gemini_probe(row, token):
    row["credential_present"] = bool(token)
    if not token:
        row["error_class"] = "missing_secret"
        return
    try:
        status, payload = request(
            "https://generativelanguage.googleapis.com/v1beta/models",
            method="GET",
            url_token=token,
        )
    except TypeError:
        # urllib request helper intentionally keeps secrets out of URLs; Gemini uses query auth.
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models?key=" + urllib.parse.quote(token)
            status, payload = request(url)
        except Exception as e:
            row["error_class"] = type(e).__name__
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
        import urllib.parse
        url = f"https://generativelanguage.googleapis.com/v1beta/{chosen['name']}:generateContent?key={urllib.parse.quote(token)}"
        status, _ = request(
            url,
            method="POST",
            payload={"contents": [{"parts": [{"text": "Reply with exactly: PROVIDER_HEALTH_OK"}]}]},
        )
        row["inference_ok"] = 200 <= status < 300
        if not row["inference_ok"]:
            row["error_class"] = f"inference_http_{status}"
    except urllib.error.HTTPError as e:
        row["error_class"] = f"inference_http_{e.code}"
    except Exception as e:
        row["error_class"] = f"inference_{type(e).__name__}"


def main():
    observed = now()
    rows = []

    gem = result("gemini")
    gemini_probe(gem, os.environ.get("GEMINI_API_KEY", ""))
    rows.append(gem)

    providers = [
        ("openrouter", "https://openrouter.ai/api/v1/models", os.environ.get("OPENROUTER_API_KEY", "")),
        ("felo", "https://openapi.felo.ai/api/v1/models", os.environ.get("FELO_AI_API", "")),
        ("huggingface", "https://router.huggingface.co/v1/models", os.environ.get("HUGGINGFACE_TOKEN", "") or os.environ.get("HF_TOKEN", "")),
    ]
    for provider, url, token in providers:
        row = result(provider)
        probe_catalog(provider, url, token, row)
        if provider == "openrouter":
            openrouter_inference(row, token)
        rows.append(row)

    document = {
        "schema": "provider-availability/v1",
        "observed_at": observed,
        "semantics": {
            "credential_present": "workflow secret resolved; does not prove validity",
            "catalog_ok": "provider catalog endpoint responded with usable model metadata",
            "inference_ok": "minimal live inference succeeded",
        },
        "providers": rows,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(document, fh, indent=2, sort_keys=True)
        fh.write("\n")

    for row in rows:
        print(
            f"{row['provider']}: credential={row['credential_present']} "
            f"catalog={row['catalog_ok']} inference={row['inference_ok']} "
            f"model={row.get('model') or '-'} error={row.get('error_class') or '-'}"
        )


if __name__ == "__main__":
    main()
