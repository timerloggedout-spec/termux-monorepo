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
ZERO_PRICE_IDS = frozenset({"stealth/ox-alpha", "ox-alpha"})
PREFER_KEYWORDS = ("coder", "code", "qwen", "deepseek", "ox-alpha", "llama", "gemma")
REVIEW_KEYWORDS = ("coder", "code", "deepseek", "r1")
CODE_ROLES = frozenset({"review", "code", "implement"})
PROVIDER_SCORE = {"felo": 12, "openrouter": 10, "omni": 8}
DEFAULT_TTL_SEC = 3600
DEFAULT_PEER_LIMIT = 24
DEFAULT_MIN_PEER_SCORE = 0


def catalog_ttl_sec() -> int:
    raw = os.environ.get("CATALOG_TTL_SEC", "")
    try:
        ttl = int(raw) if raw else DEFAULT_TTL_SEC
    except ValueError:
        return DEFAULT_TTL_SEC
    return max(0, ttl)


def catalog_peer_limit() -> int:
    raw = os.environ.get("CATALOG_PEER_LIMIT", "")
    try:
        limit = int(raw) if raw else DEFAULT_PEER_LIMIT
    except ValueError:
        return DEFAULT_PEER_LIMIT
    return max(0, limit)


def catalog_min_peer_score() -> int:
    raw = os.environ.get("CATALOG_MIN_PEER_SCORE", "")
    try:
        score = int(raw) if raw else DEFAULT_MIN_PEER_SCORE
    except ValueError:
        return DEFAULT_MIN_PEER_SCORE
    return max(0, score)


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
        return model_id in ZERO_PRICE_IDS
    try:
        return float(pricing.get("prompt", 1)) == 0.0 and float(pricing.get("completion", 1)) == 0.0
    except (TypeError, ValueError):
        return False


def _pricing_classification(model_id: str, free: bool, access: str | None) -> str:
    if not free:
        return "other"
    if access == "free_trial":
        return "free_trial"
    if model_id.endswith(":free"):
        return "free_suffix"
    return "free_zero_price"


def _row(provider: str, mid: str, free: bool, access: str | None, context_length: Any, raw_source: str) -> dict[str, Any]:
    return {
        "provider": provider,
        "id": mid,
        "free": free,
        "pricing_classification": _pricing_classification(mid, free, access),
        "context_length": context_length,
        "raw_source": raw_source,
    }


def peer_score(role: str, row: dict[str, Any]) -> int:
    mid = (row.get("id") or "").lower()
    s = 0
    for i, k in enumerate(PREFER_KEYWORDS):
        if k in mid:
            s += 100 - i * 5
    if role in CODE_ROLES and any(k in mid for k in REVIEW_KEYWORDS):
        s += 30
    s += PROVIDER_SCORE.get(row.get("provider") or "", 0)
    return s


def rank_eligible(role: str, eligible: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach role_score once and sort descending. Does not mutate input rows."""
    scored: list[dict[str, Any]] = []
    for row in eligible:
        item = dict(row)
        item["role_score"] = peer_score(role, item)
        scored.append(item)
    scored.sort(key=lambda r: r["role_score"], reverse=True)
    return scored


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
        rows.append(_row(provider, mid, free, access, item.get("context_length"), f"{provider}:/v1/models"))
    for (p, mid), access in DOCUMENTED_TRIAL.items():
        if p != provider or mid in seen:
            continue
        rows.append(_row(provider, mid, True, access, 1_000_000, f"{provider}:documented-trial"))
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
    ttl = catalog_ttl_sec()
    peer_limit = catalog_peer_limit()
    min_peer_score = catalog_min_peer_score()

    # fresh if younger than TTL (0 forces refresh)
    if ttl > 0 and cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if time.time() - float(cached.get("timestamp", 0)) < ttl:
                cached["catalog_state"] = "cached"
                cached["peer_limit"] = peer_limit
                cached["min_peer_score"] = min_peer_score
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
        if not r.get("free"):
            continue
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
        "ttl_sec": ttl,
        "peer_limit": peer_limit,
        "min_peer_score": min_peer_score,
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
            "ttl_sec": ttl,
            "peer_limit": peer_limit,
            "min_peer_score": min_peer_score,
        }
        (evid / "latest.json").write_text(json.dumps(slim, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    return doc


def peer_candidates_for_role(role: str, feed: dict[str, Any]) -> list[tuple[str, str]]:
    """Build (provider, model) peers from live eligible, ranked for role."""
    eligible = feed.get("eligible") or []
    ranked = rank_eligible(role, eligible)
    limit = feed.get("peer_limit")
    if not isinstance(limit, int):
        limit = catalog_peer_limit()
    min_score = feed.get("min_peer_score")
    if not isinstance(min_score, int):
        min_score = catalog_min_peer_score()
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for r in ranked:
        if r["role_score"] < min_score:
            continue
        key = (r["provider"], r["id"])
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
        if limit > 0 and len(out) >= limit:
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
                "ttl_sec": feed.get("ttl_sec"),
                "peer_limit": feed.get("peer_limit"),
                "min_peer_score": feed.get("min_peer_score"),
            }
        )
    )
