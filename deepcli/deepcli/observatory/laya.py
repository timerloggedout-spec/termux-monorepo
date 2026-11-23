"""Laya — aligned evidence reducer for the local observatory role.

Each candidate keeps one artifact, one critique, and one verification result.
Candidate IDs preserve identity across partial stage failures.
"""
from __future__ import annotations


def _compose(a, j, k, weights) -> float:
    jv = j.get("scores") or {}
    j_avg = sum(jv.values()) / len(jv) if jv else 0.0
    k_score = k.get("match_score", 0.0)
    return weights["jev"] * j_avg + weights["kev"] * k_score


def synthesize(artifacts: list[dict], jevs: list[dict], kevs: list[dict],
               weights: dict | None = None) -> dict:
    """Rank only complete, identity-aligned candidate evidence triples."""
    weights = weights or {"jev": 0.7, "kev": 0.3}
    if not (len(artifacts) == len(jevs) == len(kevs)):
        raise ValueError("artifacts, jevs, and kevs must have equal lengths")

    scored = []
    excluded = []
    stage_has_ids = [
        any(record.get("candidate_id") is not None for record in records)
        for records in (artifacts, jevs, kevs)
    ]
    if any(stage_has_ids):
        if not all(stage_has_ids):
            raise ValueError("candidate IDs must be present in every evidence stage")

        def index_by_candidate(records, stage):
            indexed = {}
            for record in records:
                candidate_id = record.get("candidate_id")
                if candidate_id is None:
                    raise ValueError(f"{stage} record is missing candidate_id")
                if candidate_id in indexed:
                    raise ValueError(f"{stage} contains duplicate candidate_id: {candidate_id}")
                indexed[candidate_id] = record
            return indexed

        jevs_by_id = index_by_candidate(jevs, "jev")
        kevs_by_id = index_by_candidate(kevs, "kev")
        artifact_ids = {record["candidate_id"] for record in artifacts}
        if artifact_ids != set(jevs_by_id) or artifact_ids != set(kevs_by_id):
            raise ValueError("candidate ID sets differ across evidence stages")
        triples = [
            (artifact, jevs_by_id[artifact["candidate_id"]],
             kevs_by_id[artifact["candidate_id"]])
            for artifact in artifacts
        ]
    else:
        # Compatibility path for historical records without candidate IDs.
        triples = list(zip(artifacts, jevs, kevs))

    for a, j, k in triples:
        candidate_id = a.get("candidate_id")
        if not all(x.get("ok", True) for x in (a, j, k)):
            excluded.append({
                "candidate_id": candidate_id,
                "provider": a.get("provider"),
                "model": a.get("model"),
                "artifact_ok": a.get("ok", True),
                "jev_ok": j.get("ok", True),
                "kev_ok": k.get("ok", True),
            })
            continue
        jev_scores = j.get("scores") or {}
        j_avg = sum(jev_scores.values()) / len(jev_scores) if jev_scores else 0.0
        k_score = k.get("match_score", 0.0)
        composite = _compose(a, j, k, weights)
        scored.append((composite, j_avg, k_score, a, j, k, candidate_id))

    scored.sort(key=lambda x: (-x[0], -x[2]))
    ranked = []
    for composite, j_avg, k_score, a, j, k, candidate_id in scored:
        ranked.append({
            "candidate_id": candidate_id,
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
        "excluded": excluded,
        "synthesis": winner[3].get("text", "") if winner else "",
        "provenance": [
            {"candidate_id": candidate_id,
             "provider": a.get("provider"), "model": a.get("model"),
             "jev": j.get("judge_model"), "kev_ref": k.get("reference_id")}
            for _, _, _, a, j, k, candidate_id in scored
        ],
        "weights": weights,
    }
