#!/usr/bin/env python3
"""Consolidate OpenRouter free-model polling.

Single source used by:
  - scripts/model_router.py (runtime soft-budget routing)
  - .github/workflows/openrouter-free-catalog-sync.yml (daily drift PR)

Free rule: model id ends with :free OR prompt+completion pricing == 0
(covers stealth/ox-alpha and other zero-price stealth listings).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

DEFAULT_URL = "https://openrouter.ai/api/v1/models"
USER_AGENT = "termux-monorepo-openrouter-free-catalog/1.0"


def is_free_openrouter_model(model_id: str, pricing=None) -> bool:
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


def fetch_catalog(url: str = DEFAULT_URL, timeout: float = 15.0) -> list[dict]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return list(payload.get("data") or [])


def free_models_from_catalog(catalog: list[dict]) -> list[dict]:
    free = []
    for model in catalog:
        model_id = model.get("id") or ""
        pricing = model.get("pricing") or {}
        if not is_free_openrouter_model(model_id, pricing):
            continue
        free.append(
            {
                "id": model_id,
                "name": model.get("name") or model_id,
                "context_length": model.get("context_length"),
                "pricing": {
                    "prompt": str(pricing.get("prompt", "")),
                    "completion": str(pricing.get("completion", "")),
                },
                "architecture": model.get("architecture") or {},
            }
        )
    free.sort(key=lambda item: item["id"])
    return free


def write_snapshot(path: Path, free_models: list[dict], source: str = "live") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {
        "schema_version": 1,
        "source": source,
        "polled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(free_models),
        "models": free_models,
        "ids": [m["id"] for m in free_models],
    }
    path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")


def load_snapshot(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def drift_report(previous: dict | None, current_ids: list[str]) -> dict:
    prev_ids = set((previous or {}).get("ids") or [])
    curr_ids = set(current_ids)
    added = sorted(curr_ids - prev_ids)
    removed = sorted(prev_ids - curr_ids)
    return {
        "changed": bool(added or removed),
        "added": added,
        "removed": removed,
        "prev_count": len(prev_ids),
        "curr_count": len(curr_ids),
        "ox_alpha_present": "stealth/ox-alpha" in curr_ids,
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    out = Path(os.environ.get("OPENROUTER_FREE_SNAPSHOT", "docs/schemas/openrouter-free-catalog.json"))
    if "--out" in argv:
        idx = argv.index("--out")
        out = Path(argv[idx + 1])

    previous = load_snapshot(out)
    try:
        catalog = fetch_catalog()
        free = free_models_from_catalog(catalog)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.stderr.write(f"poll failed: {error}\n")
        return 2

    write_snapshot(out, free, source="live")
    report = drift_report(previous, [m["id"] for m in free])
    print(json.dumps(report, indent=2))
    if report["changed"]:
        return 1  # non-zero signals drift for CI
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
