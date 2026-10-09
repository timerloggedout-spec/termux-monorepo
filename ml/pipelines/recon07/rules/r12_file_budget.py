"""CodeRabbit file budget is advisory, never a promote gate."""
from __future__ import annotations

from ml.pipelines.recon07.types import Finding

RULE_ID = "R12"
ADVISORY_FILE_BUDGET = 100


def evaluate(ctx: dict[str, object]) -> Finding:
    files = ctx.get("changed_files")
    if files is None:
        return Finding(RULE_ID, True, f"advisory budget is {ADVISORY_FILE_BUDGET} files; not a gate")
    try:
        count = int(files)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return Finding(RULE_ID, False, "changed_files must be an int when provided")
    return Finding(RULE_ID, count > 0, "file count does not authorize promote")
