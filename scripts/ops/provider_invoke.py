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
        if name == "cloudflare":
            account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
            if not account:
                return None, secrets, None, "account-scope-unresolved: CLOUDFLARE_ACCOUNT_ID not present in job env"
            return provider_protocols.cloudflare_chat_url(account), secrets, None, ""
        return provider_protocols.CHAT_ENDPOINTS[name], secrets, None, ""
    return None, (), None, "no reviewed chat endpoint in repo sources (catalog-only provider)"


def http_json(method: str, url: str, token: str, payload=None, timeout=45):
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", default="/tmp/invoke-completion.md")
    ap.add_argument("--max-tokens", type=int, default=300)
    args = ap.parse_args()

    provider = args.provider
    verdict = {"provider": provider, "ok": False, "diagnosis": "", "model": None,
               "http": None, "latency_ms": None}
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
        verdict["diagnosis"] = f"no-credential: none of {list(secret_names)} present in job env"
        print("INVOKE_VERDICT " + json.dumps(verdict))
        return 0
    verdict["credential"] = token_name

    model = os.environ.get("INVOKE_MODEL") or None
    if model is None and catalog_url:
        status, cat = http_json("GET", catalog_url, token)
        if status == 200:
            model = pick_model(cat)
    if model is None:
        model = "default"
        verdict["model_note"] = "catalog unresolved; provider default attempted"
    verdict["model"] = model

    prompt = open(args.prompt_file).read()
    payload = {"model": model, "max_tokens": args.max_tokens,
               "messages": [{"role": "user", "content": prompt}]}
    t0 = time.time()
    status, body = http_json("POST", url, token, payload)
    verdict["latency_ms"] = int((time.time() - t0) * 1000)
    verdict["http"] = status
    if status is None:
        verdict["diagnosis"] = "transport: " + str(body.get("transport_error"))[:200]
    elif status == 200:
        try:
            text = body["choices"][0]["message"]["content"]
        except Exception:
            text = ""
        if text:
            verdict["ok"] = True
            verdict["diagnosis"] = "invoke succeeded"
            with open(args.out, "w") as f:
                f.write(text)
        else:
            verdict["diagnosis"] = f"http 200 but no completion text in response shape {sorted(body.keys())}"
    else:
        err = body.get("error") if isinstance(body, dict) else None
        msg = (err.get("message") if isinstance(err, dict) else None) or ""
        verdict["diagnosis"] = f"http {status}: {str(msg)[:200]}"
    print("INVOKE_VERDICT " + json.dumps(verdict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
