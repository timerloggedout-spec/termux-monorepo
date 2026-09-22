"""gate: Promote only when dual gates are green and lane is promote."""
from __future__ import annotations

from typing import Any, Mapping

from ml.pipelines.lib.errors import GateBlocked
from ml.pipelines.lib.types import Lane


def assert_promotable(pr: Mapping[str, Any], lane: Lane) -> None:
    if lane is not Lane.PROMOTE:
        raise GateBlocked(f"lane {lane.value} is not promote")
    if pr.get("dual_gate") != "green":
        raise GateBlocked("dual_gate is not green")
    if pr.get("mergeable_state") != "clean":
        raise GateBlocked("mergeable_state is not clean")
    if pr.get("gitlab_required"):
        raise GateBlocked("gitlab must remain non-blocking")
