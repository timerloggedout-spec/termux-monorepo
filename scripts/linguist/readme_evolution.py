#!/usr/bin/env python3
"""Read-only comparative README evolution and seeded change-budget planner.

The planner measures/selects review budgets only. It never rewrites files,
changes mappings, or applies random substitutions.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping

DEFAULT_SCOPES = (
    "README.md",
    ".gitattributes",
    "CLAUDE.hum.md",
    "docs/linguist",
    "docs/ops/LINGUIST-PANEL-FEED.md",
    "docs/proposals/active/notation-sets",
    "scripts/linguist",
    "workspace/compression_sandbox/cedrlang",
    "harmony_hub/config/grimoire",
    "apps/tribute-dashboard/linguist.html",
)
TEXT_SUFFIXES = {
    ".md", ".py", ".json", ".yaml", ".yml", ".toml", ".txt",
    ".rst", ".html", ".svg", ".mmd", ".ini",
}
EXCLUDED_SEGMENTS = {
    ".git", ".deepcli", "tmp", "node_modules", "__pycache__",
    "artifacts", "generated",
}
WORD_RE = re.compile(r"\w+", re.UNICODE)


def _lcs_length(left: list[str], right: list[str]) -> int:
    """Return exact LCS length using O(len(right)) memory."""
    dp = [0] * (len(right) + 1)
    for left_line in reversed(left):
        previous = 0
        for index in range(len(right) - 1, -1, -1):
            old = dp[index]
            if left_line == right[index]:
                dp[index] = previous + 1
            else:
                dp[index] = max(dp[index], dp[index + 1])
            previous = old
    return dp[0]


def compare_text(base: str, candidate: str) -> dict:
    """Return a symmetric, line-based LCS delta; this is not a quality score."""
    left = base.splitlines()
    right = candidate.splitlines()
    unchanged = _lcs_length(left, right)
    changed_left = len(left) - unchanged
    changed_right = len(right) - unchanged
    denominator = max(1, len(left) + len(right))
    return {
        "base_lines": len(left),
        "candidate_lines": len(right),
        "unchanged_lines": unchanged,
        "changed_base_lines": changed_left,
        "changed_candidate_lines": changed_right,
        "changed_line_ratio": (changed_left + changed_right) / denominator,
        "changed_line_percent": 100.0 * (changed_left + changed_right) / denominator,
        "base_utf8_bytes": len(base.encode("utf-8")),
        "candidate_utf8_bytes": len(candidate.encode("utf-8")),
        "quality_score": None,
    }


def plan_file_budgets(
    token_counts: Mapping[str, int],
    *,
    seed: str,
    rate: float = 0.0007,
    jitter: float = 0.10,
    max_rate: float = 0.07,
) -> list[dict]:
    """Create deterministic per-file review budgets without mutating content."""
    if not 0 < rate <= max_rate <= 1:
        raise ValueError("rates must satisfy 0 < rate <= max_rate <= 1")
    if not 0 <= jitter <= 1:
        raise ValueError("jitter must be between 0 and 1")
    rng = random.Random(str(seed))
    rows = []
    for path in sorted(token_counts):
        count = max(0, int(token_counts[path]))
        factor = 1.0 + rng.uniform(-jitter, jitter)
        selected_rate = min(max_rate, max(0.0, rate * factor))
        rows.append({
            "path": path,
            "directory": str(Path(path).parent),
            "eligible_tokens": count,
            "selected_rate": selected_rate,
            "budget_tokens": round(count * selected_rate),
        })
    return rows


def _in_scope(path: str, scopes: Iterable[str]) -> bool:
    return any(path == scope or path.startswith(scope.rstrip("/") + "/")
               for scope in scopes)


def collect_tracked_token_counts(root: Path, scopes: Iterable[str]) -> dict[str, int]:
    """Count eligible Unicode word tokens in tracked text files only."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    paths = [p.decode("utf-8") for p in result.stdout.split(b"\0") if p]
    counts: dict[str, int] = {}
    for relative in paths:
        path = Path(relative)
        if not _in_scope(relative, scopes):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".gitattributes":
            continue
        if any(part in EXCLUDED_SEGMENTS for part in path.parts):
            continue
        candidate = root / path
        if candidate.is_symlink() or not candidate.is_file():
            continue
        try:
            content = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        counts[relative] = len(WORD_RE.findall(content))
    return counts


def _git_show(root: Path, ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="command", required=True)

    compare = sub.add_parser("compare", help="compare two README refs")
    compare.add_argument("--base-ref", default="master")
    compare.add_argument("--candidate-ref", default="HEAD")
    compare.add_argument("--path", default="README.md")

    plan = sub.add_parser("plan", help="emit a seeded report-only budget")
    plan.add_argument("--seed", default=None)
    plan.add_argument("--rate", type=float, default=0.0007)
    plan.add_argument("--jitter", type=float, default=0.10)
    plan.add_argument("--max-rate", type=float, default=0.07)
    plan.add_argument("--scope", action="append", default=None)

    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "compare":
        base = _git_show(root, args.base_ref, args.path)
        candidate = _git_show(root, args.candidate_ref, args.path)
        output = {
            "schema_version": "linguist.readme-comparison/v1",
            "path": args.path,
            "base_ref": args.base_ref,
            "candidate_ref": args.candidate_ref,
            "metrics": compare_text(base, candidate),
        }
    else:
        seed = args.seed
        if seed is None:
            seed = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True,
                capture_output=True, text=True,
            ).stdout.strip()
        scopes = tuple(args.scope or DEFAULT_SCOPES)
        counts = collect_tracked_token_counts(root, scopes)
        rows = plan_file_budgets(
            counts, seed=seed, rate=args.rate, jitter=args.jitter,
            max_rate=args.max_rate,
        )
        by_directory: dict[str, int] = defaultdict(int)
        for row in rows:
            by_directory[row["directory"]] += row["budget_tokens"]
        output = {
            "schema_version": "linguist.readme-budget-plan/v1",
            "seed": seed,
            "rate": args.rate,
            "relative_jitter": args.jitter,
            "max_rate": args.max_rate,
            "mode": "report_only",
            "mutated_files": [],
            "files": rows,
            "directory_budgets": dict(sorted(by_directory.items())),
        }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
