#!/usr/bin/env python3
"""Require a durable ICM impact receipt for every pull-request delta.

The receipt is intentionally metadata-only: it names changed paths, the ICM cards
that were consulted/updated, related repository records, and the disposition.
No network access or third-party packages are used.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RECEIPT_PREFIX = "docs/icm/changes/"
RECEIPT_SUFFIX = ".json"
REQUIRED_KEYS = {
    "schema_version",
    "change_id",
    "disposition",
    "changed_paths",
    "primary_cards",
    "related_updates",
    "rationale",
}


def changed_paths(base: str, head: str = "HEAD") -> list[str]:
    """Return changed repository paths for the three-dot merge-base diff."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRTD", "-z", f"{base}...{head}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return sorted({item.decode("utf-8") for item in result.stdout.split(b"\0") if item})


def _safe_repo_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts


def _path_list(receipt: dict[str, Any], key: str, errors: list[str]) -> list[str]:
    value = receipt.get(key)
    if not isinstance(value, list) or any(not _safe_repo_path(item) for item in value):
        errors.append(f"{key} must be an array of safe repository-relative paths")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{key} contains duplicate paths")
    return value


def validate_receipt(root: Path, paths: list[str]) -> list[str]:
    """Validate the single receipt against the exact PR delta; return failures."""
    errors: list[str] = []
    changed = sorted(set(paths))
    receipts = [
        path for path in changed
        if path.startswith(RECEIPT_PREFIX) and path.endswith(RECEIPT_SUFFIX)
    ]
    if len(receipts) != 1:
        errors.append(
            f"expected exactly one changed {RECEIPT_PREFIX}*.json receipt; found {len(receipts)}"
        )
        return errors

    receipt_path = receipts[0]
    if not _safe_repo_path(receipt_path):
        return ["receipt path is not repository-relative"]

    try:
        receipt = json.loads((root / receipt_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot read valid JSON receipt {receipt_path}: {exc}"]
    if not isinstance(receipt, dict):
        return ["receipt root must be a JSON object"]

    missing = sorted(REQUIRED_KEYS - set(receipt))
    extra = sorted(set(receipt) - REQUIRED_KEYS)
    if missing:
        errors.append("missing required receipt keys: " + ", ".join(missing))
    if extra:
        errors.append("unsupported receipt keys: " + ", ".join(extra))
    if receipt.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    change_id = receipt.get("change_id")
    if not isinstance(change_id, str) or not change_id.strip():
        errors.append("change_id must be a non-empty string")
    elif receipt_path.rsplit("/", 1)[-1][:-5] != change_id.lower().replace("_", "-"):
        errors.append("receipt filename must match change_id (lowercase, underscores as hyphens)")

    disposition = receipt.get("disposition")
    if disposition not in ("updated", "no-map-change"):
        errors.append("disposition must be 'updated' or 'no-map-change'")

    listed_changed = _path_list(receipt, "changed_paths", errors)
    if sorted(listed_changed) != changed:
        missing_paths = sorted(set(changed) - set(listed_changed))
        stale_paths = sorted(set(listed_changed) - set(changed))
        if missing_paths:
            errors.append("changed_paths omits: " + ", ".join(missing_paths))
        if stale_paths:
            errors.append("changed_paths includes paths outside this PR: " + ", ".join(stale_paths))

    primary_cards = _path_list(receipt, "primary_cards", errors)
    related_updates = _path_list(receipt, "related_updates", errors)
    for card in primary_cards:
        if not card.startswith("docs/icm/") or not card.endswith(".md"):
            errors.append(f"primary card must be a Markdown file under docs/icm/: {card}")
        elif not (root / card).is_file():
            errors.append(f"primary card does not exist: {card}")

    for path in related_updates:
        if path not in changed:
            errors.append(f"related_updates path is not changed in this PR: {path}")
        elif not (root / path).is_file():
            errors.append(f"related_updates path does not exist: {path}")

    if disposition == "updated" and not set(primary_cards).intersection(changed):
        errors.append("disposition 'updated' requires at least one primary ICM card to change")
    if disposition == "no-map-change" and not str(receipt.get("rationale", "")).strip():
        errors.append("disposition 'no-map-change' requires a rationale")
    if not isinstance(receipt.get("rationale"), str) or not receipt.get("rationale", "").strip():
        errors.append("rationale must be a non-empty string")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="base ref for the pull-request delta")
    parser.add_argument("--head", default="HEAD", help="head ref (default: HEAD)")
    args = parser.parse_args()

    try:
        paths = changed_paths(args.base, args.head)
    except subprocess.CalledProcessError as exc:
        print(f"ICM impact gate: unable to diff {args.base}...{args.head}: {exc}", file=sys.stderr)
        return 2

    print(f"ICM impact gate — {len(paths)} changed path(s)")
    failures = validate_receipt(REPO_ROOT, paths)
    for failure in failures:
        print(f"FAIL  {failure}")
    if failures:
        print(f"ICM impact gate failed ({len(failures)} issue(s))")
        return 1

    receipt_path = next(
        path for path in paths
        if path.startswith(RECEIPT_PREFIX) and path.endswith(RECEIPT_SUFFIX)
    )
    receipt = json.loads((REPO_ROOT / receipt_path).read_text(encoding="utf-8"))
    print(f"PASS  {receipt['change_id']} · {receipt['disposition']} · receipt {receipt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
