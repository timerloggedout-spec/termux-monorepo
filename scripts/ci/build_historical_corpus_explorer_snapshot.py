#!/usr/bin/env python3
"""Build the deterministic static projection consumed by Historical Corpus Explorer."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from archwiz.context_relationships.explorer_projection import project_coverage

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "workspace/llm_map/context_relationships/manifest.json"
DEFAULT_SUMMARY = ROOT / "workspace/llm_map/context_relationships/build-summary.json"
DEFAULT_OUTPUT = ROOT / "apps/historical-corpus-explorer/data/snapshot.json"


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON input {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON input must be an object: {path}")
    return value


def git_value(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"git provenance lookup failed for {' '.join(args)}: {exc}") from exc


def build_projection(
    manifest: dict[str, Any],
    summary: dict[str, Any],
    *,
    source_ref: str,
    source_sha: str,
    manifest_blob_sha: str,
) -> dict[str, Any]:
    projection = project_coverage(
        manifest,
        summary,
        source_ref=source_ref,
        source_sha=source_sha,
        manifest_blob_sha=manifest_blob_sha,
    )
    projection["snapshot_id"] = "hce-" + source_sha[:12] + "-" + manifest_blob_sha[:12]
    projection["schema_version"] = "1.0"
    return projection


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--build-summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-ref", default=os.environ.get("GITHUB_REF_NAME", "unknown"))
    parser.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--manifest-blob-sha", default="")
    parser.add_argument("--check", action="store_true", help="validate inputs and print projection without writing")
    args = parser.parse_args()

    try:
        manifest = read_object(args.manifest)
        summary = read_object(args.build_summary)
        source_sha = args.source_sha or git_value("rev-parse", "HEAD")
        manifest_blob_sha = args.manifest_blob_sha
        if not manifest_blob_sha:
            try:
                relative_manifest = args.manifest.resolve().relative_to(ROOT).as_posix()
            except ValueError as exc:
                raise ValueError("manifest must be inside the repository unless --manifest-blob-sha is supplied") from exc
            manifest_blob_sha = git_value("rev-parse", f"{source_sha}:{relative_manifest}")
        projection = build_projection(
            manifest,
            summary,
            source_ref=args.source_ref,
            source_sha=source_sha,
            manifest_blob_sha=manifest_blob_sha,
        )
        encoded = json.dumps(projection, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.check:
            print(json.dumps({
                "status": "PASS" if projection["reconciliation"]["error_count"] == 0 else "RECONCILIATION_REQUIRED",
                "snapshot_id": projection["snapshot_id"],
                "finding_count": len(projection["reconciliation"]["findings"]),
                "output_written": False,
            }, sort_keys=True))
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
        print(json.dumps({
            "status": "PASS" if projection["reconciliation"]["error_count"] == 0 else "RECONCILIATION_REQUIRED",
            "snapshot_id": projection["snapshot_id"],
            "output": str(args.output.relative_to(ROOT)) if args.output.is_relative_to(ROOT) else str(args.output),
            "finding_count": len(projection["reconciliation"]["findings"]),
        }, sort_keys=True))
        return 0
    except (ValueError, OSError) as exc:
        print(f"historical-corpus-explorer snapshot build failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
