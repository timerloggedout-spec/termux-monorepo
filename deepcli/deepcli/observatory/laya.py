"""Laya — merger. Weighted rank across Mev/Jev/Kev, resolve ties by Kev.

Role contract: (artifacts[i], jevs[i], kevs[i], weights) ->
{winner, ranked[], synthesis, provenance[]}
"""
from __future__ import annotations
from typing import Any


def _compose(a, j, k) -> float:
    jv = j.get("scores") or {}
    j_avg = sum(jv.values()) / len(jv) if jv else 0.0
    k_score = k.get("match_score", 0.0)
    return 0.7 * j_avg + 0.3 * k_score


def synthesize(artifacts: list[dict], jevs: list[dict], kevs: list[dict],
               weights: dict | None = None) -> dict:
    weights = weights or {"jev": 0.7, "kev": 0.3}
    scored = []
    for a, j, k in zip(artifacts, jevs, kevs):
        jev_scores = j.get("scores") or {}
        j_avg = sum(jev_scores.values()) / len(jev_scores) if jev_scores else 0.0
        k_score = k.get("match_score", 0.0)
        composite = weights["jev"] * j_avg + weights["kev"] * k_score
        scored.append((composite, j_avg, k_score, a, j, k))

    scored.sort(key=lambda x: (-x[0], -x[2]))
    ranked = []
    for composite, j_avg, k_score, a, j, k in scored:
        ranked.append({
            "provider": a.get("provider"),
            "model": a.get("model"),
            "composite": round(composite, 4),
            "jev_avg": round(j_avg, 4),
            "kev_match": round(k_score, 4),
            "preview": a.get("text", "")[:240],
        })

    winner = scored[0] if scored else None
    return {
        "role": "laya",
        "winner": ranked[0] if ranked else None,
        "ranked": ranked,
        "synthesis": winner[3].get("text", "") if winner else "",
        "provenance": [
            {"provider": a.get("provider"), "model": a.get("model"),
             "jev": j.get("judge_model"), "kev_ref": k.get("reference_id")}
            for _, _, _, a, j, k in scored
        ],
        "weights": weights,
    }
