from __future__ import annotations

from typing import Any

from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.moneyball.scorer import score
from ml.pipelines.viz.projection import project


def emit_cctv(snapshot: dict[str, Any]) -> dict[str, Any]:
    lanes = [
        {
            "number": pr["number"],
            "lane": classify_pr(pr).value,
            "score": score(pr),
            "why": pr.get("why"),
            "title": pr.get("title"),
        }
        for pr in snapshot.get("prs") or []
    ]
    return project(snapshot, lanes)
