"""Kev — verifier. Compare artifact against reference corpus.

Role contract: (artifact_text, reference: dict) -> {match_score, deltas[],
reference_id}

Reference can be: (a) another artifact's text, (b) a ground-truth string,
(c) an embedding similarity against a local bank entry.
Strategy chosen by config; default = exact-token F1.
"""
from __future__ import annotations
import re
from typing import Any


def _tok(s: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_]+", s.lower()))


def verify(artifact: dict, reference: dict, method: str = "token_f1") -> dict:
    a = artifact.get("text", "")
    r = reference.get("text") or reference.get("content", "")
    if method == "token_f1":
        ta, tr = _tok(a), _tok(r)
        if not ta or not tr:
            score = 0.0
            deltas = []
        else:
            inter = ta & tr
            precision = len(inter) / len(ta)
            recall = len(inter) / len(tr)
            score = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
            deltas = sorted(tr - ta)[:40]
        return {
            "role": "kev", "method": method,
            "match_score": round(score, 4),
            "deltas": deltas,
            "reference_id": reference.get("id", ""),
        }
    elif method == "exact":
        return {
            "role": "kev", "method": "exact",
            "match_score": 1.0 if a.strip() == r.strip() else 0.0,
            "deltas": [] if a.strip() == r.strip() else [r[:200]],
            "reference_id": reference.get("id", ""),
        }
    else:
        raise ValueError(f"unknown kev method: {method}")
