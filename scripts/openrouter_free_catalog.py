#!/usr/bin/env python3
"""Shared OpenRouter free-catalog helpers.

Seed (docs/schemas/openrouter-free-catalog.json) = bootstrap only.
Every poll and every router use prefers a live catalog refresh.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

SNAPSHOT_PATH = os.environ.get(
    "OPENROUTER_FREE_SNAPSHOT",
    "docs/schemas/openrouter-free-catalog.json",
)
DEFAULT_URL = "https://openrouter.ai/api/v1/models"
USER_AGENT = "termux-monorepo-openrouter-free-catalog/1.1"

LEGACY_MODELS = {
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-12b-it:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "qwen/qwen3-coder:free",
    "deepseek/deepseek-r1:free",
    "cohere/north-mini-code:free",
    "stealth/ox-alpha",
    "auto/best-free",
}


def is_free_openrouter_model(model_id, pricing=None):
    if not model_id:
        return False
    if model_id.endswith(":free"):
        return True
    if pricing is None:
        return model_id in {
            "stealth/ox-alpha",
            "google/lyria-3-clip-preview",
            "google/lyria-3-pro-preview",
        }
    try:
        return float(pricing.get("prompt", 1.0)) == 0.0 and float(
            pricing.get("completion", 1.0)
        ) == 0.0
    except (TypeError, ValueError):
        return False


def load_seed_catalog(path=None):
    path = path or SNAPSHOT_PATH
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        ids = data.get("ids") or [
            m.get("id") for m in data.get("models") or [] if m.get("id")
        ]
        return [i for i in ids if i] or None
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        sys.stderr.write(f"Warning: seed catalog unreadable ({error}).\n")
        return None


def fetch_live_free_ids(timeout=5.0):
    try:
        request = urllib.request.Request(
            DEFAULT_URL, headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        free = []
        for model in data.get("data", []):
            model_id = model.get("id", "")
            pricing = model.get("pricing", {})
            if is_free_openrouter_model(model_id, pricing) and model_id:
                free.append(model_id)
        return free or None
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.stderr.write(f"Warning: live OpenRouter poll failed ({error}).\n")
        return None


def resolve_free_catalog(counter_dir="/tmp/model-router"):
    """live → cached(1h) → seed → legacy.

    Seed is bootstrap only. Live is preferred on every call.
    """
    cache_file = os.path.join(counter_dir, "openrouter_models_cache.json")
    cached_models = None
    cached_time = 0
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as handle:
                cache_data = json.load(handle)
            cached_models = cache_data.get("models")
            cached_time = cache_data.get("timestamp", 0)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            pass

    live = fetch_live_free_ids()
    if live is not None:
        try:
            os.makedirs(counter_dir, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as handle:
                json.dump({"timestamp": time.time(), "models": live}, handle)
        except (OSError, TypeError, ValueError):
            pass
        return live, "live"

    if cached_models is not None and time.time() - cached_time < 3600:
        return cached_models, "cached"

    seed = load_seed_catalog()
    if seed is not None:
        return seed, "seed"

    if cached_models is not None:
        return cached_models, "stale"

    return list(LEGACY_MODELS), "legacy"


def expand_openrouter_peers(base_peers, free_models):
    if not free_models:
        return list(base_peers)
    curated = list(base_peers)
    seen = {model for provider, model in curated if provider == "openrouter"}
    preferred_extra = [
        "stealth/ox-alpha",
        "z-ai/glm-5.2:free",
        "nvidia/nemotron-3.5-lightning:free",
        "poolside/laguna-s-2.1:free",
        "cohere/north-mini-code:free",
    ]
    ordered = []
    free_set = set(free_models)
    for mid in preferred_extra:
        if mid in free_set and mid not in seen:
            ordered.append(mid)
            seen.add(mid)
    for mid in sorted(free_set):
        if mid in seen or "lyria" in mid:
            continue
        ordered.append(mid)
        seen.add(mid)
    expanded = list(curated)
    for mid in ordered:
        expanded.append(("openrouter", mid))
    return expanded
