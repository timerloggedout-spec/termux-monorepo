from __future__ import annotations

from typing import Any

from ml.pipelines.contracts.schema import validate_snapshot
from ml.pipelines.lib.errors import FixtureError


def stage_recon(context: dict[str, Any]) -> None:
    snapshot = context["snapshot"]
    errors = validate_snapshot(snapshot)
    if errors:
        raise FixtureError("; ".join(errors))
    context["master_sha"] = snapshot["master_sha"]
    context["issue"] = 175
