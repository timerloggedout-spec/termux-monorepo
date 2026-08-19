#!/usr/bin/env python3
"""Create a bounded SHA-256 manifest for an evidence artifact directory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Iterable


MAX_FILE_BYTES = 1_000_000


def safe_relative(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if not value or path.is_absolute() or ".." in path.parts or path.name != value:
        raise ValueError(f"artifact entry must be a single safe filename: {value!r}")
    if value.startswith("."):
        raise ValueError(f"hidden artifact entry is not allowed: {value!r}")
    return path.as_posix()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path, entries: Iterable[str]) -> dict[str, object]:
    root = root.resolve()
    files: list[dict[str, object]] = []
    seen: set[str] = set()
    for entry in entries:
        name = safe_relative(entry)
        if name in seen:
            raise ValueError(f"duplicate artifact entry: {name!r}")
        seen.add(name)
        target = (root / name).resolve()
        if root not in target.parents or not target.is_file():
            raise ValueError(f"artifact entry does not resolve to a regular root file: {name!r}")
        size = target.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError(f"artifact entry exceeds {MAX_FILE_BYTES} bytes: {name!r}")
        files.append({"path": name, "sha256": digest_file(target), "bytes": size})
    if not files:
        raise ValueError("at least one artifact entry is required")
    return {"schema_version": 1, "files": files}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("entries", nargs="+")
    args = parser.parse_args()
    try:
        manifest = build_manifest(args.root, args.entries)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
