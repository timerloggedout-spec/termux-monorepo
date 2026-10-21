from __future__ import annotations

from typing import Any


def stage_ingest(context: dict[str, Any]) -> None:
    context["prs"] = list(context["snapshot"].get("prs") or [])
