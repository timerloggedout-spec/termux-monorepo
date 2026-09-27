#!/usr/bin/env python3
"""Deterministic fixtures for the continuous-evaluation PR boundary."""

from __future__ import annotations

import re

SESSION_TITLE = re.compile(
    r"^(?:SUPERSEDED:\s*)?ops\(skills\):\s*bind session\b|^ops\(session\)|^ops/session-",
    re.I,
)

EVIDENCE_PREFIXES = (
    ".agents/skills/",
    "docs/ops/sessions/",
    "docs/ops/generated/",
)


def evidence_only(path: str) -> bool:
    return (
        path.startswith(EVIDENCE_PREFIXES)
        or bool(re.match(r"^docs/ops/SESSION-[^/]+\.md$", path, re.I))
        or path in {"docs/ops/LANE-MATRIX.md", "docs/icm/cards/session-ssot-pulse.md"}
    )


def is_session_only(title: str, paths: list[str]) -> bool:
    return bool(paths) and SESSION_TITLE.search(title) is not None and all(
        evidence_only(path) for path in paths
    )


def test_session_bind_is_suppressed() -> None:
    assert is_session_only(
        "ops(skills): bind session after live master 13191c2",
        [
            ".agents/skills/adaptive-wait/SKILL.md",
            ".agents/skills/evidence-led-monorepo-ops/SKILL.md",
            ".agents/skills/stepie-stepwise-ops/SKILL.md",
            "docs/ops/sessions/2026-09-27-1014-pdt.md",
        ],
    )


def test_real_catalog_perf_pr_is_not_suppressed() -> None:
    assert not is_session_only(
        "perf(catalog): rank peers with one peer_score pass per row",
        ["scripts/live_catalog_feed.py", "tests/test_live_catalog_feed.py"],
    )


if __name__ == "__main__":
    test_session_bind_is_suppressed()
    test_real_catalog_perf_pr_is_not_suppressed()
    print("pr-scope-guard fixtures: PASS")
