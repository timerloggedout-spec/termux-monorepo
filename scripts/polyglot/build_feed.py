#!/usr/bin/env python3
"""Build a deterministic, content-addressed PolyGlot federation feed."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs" / "integrations" / "polyglot" / "examples"

def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def build_records() -> list[dict[str, str]]:
    capability_path = BASE / "capability.json"
    capability = json.loads(capability_path.read_text(encoding="utf-8"))
    targets_path = BASE / "technology-targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    mapping_path = BASE / "mapping-quic-streams.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    dimensions_path = BASE / "matrice-dimensions.json"
    dimensions = json.loads(dimensions_path.read_text(encoding="utf-8"))
    sources = [
        ("capability", capability["capability_id"], capability_path),
        *[("technology_target", item["target_id"], targets_path) for item in targets["targets"]],
        ("mapping", mapping["mapping_id"], mapping_path),
        ("matrice_dimensions", "matrice.shared-dimensions", dimensions_path),
    ]
    records = []
    for record_type, record_id, path in sources:
        records.append({
            "record_type": record_type,
            "record_id": record_id,
            "path": path.relative_to(ROOT).as_posix(),
            "content_digest": "sha256:" + sha256(path.read_bytes()),
        })
    return records

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="owner/name")
    parser.add_argument("--revision", required=True, help="immutable source commit SHA")
    parser.add_argument("--generated-at", required=True, help="UTC ISO-8601 timestamp")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = build_records()
    envelope = {
        "schema_version": "1.0.0",
        "feed_id": f"{args.repository}@{args.revision}",
        "producer": "polyglot-linguist-federation",
        "repository": args.repository,
        "revision": args.revision,
        "generated_at": args.generated_at,
        "records": records,
        "artifact_digest": "sha256:" + sha256(canonical_bytes(records)),
        "signature": None,
        "schema_refs": [
            "docs/integrations/polyglot/schemas/feed-envelope.schema.json",
            "docs/integrations/polyglot/schemas/capability.schema.json",
            "docs/integrations/polyglot/schemas/technology-target.schema.json",
            "docs/integrations/polyglot/schemas/mapping.schema.json",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(envelope, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: wrote {args.output} ({len(records)} records, {envelope['artifact_digest']})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
