#!/usr/bin/env python3
"""Classify repository paths for the B1 GitHub Actions workflow-surface policy.

The classifier accepts path strings as data only. It emits stable boolean category
flags and never invokes a shell, expands a path, or returns a filename for workflow
interpolation. The GitHub workflow uses dorny/paths-filter only for its boolean
outputs; this helper supplies deterministic fixture coverage for the same policy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from typing import Iterable


CATEGORIES = ("automation", "source", "tests", "docs")


def normalize_path(value: str) -> str:
    """Return a safe repository-relative POSIX path or raise ValueError."""
    if not isinstance(value, str) or not value:
        raise ValueError("path must be a non-empty string")
    candidate = value.replace("\\", "/")
    path = PurePosixPath(candidate)
    if path.is_absolute() or ".." in path.parts or candidate.startswith("./"):
        raise ValueError(f"path must be repository-relative: {value!r}")
    return path.as_posix()


def classify_path(value: str) -> dict[str, bool]:
    """Classify one repository path into stable, non-exclusive surface flags."""
    path = normalize_path(value)
    name = PurePosixPath(path).name

    automation = (
        path.startswith(".github/workflows/")
        or path.startswith(".github/actions/")
        or path == "scripts/ci/workflow_surface_policy.py"
    )
    tests = path.startswith("tests/") or path == "tests/test_workflow_surface_policy.py"
    docs = (
        path.startswith("docs/")
        or path.startswith(".github/ISSUE_TEMPLATE/")
        or name.lower().startswith("readme")
        or path in {"CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md"}
    )
    source = (
        path.endswith((".py", ".sh", ".js", ".mjs", ".c", ".h", ".cpp", ".hpp"))
        and not tests
        and not path.startswith("scripts/ci/")
    )

    return {
        "automation": automation,
        "source": source,
        "tests": tests,
        "docs": docs,
    }


def classify_paths(values: Iterable[str]) -> dict[str, bool]:
    """OR-reduce path classifications for a pull-request-like path set."""
    result = {category: False for category in CATEGORIES}
    for value in values:
        categories = classify_path(value)
        for category in CATEGORIES:
            result[category] = result[category] or categories[category]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="repository-relative paths to classify")
    args = parser.parse_args()
    try:
        print(json.dumps(classify_paths(args.paths), sort_keys=True))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
