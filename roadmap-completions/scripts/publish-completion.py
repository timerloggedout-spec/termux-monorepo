#!/usr/bin/env python3
"""Publish a verified roadmap exercise badge and README index row."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

import yaml


START = "<!-- ROADMAP-COMPLETION-BADGES:START -->"
END = "<!-- ROADMAP-COMPLETION-BADGES:END -->"


def publish(root: Path, roadmap: str, exercise: str, score: int) -> dict[str, Any]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", roadmap):
        raise ValueError("Roadmap slug must use lowercase letters, digits, and hyphens.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", exercise):
        raise ValueError("Exercise slug must use lowercase letters, digits, and hyphens.")
    if score < 0 or score > 100:
        raise ValueError("Score must be between 0 and 100.")

    root = root.resolve()
    rules_path = root / "roadmap-completions/config/verification-rules.yaml"
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8")) or {}
    levels = rules.get("badge_levels", {})
    selected = next(
        (
            (name, value)
            for name, value in levels.items()
            if int(value.get("min_score", 0)) <= score <= int(value.get("max_score", 100))
        ),
        None,
    )
    if selected is None:
        raise ValueError(f"No badge level covers verification score {score}.")
    level, details = selected
    label = str(details.get("label", level.upper()))
    color = str(details.get("color", "#555555"))
    badge_path = Path("roadmap-completions/badges") / roadmap / f"{exercise}.svg"
    badge_file = root / badge_path
    badge_file.parent.mkdir(parents=True, exist_ok=True)

    left = html.escape(f"{roadmap} / {exercise}")
    right = html.escape(f"{label} · {score}")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="28" role="img" '
        f'aria-label="{left}: {right}">'
        '<rect width="360" height="28" rx="4" fill="#555"/>'
        '<rect x="205" width="155" height="28" rx="4" fill="' + html.escape(color, quote=True) + '"/>'
        f'<g fill="#fff" font-family="Verdana,Geneva,sans-serif" font-size="11">'
        f'<text x="102" y="18" text-anchor="middle">{left}</text>'
        f'<text x="282" y="18" text-anchor="middle">{right}</text>'
        '</g></svg>\n'
    )
    badge_file.write_text(svg, encoding="utf-8")

    readme = root / "README.md"
    readme_text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    relative_badge = badge_path.as_posix()
    row = f"| {roadmap} | {exercise} | {label} | {score} | ![{roadmap} {exercise}]({relative_badge}) |"
    if START in readme_text and END in readme_text:
        before, remainder = readme_text.split(START, 1)
        block, after = remainder.split(END, 1)
        row_pattern = re.compile(rf"(?m)^\| {re.escape(roadmap)} \| {re.escape(exercise)} \|.*$")
        if row_pattern.search(block):
            block = row_pattern.sub(row, block)
        else:
            block = block.rstrip() + "\n" + row + "\n"
        readme_text = before + START + block + END + after
    else:
        block = (
            "\n\n" + START + "\n"
            "## Roadmap Completion Badges\n\n"
            "| Roadmap | Exercise | Level | Score | Badge |\n"
            "|---|---|---|---:|---|\n"
            + row + "\n" + END + "\n"
        )
        readme_text = readme_text.rstrip() + block
    readme.write_text(readme_text, encoding="utf-8")

    return {
        "roadmap": roadmap,
        "exercise": exercise,
        "score": score,
        "level": level,
        "badge": relative_badge,
        "readme": "README.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roadmap", required=True)
    parser.add_argument("--exercise", required=True)
    parser.add_argument("--score", type=int, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(publish(args.root, args.roadmap, args.exercise, args.score), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
