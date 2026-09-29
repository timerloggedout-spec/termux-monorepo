"""Classify a PR into vocab v2. Never emit HOLD/WAIT/OBSERVE."""
from __future__ import annotations

from typing import Any

from ml.pipelines.lanes.minesweeper_rules import minesweeper_extract
from ml.pipelines.lanes.supersede_rules import should_supersede
from ml.pipelines.lanes.vocab import Lane


def classify_pr(pr: dict[str, Any]) -> Lane:
    base = (pr.get("base") or {}).get("ref") if isinstance(pr.get("base"), dict) else pr.get("base")
    if pr.get("wholesale") or "ml-wholesale" in str(pr.get("why") or ""):
        return Lane.EXTRACT
    if minesweeper_extract(pr):
        return Lane.EXTRACT
    if str(pr.get("title") or "").startswith("feat(ml):") and pr.get("keep_alive"):
        return Lane.EXTRACT
    if should_supersede(pr):
        return Lane.SUPERSEDE
    if pr.get("draft") or pr.get("mergeable_state") == "dirty":
        return Lane.NEED_EVIDENCE
    if base and base != "master":
        return Lane.NEED_EVIDENCE
    if not pr.get("gates", {}).get("repo-gate") or not pr.get("gates", {}).get("termux-smoke"):
        return Lane.NEED_EVIDENCE
    return Lane.CANDIDATE
