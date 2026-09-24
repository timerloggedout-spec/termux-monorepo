"""Lane router: extract/hold/wait/observe/supersede short-circuit before scorer promote."""
from __future__ import annotations
from typing import Any, Mapping
from ml.pipelines.lib.types import Lane
from ml.pipelines.moneyball.scorer import classify as moneyball_classify, score
from .extract_rules import should_extract
from .hold_rules import should_hold
from .observe_rules import should_observe
from .wait_rules import should_wait
from .supersede_rules import should_supersede
from .minesweeper_rules import is_minesweeper

def classify_pr(pr: Mapping[str, Any]) -> Lane:
    if should_supersede(pr):
        return Lane.SUPERSEDE
    if should_extract(pr) or (is_minesweeper(pr) and int(pr.get("changed_files") or 0) > 40):
        if is_minesweeper(pr) and int(pr.get("changed_files") or 0) > 40:
            return Lane.EXTRACT
        if should_extract(pr):
            return Lane.EXTRACT
    if should_hold(pr):
        return Lane.HOLD
    if should_observe(pr):
        return Lane.OBSERVE
    if should_wait(pr):
        return Lane.WAIT
    return moneyball_classify(score(pr), pr)
