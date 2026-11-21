#!/usr/bin/env python3
"""Build a deterministic, content-addressed PolyGlot federation feed."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs" / "integrations" / "polyglot" / "examples"

def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def committed_bytes(revision: str, path: Path) -> bytes:
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"cannot read {relative} at {revision}: {detail}")
    return result.stdout

def build_records(revision: str) -> list[dict[str, str]]:
    paths = {
        "capability": BASE / "capability.json",
        "technology_targets": BASE / "technology-targets.json",
        "mapping": BASE / "mapping-quic-streams.json",
        "dimensions": BASE / "matrice-dimensions.json",
    }
    committed = {key: committed_bytes(revision, path) for key, path in paths.items()}
    documents = {key: json.loads(content) for key, content in committed.items()}
    capability = documents["capability"]
    targets = documents["technology_targets"]
    mapping = documents["mapping"]
    sources = [
        ("capability", capability["capability_id"], paths["capability"], committed["capability"]),
        *[
            ("technology_target", item["target_id"], paths["technology_targets"], committed["technology_targets"])
            for item in targets["targets"]
        ],
        ("mapping", mapping["mapping_id"], paths["mapping"], committed["mapping"]),
        ("matrice_dimensions", "matrice.shared-dimensions", paths["dimensions"], committed["dimensions"]),
    ]
    records = []
    for record_type, record_id, path, content in sources:
        records.append({
            "record_type": record_type,
            "record_id": record_id,
            "path": path.relative_to(ROOT).as_posix(),
            "content_digest": "sha256:" + sha256(content),
        })
    return records

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="owner/name")
    parser.add_argument("--revision", required=True, help="immutable source commit SHA")
    parser.add_argument("--generated-at", required=True, help="UTC ISO-8601 timestamp")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"{args.revision}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if resolved.returncode:
        parser.error(f"--revision must resolve to a commit: {args.revision}")
    revision = resolved.stdout.strip()
    if len(revision) != 40:
        parser.error("--revision must resolve to a full commit SHA")
    records = build_records(revision)
    envelope = {
        "schema_version": "1.0.0",
        "feed_id": f"{args.repository}@{revision}",
        "producer": "polyglot-linguist-federation",
        "repository": args.repository,
        "revision": revision,
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
