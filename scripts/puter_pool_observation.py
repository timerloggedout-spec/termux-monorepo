#!/usr/bin/env python3
"""Collect privacy-minimized Puter Pool runtime counters for the provider registry.

Reads only GET /v1/models, /api/stats, /api/queue, /healthz and /readyz.
The collector deliberately excludes account records, balances, request history,
prompts, completions, tokens and local SQLite content. Puter Pool CreditTracker
values are synthetic local scheduler units, so quota readings remain unknown.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from scripts.puter_pool_catalog import DEFAULT_BASE_URL, _catalog_url, fetch_models

MAX_RESPONSE_BYTES = 512 * 1024
PATHS = ("/api/stats", "/api/queue", "/healthz", "/readyz")
COUNTERS = (
    "totalAccounts", "activeAccounts", "disabledAccounts", "exhaustedAccounts",
    "errorAccounts", "totalRequests", "successfulRequests", "failedRequests",
    "queuedRequests", "activeRequests", "averageLatency", "uptime",
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _fetch_json(base_url: str, path: str, timeout: float, api_key: str | None) -> dict[str, Any]:
    if path not in PATHS:
        raise ValueError("unsupported_puter_pool_observation_path")
    models_url = _catalog_url(base_url)
    parsed = urllib.parse.urlsplit(models_url)
    url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
    headers = {"Accept": "application/json", "User-Agent": "termux-monorepo-puter-pool-observer/1"}
    if api_key:
        headers["x-api-key"] = api_key
    request = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(_NoRedirect, urllib.request.HTTPHandler(), urllib.request.HTTPSHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"puter_pool_http_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("puter_pool_unreachable") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("puter_pool_response_too_large")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("puter_pool_invalid_json") from None
    if not isinstance(value, dict):
        raise RuntimeError("puter_pool_invalid_response_shape")
    return value


def _nonnegative_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def collect_observation(base_url: str = DEFAULT_BASE_URL, timeout: float = 8.0, api_key: str | None = None) -> dict[str, Any]:
    models = fetch_models(base_url, timeout, api_key)
    snapshots = {path: _fetch_json(base_url, path, timeout, api_key) for path in PATHS}
    stats, queue = snapshots["/api/stats"], snapshots["/api/queue"]
    counters = {key: _nonnegative_int(stats.get(key)) for key in COUNTERS}
    counters["queuedRequests"] = _nonnegative_int(queue.get("queuedRequests")) if _nonnegative_int(queue.get("queuedRequests")) is not None else counters["queuedRequests"]
    counters["activeRequests"] = _nonnegative_int(queue.get("activeRequests")) if _nonnegative_int(queue.get("activeRequests")) is not None else counters["activeRequests"]
    health, ready = snapshots["/healthz"], snapshots["/readyz"]
    observed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema": "provider-runtime-observation/v1",
        "provider_id": "g4f.puter",
        "provider": "g4f/Puter",
        "source_repository": "timerloggedout-spec/puter-pool_fork",
        "observed_at": observed_at,
        "pool": {
            "health": health.get("status") if isinstance(health.get("status"), str) else "unknown",
            "readiness": ready.get("status") if isinstance(ready.get("status"), str) else "unknown",
            "strategy": stats.get("strategy") if stats.get("strategy") in {"round-robin", "least-used"} else None,
            "counters": counters,
            "model_count": len(models),
            "model_ids": [row["id"] for row in models],
        },
        "quota": {
            "status": "unknown", "used": None, "limit": None, "remaining": None, "reset": None,
            "reason": "Puter Pool CreditTracker is a local heuristic; provider-authoritative quota remains unobserved.",
        },
        "privacy": {
            "account_inventory_collected": False, "account_balances_collected": False,
            "request_history_collected": False, "prompts_collected": False,
            "completions_collected": False, "credentials_collected": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("PUTER_POOL_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--output", default="/tmp/provider-observations/puter-pool.json")
    parser.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args(argv)
    if not 0.1 <= args.timeout <= 30:
        parser.error("--timeout must be between 0.1 and 30 seconds")
    document = collect_observation(args.base_url, args.timeout, os.environ.get("PUTER_POOL_API_KEY"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".puter-pool-observation-", suffix=".tmp", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, output)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    counters = document["pool"]["counters"]
    print(f"provider=g4f/Puter models={document['pool']['model_count']} requests={counters['totalRequests']} quota=unknown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
