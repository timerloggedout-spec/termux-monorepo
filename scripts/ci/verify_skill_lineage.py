#!/usr/bin/env python3
"""Read-only verifier for immutable skill source pins and derivative lineage."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHA256 = re.compile(r"^[0-9a-f]{64}$")
CHECKSUM_STATES = {"verified", "partial", "unverified"}

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def repo_path(value: str, root: Path = ROOT) -> Path:
    path = (root / value).resolve()
    resolved_root = root.resolve()
    if path != resolved_root and resolved_root not in path.parents:
        raise ValueError(f"path escapes repository: {value}")
    if not path.is_file():
        raise FileNotFoundError(value)
    return path

def verify_manifest(data: dict, root: Path = ROOT, baseline_data: dict | None = None) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0":
        return ["unsupported manifest schema_version"]
    sources = data.get("sources", [])
    candidates = data.get("candidates", [])
    if not isinstance(sources, list) or not isinstance(candidates, list):
        return ["manifest sources and candidates must be lists"]
    source_by_id: dict[str, dict] = {}
    source_paths: dict[Path, str] = {}
    candidate_ids: set[str] = set()
    candidate_paths: set[Path] = set()
    for index, source in enumerate(sources):
        source_id, value = source.get("id", ""), source.get("path", "")
        if not source_id or source_id in source_by_id:
            errors.append(f"source[{index}]: missing or duplicate source id")
            continue
        if not value or not SHA256.fullmatch(source.get("sha256", "")):
            errors.append(f"source[{index}]: path and SHA-256 required")
            continue
        if source.get("checksum_status") not in CHECKSUM_STATES:
            errors.append(f"source[{index}]: checksum_status must be verified, partial, or unverified")
        if not source.get("provenance"):
            errors.append(f"source[{index}]: provenance required")
        try:
            path = repo_path(value, root)
            actual = digest(path)
        except (OSError, ValueError) as exc:
            errors.append(f"source[{index}]: {exc}")
            continue
        if path in source_paths:
            errors.append(f"source[{index}]: duplicate canonical source path")
        source_paths[path] = source_id
        if actual != source["sha256"]:
            errors.append(f"source[{index}]: original source SHA-256 mismatch")
        source_by_id[source_id] = source
    if baseline_data is not None:
        baseline_sources = baseline_data.get("sources", [])
        if not isinstance(baseline_sources, list):
            errors.append("baseline manifest sources must be a list")
        else:
            for pinned in baseline_sources:
                source_id = pinned.get("id")
                current = source_by_id.get(source_id)
                if current is None:
                    errors.append(f"baseline source pin removed: {source_id}")
                elif current.get("path") != pinned.get("path") or current.get("sha256") != pinned.get("sha256"):
                    errors.append(f"baseline source pin changed: {source_id}")
    for index, candidate in enumerate(candidates):
        candidate_id = candidate.get("id", "")
        source_id = candidate.get("source_id", "")
        if not candidate_id or candidate_id in candidate_ids:
            errors.append(f"candidate[{index}]: missing or duplicate candidate id")
            continue
        candidate_ids.add(candidate_id)
        source = source_by_id.get(source_id)
        if source is None:
            errors.append(f"candidate[{index}]: unknown source_id {source_id}")
            continue
        value = candidate.get("path", "")
        if not value or not SHA256.fullmatch(candidate.get("sha256", "")):
            errors.append(f"candidate[{index}]: path and SHA-256 required")
            continue
        if candidate.get("parent_sha256") != source.get("sha256"):
            errors.append(f"candidate[{index}]: parent SHA-256 does not match source pin")
        if not candidate.get("transformation_id"):
            errors.append(f"candidate[{index}]: transformation_id required")
        try:
            path = repo_path(value, root)
            actual = digest(path)
        except (OSError, ValueError) as exc:
            errors.append(f"candidate[{index}]: {exc}")
            continue
        if path in source_paths:
            errors.append(f"candidate[{index}]: candidate aliases an original source path")
        if path in candidate_paths:
            errors.append(f"candidate[{index}]: duplicate canonical candidate path")
        candidate_paths.add(path)
        if actual != candidate["sha256"]:
            errors.append(f"candidate[{index}]: candidate SHA-256 mismatch")
    return errors

def load_baseline(ref: str | None, manifest_path: str) -> dict | None:
    if not ref:
        return None
    result = subprocess.run(["git", "show", f"{ref}:{manifest_path}"], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        return None
    return json.loads(result.stdout)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--baseline-ref")
    args = parser.parse_args()
    manifest_path = repo_path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    baseline = load_baseline(args.baseline_ref, args.manifest)
    errors = verify_manifest(data, ROOT, baseline)
    print(json.dumps({
        "manifest": args.manifest,
        "sources_checked": len(data.get("sources", [])),
        "candidates_checked": len(data.get("candidates", [])),
        "baseline_ref": args.baseline_ref,
        "errors": errors,
        "status": "failed" if errors else "passed",
    }, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
