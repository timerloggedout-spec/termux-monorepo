#!/usr/bin/env python3
"""MSM-003 — explicit series | parallel | concurrent selection modes."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from .bootstrap import bootstrap_equal_weights


class SelectionMode(str, Enum):
    SERIES = "series"
    PARALLEL = "parallel"
    CONCURRENT = "concurrent"


def select_models(
    *,
    role: str = "triage",
    mode: SelectionMode | str = SelectionMode.SERIES,
    k: int = 3,
    weights: dict[str, Any] | None = None,
    roles_for_concurrent: tuple[str, ...] = ("triage", "review", "invoke"),
) -> dict[str, Any]:
    """Dense-feedback selection. Does not invoke LLMs; routes candidates only."""
    table = weights or bootstrap_equal_weights()
    mode_s = SelectionMode(mode) if not isinstance(mode, SelectionMode) else mode

    def ranked(role_name: str) -> list[dict[str, Any]]:
        role_map = (table.get("roles") or {}).get(role_name) or {}
        items = [
            {
                "model_id": mid,
                "weight": meta.get("weight", 1.0),
                "confidence": meta.get("confidence", 0.0),
                "n": meta.get("n", 0),
                "free": meta.get("free", True),
            }
            for mid, meta in role_map.items()
            if meta.get("free", True)
        ]
        items.sort(key=lambda x: (-x["weight"], -x["confidence"], x["model_id"]))
        return items

    if mode_s == SelectionMode.SERIES:
        cands = ranked(role)
        chosen = cands[0] if cands else None
        return {
            "mode": mode_s.value,
            "role": role,
            "candidates": cands[: max(k, 1)],
            "chosen": chosen,
            "routing": {
                "reason": "series_highest_weight_then_confidence",
                "criteria_matched": ["free_only", "equal_or_evidence_weight"],
            },
        }

    if mode_s == SelectionMode.PARALLEL:
        cands = ranked(role)[: max(1, min(k, 5))]
        return {
            "mode": mode_s.value,
            "role": role,
            "candidates": cands,
            "chosen_set": cands,
            "routing": {
                "reason": "parallel_sample_k_free",
                "criteria_matched": ["free_only", f"k<={k}"],
            },
        }

    # concurrent: independent cards per role
    by_role = {r: ranked(r)[:1] for r in roles_for_concurrent}
    return {
        "mode": mode_s.value,
        "roles": list(roles_for_concurrent),
        "chosen_by_role": {r: (v[0] if v else None) for r, v in by_role.items()},
        "candidates_by_role": by_role,
        "routing": {
            "reason": "concurrent_independent_cards_join_on_canny",
            "criteria_matched": ["free_only", "independent_roles"],
            "join": "canny_or_job_contract",
        },
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", default="triage")
    p.add_argument("--mode", default="series", choices=[m.value for m in SelectionMode])
    p.add_argument("-k", type=int, default=3)
    args = p.parse_args()
    print(json.dumps(select_models(role=args.role, mode=args.mode, k=args.k), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
