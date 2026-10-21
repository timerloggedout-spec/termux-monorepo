#!/usr/bin/env python3
"""Deterministic contract check for the adaptive-wait/evidence-led skill cluster."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAIRS = {
    ".agents/skills/adaptive-wait/SKILL.md": "docs/ops/skills/adaptive-wait/SKILL.md",
    ".agents/skills/evidence-led-monorepo-ops/SKILL.md": "docs/ops/skills/evidence-led-monorepo-ops/SKILL.md",
}
REQUIRED = {
    ".agents/skills/adaptive-wait/SKILL.md": [
        "## Control objective",
        "## State machine",
        "## Adaptive cadence",
        "## Mandatory re-fetch contract",
        "## Evidence receipt",
        "## Promotion boundary",
    ],
    ".agents/skills/evidence-led-monorepo-ops/SKILL.md": [
        "## Operating contract",
        "## 1. Reconstruct current state",
        "## 2. Evidence hierarchy",
        "## 3. Evidence identity",
        "## 5. Adaptive WAIT integration",
        "## 7. Promotion",
        "## 10. Closeout receipt",
    ],
}

# Bodies that mean a writer clobbered the file instead of appending to it.
# Single source of truth lives in skill_clobber.py (shared with the SHE heal workflow).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from skill_clobber import MIN_BODY_BYTES, PLACEHOLDER_PATTERNS, reference_text  # noqa: E402

# Content-change evaluation against the parent commit (PR base or HEAD~1).
# Lines are compared as a multiset of stripped, non-blank lines, so moving or
# reordering content is not counted as loss; only lines that no longer appear are.
MAX_LOST_RATIO = 0.5        # fail: more than half of the parent's lines are gone
WARN_LOST_RATIO = 0.10      # warn: more than 10% gone (edits/trims worth a look)
MIN_LINES_FOR_LOSS_CHECK = 100
SHRINK_OVERRIDE_TOKEN = "[allow-skill-shrink]"
SESSION_HEADER = re.compile(r"(?m)^(?:## )?Session (\d{4}-\d{2}-\d{2})")


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def content_delta(before: str, after: str) -> dict:
    """Classify the change: lost/added lines (order-insensitive) and whether order moved."""
    from collections import Counter
    b, a = Counter(_lines(before)), Counter(_lines(after))
    lost = sum((b - a).values())
    added = sum((a - b).values())
    total = sum(b.values()) or 1
    common_b = [ln for ln in _lines(before) if ln in a]
    common_a = [ln for ln in _lines(after) if ln in b]
    return {
        "parent_lines": total,
        "lost": lost,
        "added": added,
        "lost_ratio": lost / total,
        "reordered": common_b != common_a,
    }


def section_order_ok(text: str, required: list[str]) -> bool:
    pos = [text.find(s) for s in required]
    return all(p >= 0 for p in pos) and pos == sorted(pos)


def session_dates_monotonic(text: str) -> bool:
    dates = SESSION_HEADER.findall(text)
    return dates == sorted(dates)


def parent_text(path: str) -> str | None:
    """Return the file at the parent commit (PR base or HEAD~1), or None when unavailable."""
    import os
    base = os.environ.get("SKILL_BASE_REF") or "HEAD~1"
    res = subprocess.run(
        ["git", "show", f"{base}:{path}"], cwd=ROOT, text=True, capture_output=True
    )
    return res.stdout if res.returncode == 0 else None


def shrink_override() -> bool:
    res = subprocess.run(
        ["git", "log", "-1", "--format=%B"], cwd=ROOT, text=True, capture_output=True
    )
    return SHRINK_OVERRIDE_TOKEN in (res.stdout or "")


def tracked_paths() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, text=True, capture_output=True
    )
    return [p for p in out.stdout.splitlines() if p]

def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for canonical, mirror in PAIRS.items():
        cp = ROOT / canonical
        mp = ROOT / mirror
        if not cp.is_file():
            errors.append(f"missing canonical skill: {canonical}")
            continue
        if not mp.is_file():
            errors.append(f"missing docs mirror: {mirror}")
            continue
        text = cp.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "name:" not in text or "description:" not in text:
            errors.append(f"invalid frontmatter: {canonical}")
        for section in REQUIRED[canonical]:
            if section not in text:
                errors.append(f"missing section in {canonical}: {section}")
        if len(text.encode()) < MIN_BODY_BYTES:
            errors.append(f"stub body in {canonical} ({len(text.encode())} bytes)")
        for pat in PLACEHOLDER_PATTERNS:
            if pat.search(text):
                errors.append(f"placeholder/clobbered body in {canonical}: matches {pat.pattern!r}")
        if all(x in text for x in REQUIRED[canonical]) and not section_order_ok(text, REQUIRED[canonical]):
            errors.append(f"required sections out of contract order in {canonical}")
        if not session_dates_monotonic(text):
            warnings.append(f"session log in {canonical} is not in date order (reordered history?)")
        import os as _os
        before, _ = reference_text(canonical, _os.environ.get("SKILL_BASE_REF") or "HEAD~1")
        if before is not None:
            d = content_delta(before, text)
            summary = (
                f"{canonical}: parent={d['parent_lines']} lost={d['lost']} "
                f"added={d['added']} lost_ratio={d['lost_ratio']:.2f} reordered={d['reordered']}"
            )
            print(summary)
            if d["parent_lines"] >= MIN_LINES_FOR_LOSS_CHECK and d["lost_ratio"] > MAX_LOST_RATIO:
                if shrink_override():
                    warnings.append(f"override {SHRINK_OVERRIDE_TOKEN}: {summary}")
                else:
                    errors.append(
                        f"{summary}; content lost vs parent. Append instead of rewriting, "
                        f"or put {SHRINK_OVERRIDE_TOKEN} in the commit message"
                    )
            elif d["lost_ratio"] > WARN_LOST_RATIO:
                warnings.append(f"{summary}; review removed lines")
        mirror_text = mp.read_text(encoding="utf-8")
        if f"{canonical}" not in mirror_text:
            errors.append(f"mirror does not identify canonical path: {mirror}")
        if re.search(r"(?i)(api[_-]?key|authorization:\s*bearer|private[_-]?key)\s*[:=]", text):
            errors.append(f"possible secret pattern in {canonical}")

    paths = tracked_paths()
    skill_files = [p for p in paths if p.endswith("/SKILL.md") or p == "SKILL.md"]
    archives = [p for p in paths if p.endswith(".skill") ]
    if not skill_files:
        errors.append("no tracked SKILL.md files discovered")
    print(f"tracked_skill_md={len(skill_files)} tracked_skill_archives={len(archives)}")
    for p in skill_files:
        if not (ROOT / p).is_file():
            errors.append(f"tracked skill path is not a regular file: {p}")
    for w in warnings:
        print(f"::warning::{w}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("adaptive-wait/evidence-led skill contract: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())