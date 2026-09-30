"""Project a lane board from a snapshot. Vocab v2 only."""
from __future__ import annotations

from collections import Counter
from typing import Any

from ml.pipelines.command_center.constants import INVALID_PARKING, VOCAB
from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.moneyball.scorer import score


def _as_pr(row: dict[str, Any]) -> dict[str, Any]:
    """Normalize sweep JSON (base_ref) into classify_pr shape (base.ref)."""
    if "base" not in row and row.get("base_ref"):
        row = dict(row)
        row["base"] = {"ref": row["base_ref"]}
    if "user" in row and isinstance(row["user"], str):
        row = dict(row)
        row["user"] = {"login": row["user"]}
    if "gates" not in row:
        row = dict(row)
        row["gates"] = {}
    return row


def project_row(pr: dict[str, Any]) -> dict[str, Any]:
    shaped = _as_pr(pr)
    lane = classify_pr(shaped).value
    if lane in INVALID_PARKING:
        raise ValueError(f"invalid parking {lane} on #{shaped.get('number')}")
    return {
        "number": int(shaped["number"]),
        "title": shaped.get("title"),
        "lane": lane,
        "score": score(shaped),
        "reasons": list(shaped.get("reasons") or shaped.get("why") or []),
        "base": (shaped.get("base") or {}).get("ref") if isinstance(shaped.get("base"), dict) else shaped.get("base"),
        "html_url": shaped.get("html_url"),
    }


def board_from_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    rows = [project_row(pr) for pr in snapshot.get("prs") or []]
    counts = Counter(r["lane"] for r in rows)
    for lane in VOCAB:
        counts.setdefault(lane, 0)
    if any(k in counts for k in INVALID_PARKING):
        raise ValueError("board emitted invalid parking")
    return {
        "master_sha": snapshot.get("master_sha"),
        "observed_at": snapshot.get("observed_at"),
        "counts": dict(counts),
        "rows": rows,
        "vocab": list(VOCAB),
    }
