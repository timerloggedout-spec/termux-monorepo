"""Populate paired local catalogue snapshots from one incumbent v5 input.

The runner reuses a supplied snapshot and keeps execution offline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from scripts.provider_model_catalog_vultr_inspired import normalize_incumbent


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix=".provider-catalog-", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as output_file:
            output_file.write(content)
            output_file.flush()
            os.fsync(output_file.fileno())
        os.replace(temporary_path, path)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)


def populate(input_path: Path, output_dir: Path) -> dict[str, Any]:
    """Write Incumbent and VultrInspired snapshots from identical source rows."""
    source_bytes = input_path.read_bytes()
    incumbent = json.loads(source_bytes.decode("utf-8"))
    if not isinstance(incumbent, dict) or incumbent.get("schema") != "provider-model-catalog/v5":
        raise ValueError("unsupported_incumbent_schema")

    inspired = normalize_incumbent(incumbent)
    incumbent_path = output_dir / "incumbent-v5.json"
    inspired_path = output_dir / "vultr-inspired-v1.json"

    _atomic_write(incumbent_path, source_bytes)
    inspired_bytes = (json.dumps(inspired, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _atomic_write(inspired_path, inspired_bytes)

    manifest = {
        "schema": "provider-catalog-competition-manifest/v1",
        "source_catalogue": "Incumbent",
        "source_schema": "provider-model-catalog/v5",
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "variants": [
            {
                "catalogue": "Incumbent",
                "version": "5.0.0",
                "path": incumbent_path.name,
                "sha256": hashlib.sha256(source_bytes).hexdigest(),
                "model_count": len(incumbent.get("models", [])),
            },
            {
                "catalogue": "VultrInspired",
                "version": "1.0.0",
                "path": inspired_path.name,
                "sha256": hashlib.sha256(inspired_bytes).hexdigest(),
                "model_count": len(inspired["models"]),
                "issue_count": len(inspired["issues"]),
            },
        ],
        "execution": {
            "mode": "offline_snapshot_projection",
            "network_requests": 0,
            "credentials_required": False,
            "inference_calls": 0,
        },
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _atomic_write(output_dir / "manifest.json", manifest_bytes)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing incumbent v5 JSON snapshot")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for paired catalogue files")
    args = parser.parse_args(argv)
    manifest = populate(args.input, args.output_dir)
    print(
        "catalogues=2 "
        f"incumbent_models={manifest['variants'][0]['model_count']} "
        f"vultr_inspired_models={manifest['variants'][1]['model_count']} "
        f"issues={manifest['variants'][1]['issue_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
