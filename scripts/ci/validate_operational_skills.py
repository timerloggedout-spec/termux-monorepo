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

def tracked_paths() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, text=True, capture_output=True
    )
    return [p for p in out.stdout.splitlines() if p]

def main() -> int:
    errors: list[str] = []
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
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("adaptive-wait/evidence-led skill contract: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())