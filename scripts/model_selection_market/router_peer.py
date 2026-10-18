#!/usr/bin/env python3
"""MSM-007 — model_router peer hook (observe-only).

Produces ranked free peer candidates for a role from MSM bootstrap/join +
optional ledger aggregates. Does NOT mutate production weights.
Does NOT call network. Does NOT promote weights (observe until two cycles).

Integration surface for model_router / model_router_bootstrap:
  from scripts.model_selection_market.router_peer import observe_peers_for_role
  peers = observe_peers_for_role(role="triage")  # list[{model_id, weight, ...}]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .catalog_join import join_catalog
from .ledger import PerformanceLedger
from .selector import SelectionMode, select_models

PROMOTE_MIN_N = 2  # two observe cycles before any future promote path


def observe_peers_for_role(
    role: str = "triage",
    *,
    mode: str | SelectionMode = SelectionMode.SERIES,
    k: int = 5,
    catalog_path: Path | None = None,
    ledger_path: Path | None = None,
    weights: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return observe-only peer list for model_router.

    weight remains 1.0; confidence from ledger n when present.
    promote_eligible is informational only — never auto-applied here.
    """
    table = weights or join_catalog(catalog_path=catalog_path)

    # Overlay ledger confidence / n (still weight=1.0)
    if ledger_path is not None:
        led = PerformanceLedger(ledger_path)
        agg = led.aggregate(role=role)
        role_agg = (agg.get("aggregates") or {}).get(role) or {}
        role_map = (table.get("roles") or {}).get(role) or {}
        for mid, meta in role_map.items():
            if mid in role_agg:
                meta["n"] = role_agg[mid].get("n", 0)
                meta["confidence"] = role_agg[mid].get("confidence", 0.0)
                meta["weight"] = 1.0
                meta["weight_policy"] = "observe_only_until_promote"

    selection = select_models(role=role, mode=mode, k=k, weights=table)
    candidates = selection.get("candidates") or selection.get("chosen_set") or []
    if selection.get("mode") == "concurrent":
        # flatten first-of-role for router surface
        by = selection.get("candidates_by_role") or {}
        candidates = (by.get(role) or [])[:k]

    peers: list[dict[str, Any]] = []
    for c in candidates:
        n = int(c.get("n") or 0)
        peers.append(
            {
                "model_id": c.get("model_id"),
                "weight": 1.0,
                "confidence": c.get("confidence", 0.0),
                "n": n,
                "free": c.get("free", True),
                "promote_eligible": n >= PROMOTE_MIN_N,  # info only
                "weight_policy": "observe_only_until_promote",
            }
        )

    return {
        "schema_version": 1,
        "msm": "007",
        "role": role,
        "mode": selection.get("mode"),
        "policy": "observe_only",
        "weight_promote": False,
        "promote_min_n": PROMOTE_MIN_N,
        "peers": peers,
        "chosen": peers[0] if peers else None,
        "routing": selection.get("routing") or {"reason": "msm_observe_peer"},
        "join_sources": (table.get("join") or {}).get("sources"),
    }


def peers_as_router_pairs(observe: dict[str, Any], provider_default: str = "openrouter") -> list[tuple[str, str]]:
    """Map MSM peers to (provider, model) tuples for model_router ROLE_PEERS shape.

    Heuristic: gemini-* → gemini; else openrouter (free catalog home).
    """
    out: list[tuple[str, str]] = []
    for p in observe.get("peers") or []:
        mid = p.get("model_id") or ""
        if not mid:
            continue
        if mid.startswith("gemini"):
            provider = "gemini"
        elif "/" in mid:
            provider = provider_default
        else:
            provider = provider_default
        out.append((provider, mid))
    return out


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", default="triage")
    p.add_argument("--mode", default="series", choices=["series", "parallel", "concurrent"])
    p.add_argument("-k", type=int, default=5)
    p.add_argument("--catalog", type=Path, default=None)
    p.add_argument("--ledger", type=Path, default=None)
    p.add_argument("--pairs", action="store_true", help="print (provider, model) pairs")
    args = p.parse_args()
    obs = observe_peers_for_role(
        role=args.role,
        mode=args.mode,
        k=args.k,
        catalog_path=args.catalog,
        ledger_path=args.ledger,
    )
    if args.pairs:
        print(json.dumps(peers_as_router_pairs(obs), indent=2))
    else:
        print(json.dumps(obs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
