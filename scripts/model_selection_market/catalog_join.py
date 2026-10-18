#!/usr/bin/env python3
"""MSM-006 — live catalog join into equal-weight bootstrap (observe).

Sources (offline-safe order):
  1. explicit catalog path / dict
  2. docs/schemas/openrouter-free-catalog.json (committed snapshot)
  3. optional live_catalog_feed eligible rows (no network required for dual-gate)
  4. STATIC_FREE_SEED always merged as residual

Free-only. weight=1.0 on admit. No secrets. Network never required for tests.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bootstrap import ROLES, STATIC_FREE_SEED, bootstrap_equal_weights, load_static_free_seed

DEFAULT_OR_SNAPSHOT = Path("docs/schemas/openrouter-free-catalog.json")

# Default role affinity when catalog row has no roles metadata
_DEFAULT_ROLES = list(ROLES)
_REVIEWISH = ("coder", "code", "deepseek", "r1", "qwen")
_TRIAGEISH = ("gemma", "llama", "flash", "ox-alpha", "nemotron")


def _roles_for_id(model_id: str) -> list[str]:
    mid = model_id.lower()
    roles: list[str] = []
    if any(k in mid for k in _REVIEWISH):
        roles.append("review")
    if any(k in mid for k in _TRIAGEISH) or mid.endswith(":free") or mid == "stealth/ox-alpha":
        roles.extend(["triage", "invoke"])
    if not roles:
        roles = list(_DEFAULT_ROLES)
    # unique preserve order
    seen: set[str] = set()
    out: list[str] = []
    for r in roles:
        if r not in seen and r in ROLES:
            seen.add(r)
            out.append(r)
    return out or list(_DEFAULT_ROLES)


def _is_free_meta(model_id: str, meta: dict[str, Any] | None = None) -> bool:
    meta = meta or {}
    if meta.get("free") is True:
        return True
    if meta.get("free") is False:
        return False
    if model_id.endswith(":free"):
        return True
    if model_id in ("stealth/ox-alpha", "ox-alpha"):
        return True
    pricing = meta.get("pricing") or {}
    try:
        return float(pricing.get("prompt", 1)) == 0.0 and float(pricing.get("completion", 1)) == 0.0
    except (TypeError, ValueError):
        return False


def normalize_catalog_models(raw: Any) -> dict[str, dict[str, Any]]:
    """Accept several envelope shapes → {model_id: {free, roles, ...}}."""
    models: dict[str, dict[str, Any]] = {}

    def admit(mid: str, meta: dict[str, Any] | None = None) -> None:
        if not mid or not _is_free_meta(mid, meta):
            return
        m = dict(meta or {})
        m["free"] = True
        if "roles" not in m:
            m["roles"] = _roles_for_id(mid)
        models[mid] = m

    if raw is None:
        return models

    if isinstance(raw, dict):
        # envelope: {models: [...]} or {models: {id: meta}} or {ids: [...]} or flat {id: meta}
        if "models" in raw:
            body = raw["models"]
            if isinstance(body, list):
                for item in body:
                    if isinstance(item, str):
                        admit(item, {"free": True})
                    elif isinstance(item, dict):
                        mid = item.get("id") or item.get("model_id") or ""
                        admit(mid, item)
            elif isinstance(body, dict):
                for mid, meta in body.items():
                    admit(mid, meta if isinstance(meta, dict) else {"free": True})
        if "ids" in raw and isinstance(raw["ids"], list):
            for mid in raw["ids"]:
                if isinstance(mid, str):
                    admit(mid, {"free": True})
        if "eligible" in raw and isinstance(raw["eligible"], list):
            for item in raw["eligible"]:
                if isinstance(item, dict):
                    mid = item.get("id") or ""
                    admit(mid, {**item, "free": item.get("free", True)})
        # flat map fallback (no reserved keys only)
        reserved = {"schema_version", "source", "polled_at", "count", "ids", "models", "policy", "eligible", "schema", "timestamp"}
        for k, v in raw.items():
            if k in reserved:
                continue
            if isinstance(v, dict) and ("free" in v or "roles" in v or "pricing" in v):
                admit(k, v)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                admit(item, {"free": True})
            elif isinstance(item, dict):
                mid = item.get("id") or item.get("model_id") or ""
                admit(mid, item)

    return models


def load_catalog_file(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return normalize_catalog_models(raw)


def join_catalog(
    *,
    catalog_path: Path | None = None,
    catalog_dict: dict[str, Any] | list[Any] | None = None,
    include_static: bool = True,
    include_or_snapshot: bool = True,
) -> dict[str, Any]:
    """Merge free models from optional live sources into equal-weight table.

    Returns bootstrap_equal_weights() shape plus join provenance.
    """
    merged: dict[str, dict[str, Any]] = {}
    sources: list[str] = []

    if include_static:
        for mid, meta in load_static_free_seed().items():
            merged[mid] = dict(meta)
        sources.append("static_free_seed")

    if include_or_snapshot:
        snap = catalog_path or DEFAULT_OR_SNAPSHOT
        # If explicit path given, treat as primary; still may be OR snapshot
        loaded = load_catalog_file(Path(snap)) if Path(snap).is_file() else {}
        if loaded:
            for mid, meta in loaded.items():
                merged.setdefault(mid, meta)
            sources.append(str(snap))

    if catalog_dict is not None:
        loaded = normalize_catalog_models(catalog_dict)
        for mid, meta in loaded.items():
            merged.setdefault(mid, meta)
        sources.append("catalog_dict")

    table = bootstrap_equal_weights(merged)
    table["join"] = {
        "policy": "free_only_equal_weight",
        "sources": sources,
        "joined_model_ids": sorted(merged.keys()),
        "joined_count": len(merged),
        "observe_only": True,
        "weight_promote": False,
    }
    return table


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalog", type=Path, default=None, help="JSON catalog path")
    p.add_argument("--no-static", action="store_true")
    p.add_argument("--no-or-snapshot", action="store_true")
    args = p.parse_args()
    out = join_catalog(
        catalog_path=args.catalog,
        include_static=not args.no_static,
        include_or_snapshot=not args.no_or_snapshot or args.catalog is not None,
    )
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
