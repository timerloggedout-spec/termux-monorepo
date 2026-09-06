"""MLP-02: bind live issues/PRs onto the Issue #175 matrix."""
from __future__ import annotations

from typing import Any


WATCH = {
    175: "operator-matrix",
    213: "ml-pipelines",
    265: "providers-manus",
    268: "actions-hygiene",
    294: "she-p0",
    337: "continuous-eval",
    408: "ox-alpha",
    192: "actions-refinements",
}


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    open_issues = {int(i["number"]): i for i in snapshot.get("issues", [])}
    bound = []
    for number, role in WATCH.items():
        issue = open_issues.get(number)
        bound.append(
            {
                "number": number,
                "role": role,
                "open": bool(issue),
                "title": (issue or {}).get("title"),
                "labels": (issue or {}).get("labels") or [],
            }
        )
    return {"watch": bound, "open_watch": sum(1 for row in bound if row["open"])}
