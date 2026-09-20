#!/usr/bin/env python3
"""Live multi-provider catalog feed for model-router and MoneyBall evidence.

Intended chain (AGENT-TEAM-ORCHESTRATION / SCOUT-ROSTER):

  provider catalogs (OR|Felo|Omni)
    → normalized eligible free/zero/trial rows
    → model-router peer candidates (runtime pick)
    → invocation telemetry
    → MoneyBall/3L0 scoring (post-success; not runtime pick)

Catalog is evidence + eligibility. MoneyBall does not pick the next HTTP model.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any

UA = "termux-monorepo-live-catalog-feed/1"
ENDPOINTS = {
    "openrouter": "https://openrouter.ai/api/v1/models",
    "felo": "https://openapi.felo.ai/api/v1/models",
    "omni": "https://cloud.omniroute.online/v1/models",
}
SECRET_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "felo": "FELO_AI_API",
    "omni": ("OMNI_API_KEY", "OMNIROUTE_API_KEY"),
}
# Documented free-trial when /models omits pricing (Felo OX Alpha)
DOCUMENTED_TRIAL = {
    ("felo", "ox-alpha"): "free_trial",
}

# Module-level constant sets and tuples to eliminate per-call allocation overhead
SPECIAL_FREE_MODELS = {"stealth/ox-alpha", "ox-alpha"}
PREFER_KEYWORDS = ("coder", "code", "qwen", "deepseek", "ox-alpha", "llama", "gemma")
REVIEW_KEYWORDS = ("coder", "code", "deepseek", "r1")


def _token(provider: str) -> str | None:
    env = SECRET_ENV[provider]
    if isinstance(env, tuple):
        for name in env:
            v = os.environ.get(name)
            if v:
                return v
        return None
    return os.environ.get(env) or None


def _is_free(model_id: str, pricing: dict | None, access: str | None = None) -> bool:
    if access == "free_trial":
        return True
    if model_id.endswith(":free"):
        return True
    if not pricing:
        return model_id in SPECIAL_FREE_MODELS
    try:
        return float(pricing.get("prompt", 1)) == 0.0 and float(pricing.get("completion", 1)) == 0.0
    except (TypeError, ValueError):
        return False


def poll_provider(provider: str) -> tuple[list[dict[str, Any]], str]:
    tok = _token(provider)
    if not tok:
        return [], "missing_secret"
    url = ENDPOINTS[provider]
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
            "Authorization": f"Bearer {tok}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:  # noqa: BLE001 — evidence path
        return [], f"error:{type(exc).__name__}"
    rows = []
    seen: set[str] = set()
    for item in data.get("data") or []:
        mid = item.get("id") or ""
        if not mid:
            continue
        seen.add(mid)
        pricing = item.get("pricing") or {}
        access = DOCUMENTED_TRIAL.get((provider, mid))
        free = _is_free(mid, pricing, access)
        rows.append(
            {
                "provider": provider,
                "id": mid,
                "free": free,
                "pricing_classification": (
                    "free_zero_price"
                    if free and not mid.endswith(":free") and access != "free_trial"
                    else ("free_suffix" if mid.endswith(":free") else ("free_trial" if access == "free_trial" else "other"))
                ),
                "context_length": item.get("context_length"),
                "raw_source": f"{provider}:/v1/models",
            }
        )
    for (p, mid), access in DOCUMENTED_TRIAL.items():
        if p != provider or mid in seen:
            continue
        rows.append(
            {
                "provider": provider,
                "id": mid,
                "free": True,
                "pricing_classification": "free_trial",
                "context_length": 1_000_000,
                "raw_source": f"{provider}:documented-trial",
            }
        )
    return rows, "live"


def load_eligible(
    providers: list[str] | None = None,
    cache_dir: str | None = None,
) -> dict[str, Any]:
    """Return eligible free/zero/trial rows + provenance for router + MB."""
    providers = providers or ["openrouter", "felo", "omni"]
    cache_dir = cache_dir or os.environ.get("COUNTER_DIR", "/tmp/model-router")
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    cache_path = Path(cache_dir) / "live_catalog_feed.json"

    # fresh if < 1h
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if time.time() - float(cached.get("timestamp", 0)) < 3600:
                cached["catalog_state"] = "cached"
                return cached
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            pass

    all_rows: list[dict[str, Any]] = []
    states: dict[str, str] = {}
    for p in providers:
        rows, state = poll_provider(p)
        states[p] = state
        all_rows.extend(rows)

    eligible: list[dict[str, Any]] = []
    by_p: dict[str, list[str]] = {}
    for r in all_rows:
        if r.get("free"):
            eligible.append(r)
            by_p.setdefault(r["provider"], []).append(r["id"])

    doc = {
        "schema": "live-catalog-feed/v1",
        "timestamp": time.time(),
        "catalog_state": "live" if any(s == "live" for s in states.values()) else "unavailable",
        "provider_states": states,
        "models": all_rows,
        "eligible": eligible,
        "eligible_ids_by_provider": by_p,
    }

    try:
        cache_path.write_text(json.dumps(doc), encoding="utf-8")
        # MoneyBall / scout evidence side-channel (no secrets)
        evid = Path("docs/ops/generated/catalog-feed")
        evid.mkdir(parents=True, exist_ok=True)
        slim = {
            "schema": doc["schema"],
            "timestamp": doc["timestamp"],
            "catalog_state": doc["catalog_state"],
            "provider_states": states,
            "eligible_count": len(eligible),
            "eligible_ids_by_provider": by_p,
        }
        (evid / "latest.json").write_text(json.dumps(slim, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    return doc


def peer_candidates_for_role(role: str, feed: dict[str, Any]) -> list[tuple[str, str]]:
    """Build (provider, model) peers from live eligible, ranked for role."""
    eligible = feed.get("eligible") or []

    def score(r: dict) -> int:
        mid = (r.get("id") or "").lower()
        s = 0
        for i, k in enumerate(PREFER_KEYWORDS):
            if k in mid:
                s += 100 - i * 5
        if role == "review" and any(k in mid for k in REVIEW_KEYWORDS):
            s += 30
        if r.get("provider") == "openrouter":
            s += 10
        if r.get("provider") == "felo":
            s += 12  # FELO wired as first-class peer
        if r.get("provider") == "omni":
            s += 8
        return s

    ranked = sorted(eligible, key=score, reverse=True)
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for r in ranked:
        key = (r["provider"], r["id"])
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
        if len(out) >= 24:
            break
    # Always allow omni auto aggregate if secret present
    if _token("omni") and ("omni", "auto/best-free") not in seen:
        out.insert(0, ("omni", "auto/best-free"))
    return out


if __name__ == "__main__":
    feed = load_eligible()
    print(
        json.dumps(
            {
                "state": feed.get("catalog_state"),
                "eligible": len(feed.get("eligible") or []),
                "by_provider": {k: len(v) for k, v in (feed.get("eligible_ids_by_provider") or {}).items()},
                "provider_states": feed.get("provider_states"),
            }
        )
    )
