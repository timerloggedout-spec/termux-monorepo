"""Compare catalog intent with the live classifier. Disagreement is evidence, not a merge."""
from __future__ import annotations

from typing import Any

from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.recon07.families import forbidden_actions
from ml.pipelines.recon07.registry import load_observations
from ml.pipelines.recon07.types import Observation


def as_pr(obs: Observation) -> dict[str, Any]:
    return {
        "number": obs.number,
        "title": obs.title,
        "base": {"ref": obs.base},
        "why": ",".join(obs.reasons),
        "reasons": list(obs.reasons),
        "wholesale": "ml-wholesale-no-go" in obs.reasons or "wholesale-ml" in obs.reasons,
        "keep_alive": "ml-keep-alive-rebase-required" in obs.reasons,
        "draft": False,
        "mergeable_state": "unknown",
    }


def disagreements(rows: list[Observation] | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for obs in rows if rows is not None else load_observations():
        if obs.kind != "pr":
            continue
        classified = classify_pr(as_pr(obs)).value
        out.append(
            {
                "number": obs.number,
                "catalog": obs.lane,
                "classifier": classified,
                "agree": obs.lane == classified,
                "blocked": obs.lane != "CANDIDATE" or classified != "CANDIDATE",
                "forbidden": list(forbidden_actions(obs.number)),
            }
        )
    return out


def summary(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    data = rows if rows is not None else disagreements()
    return {
        "compared": len(data),
        "agree": sum(1 for row in data if row["agree"]),
        "blocked": sum(1 for row in data if row["blocked"]),
        "promotable": [row["number"] for row in data if not row["blocked"]],
    }
