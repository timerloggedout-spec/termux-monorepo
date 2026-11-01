#!/usr/bin/env python3
"""Allocation verification probe (census batch-2).

[MUSEai]@{role:{quota-specialist}} - Read-only account-surface reads
for every provider whose credential name was verified in the repo
store (quota-gaps recon, PR #2859). Each provider gets ONE GET against
its canonical account/models surface with the key from env; the raw
status + a bounded body excerpt land in rows.json. No spend, no POSTs
(except Fly's GraphQL read query), keys never printed. A row earns
evidence only from what the surface actually returns.
"""
import json
import os
import urllib.request
import urllib.error

P = os.environ.get("PROBE_PROVIDER", "")


def get(url, headers=None, data=None, method=None):
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.status, resp.read().decode(errors="replace")[:4000]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:1000]
    except Exception as e:
        return 0, f"ERROR {type(e).__name__}: {e}"


def bearer(key):
    return {"Authorization": f"Bearer {key}"}


def main():
    key = os.environ.get("PROBE_KEY", "")
    out = {"provider": P, "key_present": bool(key)}
    if not key:
        out["note"] = "secret empty at runtime"
        print(json.dumps(out)); return
    r = PROVIDERS.get(P)
    if r is None:
        out["note"] = "no route in probe table"
        print(json.dumps(out)); return
    status, body = r(key)
    out["http"] = status
    out["body_excerpt"] = body
    print(json.dumps(out))


def fly(key):
    q = {"query": "query { viewer { email } organizations { nodes { slug name type } } }"}
    return get("https://api.fly.io/graphql", {**bearer(key), "Content-Type": "application/json"},
               data=json.dumps(q).encode())


PROVIDERS = {
    "groq": lambda k: get("https://api.groq.com/openai/v1/models", bearer(k)),
    "cohere": lambda k: get("https://api.cohere.com/v1/models", bearer(k)),
    "sambanova": lambda k: get("https://api.sambanova.ai/v1/models", bearer(k)),
    "siliconflow": lambda k: get("https://api.siliconflow.cn/v1/user/info", bearer(k)),
    "zai": lambda k: get("https://api.z.ai/api/paas/v4/models", bearer(k)),
    "llm7": lambda k: get("https://api.llm7.io/v1/models", bearer(k)),
    "routeway": lambda k: get("https://api.routeway.ai/v1/models", bearer(k)),
    "unorouter": lambda k: get("https://api.unorouter.com/v1/models", bearer(k)),
    "aion": lambda k: get("https://api.aion.xyz/v1/models", bearer(k)),
    "sealion": lambda k: get("https://api.sealion.ai/v1/models", bearer(k)),
    "ollama": lambda k: get("https://ollama.com/api/tags", bearer(k)),
    "nvidia": lambda k: get("https://integrate.api.nvidia.com/v1/models", bearer(k)),
    "gemini": lambda k: get(f"https://generativelanguage.googleapis.com/v1beta/models?key={k}"),
    "huggingface": lambda k: get("https://huggingface.co/api/whoami-v2", bearer(k)),
    "xkiro": lambda k: get("https://api.xkiro.com/v1/models", bearer(k)),
    "felo": lambda k: get("https://api.felo.ai/api/account", bearer(k)),
    "cloudflare": lambda k: get("https://api.cloudflare.com/client/v4/user/tokens/verify", bearer(k)),
    "vercel": lambda k: get("https://api.vercel.com/v2/user", bearer(k)),
    "supabase": lambda k: get("https://api.supabase.com/v1/projects", bearer(k)),
    "pinecone": lambda k: get("https://api.pinecone.io/indexes", {"Api-Key": k}),
    "fly": fly,
}

if __name__ == "__main__":
    main()
