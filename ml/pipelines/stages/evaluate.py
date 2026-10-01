from __future__ import annotations

from typing import Any

from ml.pipelines.contracts.promote import promote_decision
from ml.pipelines.lanes.vocab import Lane


def stage_evaluate(context: dict[str, Any]) -> None:
    decisions = []
    prs = {pr["number"]: pr for pr in context.get("prs") or []}
    for row in context.get("lanes") or []:
        pr = prs.get(row["number"], {})
        pr = {**pr, "lane": row["lane"]}
        decisions.append(
            {
                "number": row["number"],
                "decision": promote_decision(pr),
                "lane": row["lane"],
                "promotable": row["lane"] == Lane.CANDIDATE.value,
            }
        )
    context["decisions"] = decisions
