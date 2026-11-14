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
        return None, {"transport_error": f"{type(e).__name__}: {e}"}


def pick_model(catalog: dict) -> str | None:
    ids = [m.get("id") for m in catalog.get("data", []) if isinstance(m, dict) and m.get("id")]
    chat = [i for i in ids if not any(h in i.lower() for h in NON_CHAT_HINTS)]
    return (chat or ids or [None])[0]


def _usage_tokens(body):
    """Null-honest usage extraction, mirroring the http-llm-invoke
    action's jq contract: integer-valued prompt/input +
    completion/output counts, else None. Never zero-filled."""
    if not isinstance(body, dict):
        return None, None
    u = body.get("usage")
    if not isinstance(u, dict):
        return None, None
    def pick(*keys):
        for k in keys:
            v = u.get(k)
            if isinstance(v, bool):
                continue
            if isinstance(v, int) and v >= 0:
                return v
            if isinstance(v, float) and v >= 0 and v == int(v):
                return int(v)
        return None
    return (pick("prompt_tokens", "input_tokens"),
            pick("completion_tokens", "output_tokens"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", default="/tmp/invoke-completion.md")
    ap.add_argument("--max-tokens", type=int, default=300)
    ap.add_argument("--catalog-only", action="store_true",
                    help="Count the provider's live catalog instead of invoking")
    args = ap.parse_args()

    provider = args.provider
    verdict = {"provider": provider, "ok": False, "diagnosis": "", "model": None,
               "tokens_in": None, "tokens_out": None,
               "http": None, "latency_ms": None, "catalog_http": None}
    url, secret_names, catalog_url, note = resolve_provider(provider)
    if url is None:
        verdict["diagnosis"] = note or "unresolved provider"
        print("INVOKE_VERDICT " + json.dumps(verdict))
        return 0
    token, token_name = "", ""
    for name in secret_names:
        if os.environ.get(name):
            token, token_name = os.environ[name], name
            break
    if not token:
        if args.catalog_only:
            print("CATALOG_VERDICT " + json.dumps(
                {"provider": provider, "credential": None, "catalog_http": None, "models": None,
                 "sample": [], "diagnosis": f"no-credential: none of {list(secret_names)} present in job env"}))
            return 0
        verdict["diagnosis"] = f"no-credential: none of {list(secret_names)} present in job env"
        print("INVOKE_VERDICT " + json.dumps(verdict))
        return 0
    verdict["credential"] = token_name

    candidates: list = []
    if args.catalog_only:
        cverdict = {"provider": provider, "credential": token_name, "catalog_http": None,
                    "models": None, "sample": []}
        if catalog_url is None and provider in provider_catalog_protocols.PROVIDERS:
            pass  # catalog stays None: counted as not countable from CI
        if catalog_url:
            if provider == "cloudflare":
                status, cat = http_json("POST", catalog_url, token, {"page": 1, "per_page": 100})
            else:
                status, cat = http_json("GET", catalog_url, token)
            cverdict["catalog_http"] = status
            if status != 200 and provider == "cohere":
                status2, cat2 = http_json("GET", "https://api.cohere.com/v2/models", token)
                cverdict["catalog_http_v2"] = status2
                if status2 == 200:
                    status, cat = status2, cat2
            if status == 200:
                ids = None
                if provider_catalog_protocols is not None and provider in provider_catalog_protocols.PROVIDERS:
                    try:
                        ids = [r["id"] for r in provider_catalog_protocols.normalize_models(provider, cat)]
                    except Exception:
                        ids = None
                if ids is None:
                    ids = [m.get("id") for m in cat.get("data", []) if isinstance(m, dict) and m.get("id")]
                    if not ids and isinstance(cat.get("models"), list):
                        ids = [m.get("id") or m.get("name") for m in cat["models"] if isinstance(m, dict)]
                cverdict["models"] = len(ids)
                cverdict["sample"] = ids[:3]
        print("CATALOG_VERDICT " + json.dumps(cverdict))
        return 0

    model = os.environ.get("INVOKE_MODEL") or None
    if model is None and catalog_url:
        if provider == "cloudflare":
            status, cat = http_json("POST", catalog_url, token, {"page": 1, "per_page": 50})
        else:
            status, cat = http_json("GET", catalog_url, token)
        verdict["catalog_http"] = status
        if status != 200 and provider == "cohere":
            # v1 models catalog refused; the v2 catalog is the same key's other door.
            status2, cat2 = http_json("GET", "https://api.cohere.com/v2/models", token)
            verdict["catalog_http_v2"] = status2
            if status2 == 200:
                status, cat = status2, cat2
        if status == 200:
            if provider_catalog_protocols is not None and provider in provider_catalog_protocols.PROVIDERS:
                try:
                    ids = [r["id"] for r in provider_catalog_protocols.normalize_models(provider, cat)]
                    chat = [i for i in ids if not any(h in i.lower() for h in NON_CHAT_HINTS)]
                    candidates = chat or ids
                    model = (candidates or [None])[0]
                except Exception:
                    model = None
            else:
                data_ids = [m.get("id") for m in cat.get("data", []) if isinstance(m, dict) and m.get("id")]
                chat = [i for i in data_ids if not any(h in i.lower() for h in NON_CHAT_HINTS)]
                candidates = chat or data_ids
                model = (candidates or [None])[0]
    if model is None:
        model = "default"
        verdict["model_note"] = "catalog unresolved; provider default attempted"
    verdict["model"] = model

    prompt = open(args.prompt_file).read()
    attempts = [m for m in dict.fromkeys([model] + candidates[:2]) if m] or ["default"]
    status, body = None, {}
    for attempt_model in attempts:
        verdict["model"] = attempt_model
        for budget in (args.max_tokens, 1024):
            payload = {"model": attempt_model, "max_tokens": budget,
                       "messages": [{"role": "user", "content": prompt}]}
            t0 = time.time()
            status, body = http_json("POST", url, token, payload)
            verdict["latency_ms"] = int((time.time() - t0) * 1000)
            _tin, _tout = _usage_tokens(body)
            if _tin is not None or _tout is not None:
                verdict["tokens_in"], verdict["tokens_out"] = _tin, _tout
            verdict["http"] = status
            if status != 200:
                break
            text = ""
            try:
                text = body["choices"][0]["message"]["content"]
            except Exception:
                pass
            if not text:
                # Cohere v2/chat shape: message.content = [{type: text, text: ...}]
                try:
                    parts = body["message"]["content"]
                    text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                except Exception:
                    text = ""
            if text:
                verdict["ok"] = True
                verdict["diagnosis"] = "invoke succeeded"
                with open(args.out, "w") as f:
                    f.write(text)
                break
            # empty content (e.g. reasoning budget consumed it): retry once, bigger budget
        if verdict["ok"]:
            break
        if status is None:
            verdict["diagnosis"] = "transport: " + str(body.get("transport_error"))[:200]
            break
        if status == 404 and attempt_model != attempts[-1]:
            continue  # catalog/serving skew: fall over to the next catalog model
        err = body.get("error") if isinstance(body, dict) else None
        msg = (err.get("message") if isinstance(err, dict) else None) or ""
        if status == 200:
            verdict["diagnosis"] = f"http 200 but no completion text at max_tokens 1024 (response shape {sorted(body.keys())})"
        else:
            verdict["diagnosis"] = f"http {status}: {str(msg)[:200]}"
        break
    else:
        err = body.get("error") if isinstance(body, dict) else None
        msg = (err.get("message") if isinstance(err, dict) else None) or ""
        verdict["diagnosis"] = f"http {status}: {str(msg)[:200]}"
    print("INVOKE_VERDICT " + json.dumps(verdict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
