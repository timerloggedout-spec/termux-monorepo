"""Promote packet: dual-gate + clean mergeable + extract-sized."""
from __future__ import annotations

from typing import Any, Mapping

from ml.pipelines.contracts.gate import assert_promotable
from ml.pipelines.lib.errors import GateBlocked
from ml.pipelines.lib.types import Lane
from ml.pipelines.lib.weights import FILES_OVER_40


def promote_packet(pr: Mapping[str, Any], lane: Lane) -> dict[str, Any]:
    assert_promotable(pr, lane)
    files = int(pr.get("changed_files") or 0)
    if files > FILES_OVER_40:
        raise GateBlocked("extract required: changed_files over 40")
    return {
        "number": pr.get("number"),
        "lane": lane.value,
        "decision": "promote",
        "files": files,
    }
