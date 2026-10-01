#!/usr/bin/env python3
"""MSM-001 — equal-weight role table bootstrap.

Public leaderboards are features only. Every eligible free model starts at weight=1.0.
Live catalog join is optional; static free seed always works offline for dual-gate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROLES = ("triage", "review", "invoke")

# Offline-safe free seed aligned with model-rotation / success-matrix (no network).
STATIC_FREE_SEED: dict[str, dict[str, Any]] = {
    "stealth/ox-alpha": {"roles": list(ROLES), "free": True, "note": "zero pricing"},
    "meta-llama/llama-3.3-70b-instruct:free": {"roles": list(ROLES), "free": True},
    "google/gemma-3-12b-it:free": {"roles": ["triage", "invoke"], "free": True},
    "qwen/qwen3-coder:free": {"roles": ["review"], "free": True},
    "deepseek/deepseek-r1:free": {"roles": ["review"], "free": True},
    "google/gemma-4-31b-it:free": {"roles": list(ROLES), "free": True},
    "google/gemma-4-26b-a4b-it:free": {"roles": list(ROLES), "free": True},
    "cohere/north-mini-code:free": {"roles": ["review", "invoke"], "free": True},
    "gemini-3.1-flash-lite": {"roles": ["triage", "invoke", "review"], "free": True, "provider": "gemini"},
    "gemini-3.5-flash-lite": {"roles": ["triage", "invoke", "review"], "free": True, "provider": "gemini"},
    "gemini-3.5-flash": {"roles": ["review"], "free": True, "provider": "gemini"},
}


def load_static_free_seed() -> dict[str, dict[str, Any]]:
    return {k: dict(v) for k, v in STATIC_FREE_SEED.items()}


def bootstrap_equal_weights(
    models: dict[str, dict[str, Any]] | None = None,
    *,
    roles: tuple[str, ...] = ROLES,
) -> dict[str, Any]:
    """Return role → model_id → {weight, confidence, n, free}.

    weight always 1.0 on admit. confidence 0.0 until ledger samples exist.
    """
    src = models if models is not None else load_static_free_seed()
    table: dict[str, dict[str, dict[str, Any]]] = {r: {} for r in roles}
    skipped: list[str] = []
    for mid, meta in src.items():
        if not meta.get("free", False):
            skipped.append(mid)
            continue
        model_roles = meta.get("roles") or list(roles)
        for role in model_roles:
            if role not in table:
                continue
            table[role][mid] = {
                "weight": 1.0,
                "confidence": 0.0,
                "n": 0,
                "free": True,
                "note": meta.get("note"),
            }
    return {
        "schema_version": 1,
        "policy": "equal_weight_bootstrap",
        "public_boards": "features_only",
        "roles": table,
        "skipped_non_free": skipped,
        "model_count": sum(len(v) for v in table.values()),
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true", help="print bootstrap table")
    p.add_argument("--catalog", type=Path, default=None, help="optional JSON catalog path")
    args = p.parse_args()
    models = None
    if args.catalog and args.catalog.is_file():
        raw = json.loads(args.catalog.read_text(encoding="utf-8"))
        # Accept {model_id: meta} or {"models": {..}}
        models = raw.get("models", raw)
    out = bootstrap_equal_weights(models)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
