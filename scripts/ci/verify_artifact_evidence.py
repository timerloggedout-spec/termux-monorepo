#!/usr/bin/env python3
"""Verify a bounded artifact-evidence manifest after an explicit download step."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from scripts.ci.create_artifact_evidence import digest_file, safe_relative
except ModuleNotFoundError:  # Direct execution from scripts/ci on a GitHub runner.
    from create_artifact_evidence import digest_file, safe_relative


SHA256 = re.compile(r"^[0-9a-f]{64}$")


def verify_manifest(root: Path, manifest_path: Path) -> int:
    root = root.resolve()
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read manifest: {exc}") from exc
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ValueError("manifest schema_version must be 1")
    files = document.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("manifest files must be a non-empty list")

    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("manifest entry must be an object")
        name = safe_relative(entry.get("path", ""))
        if name in seen:
            raise ValueError(f"duplicate manifest path: {name!r}")
        seen.add(name)
        expected_digest = entry.get("sha256")
        expected_size = entry.get("bytes")
        if not isinstance(expected_digest, str) or not SHA256.fullmatch(expected_digest):
            raise ValueError(f"invalid SHA-256 for {name!r}")
        if not isinstance(expected_size, int) or expected_size < 0:
            raise ValueError(f"invalid size for {name!r}")
        target = (root / name).resolve()
        if root not in target.parents or not target.is_file():
            raise ValueError(f"manifest file is missing or outside root: {name!r}")
        if target.stat().st_size != expected_size:
            raise ValueError(f"size mismatch for {name!r}")
        if digest_file(target) != expected_digest:
            raise ValueError(f"digest mismatch for {name!r}")
    return len(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    try:
        count = verify_manifest(args.root, args.manifest)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"verified artifact evidence: {count} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
