#!/usr/bin/env python3
"""Read-only verifier for immutable skill source and derivative lineage."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if path != ROOT and ROOT not in path.parents:
        raise ValueError(f"path escapes repository: {value}")
    if not path.is_file():
        raise FileNotFoundError(value)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    data = json.loads(repo_path(args.manifest).read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError("unsupported manifest schema_version")
    pairs = data.get("pairs")
    if not isinstance(pairs, list):
        raise ValueError("manifest pairs must be a list")
    seen = set()
    errors = []
    for index, pair in enumerate(pairs):
        source, candidate = pair.get("source", {}), pair.get("candidate", {})
        source_path, candidate_path = source.get("path", ""), candidate.get("path", "")
        if not source_path or not candidate_path or source_path == candidate_path:
            errors.append(f"pair[{index}]: source and candidate require distinct paths")
            continue
        if source_path in seen or candidate_path in seen:
            errors.append(f"pair[{index}]: duplicate path")
            continue
        seen.update((source_path, candidate_path))
        try:
            actual_source = digest(repo_path(source_path))
            actual_candidate = digest(repo_path(candidate_path))
        except (OSError, ValueError) as exc:
            errors.append(f"pair[{index}]: {exc}")
            continue
        if actual_source != source.get("sha256"):
            errors.append(f"pair[{index}]: original source SHA-256 mismatch")
        if actual_source != candidate.get("parent_sha256"):
            errors.append(f"pair[{index}]: candidate parent SHA-256 mismatch")
        if actual_candidate != candidate.get("sha256"):
            errors.append(f"pair[{index}]: candidate SHA-256 mismatch")
        if not candidate.get("transformation_id"):
            errors.append(f"pair[{index}]: transformation_id required")
    print(json.dumps({"manifest": args.manifest, "pairs_checked": len(pairs),
                      "errors": errors, "status": "failed" if errors else "passed"}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
