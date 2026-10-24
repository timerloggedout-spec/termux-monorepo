#!/usr/bin/env python3
"""Create a checksum-backed provenance inventory for sanitized Hex artifacts.

This registers the GitHub Actions artifact bundle; it does not claim that the
bundle is a native Hex export or that it was imported into a Hex workspace.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_FILES = ("evidence.ndjson", "evidence.csv", "receipt.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_inventory(
    artifact_dir: Path,
    *,
    run_id: str,
    run_attempt: str,
    source_sha: str,
    source_ref: str,
    source_path: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if not run_id or not run_attempt or not source_sha or not source_ref or not source_path:
        raise ValueError("run identity and source provenance fields must be non-empty")
    if len(source_sha) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in source_sha):
        raise ValueError("source_sha must be a full 40-character Git commit SHA")

    receipt_path = artifact_dir / "receipt.json"
    if not receipt_path.is_file():
        raise ValueError("receipt.json is missing from the artifact bundle")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise ValueError("receipt.json must contain an object")
    if receipt.get("validation_status") != "VALIDATED":
        raise ValueError("receipt is not validated")
    if receipt.get("raw_content_exported") is not False:
        raise ValueError("receipt does not affirm the raw-content export boundary")
    if receipt.get("source_sha") != source_sha or receipt.get("source_ref") != source_ref:
        raise ValueError("receipt source provenance does not match the requested inventory")
    if receipt.get("snapshot_id") != f"{run_id}-{run_attempt}":
        raise ValueError("receipt snapshot_id does not match the run attempt")

    files = []
    for name in EXPECTED_FILES:
        path = artifact_dir / name
        if not path.is_file():
            raise ValueError(f"required artifact file is missing: {name}")
        files.append({
            "path": name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    return {
        "schema_version": "hex-moneyball-artifact-provenance/v1",
        "artifact_kind": "sanitized_github_actions_artifact",
        "native_hex_export": False,
        "hex_import_confirmed": False,
        "contract_version": receipt.get("contract_version"),
        "snapshot_id": receipt["snapshot_id"],
        "source": {
            "repository": "timerloggedout-spec/termux-monorepo",
            "sha": source_sha,
            "ref": source_ref,
            "path": source_path,
        },
        "producer": {
            "platform": "GitHub Actions",
            "run_id": str(run_id),
            "run_attempt": str(run_attempt),
            "run_uid": f"gha:timerloggedout-spec/termux-monorepo:{run_id}:{run_attempt}",
        },
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "contents": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_dir", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--source-path", required=True)
    parser.add_argument("--generated-at", default=None, help="Optional fixed UTC timestamp for reproducible tests")
    args = parser.parse_args()
    inventory = create_inventory(
        args.artifact_dir,
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        source_sha=args.source_sha,
        source_ref=args.source_ref,
        source_path=args.source_path,
        generated_at=args.generated_at,
    )
    output = args.artifact_dir / "artifact-provenance.json"
    output.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"path": output.name, "schema_version": inventory["schema_version"], "files": len(inventory["contents"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
