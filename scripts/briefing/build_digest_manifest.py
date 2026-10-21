#!/usr/bin/env python3
"""Validate the standing daily-digest source registry and emit a deterministic manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_KEYS = {"id", "name", "role", "url"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.registry.read_text(encoding="utf-8"))
    resources = data.get("resource_families", [])
    if not resources:
        raise SystemExit("registry has no resource_families")

    ids = set()
    for item in resources:
        missing = REQUIRED_KEYS - item.keys()
        if missing:
            raise SystemExit(f"resource {item.get('id', '<unknown>')} missing: {sorted(missing)}")
        if item["id"] in ids:
            raise SystemExit(f"duplicate resource id: {item['id']}")
        ids.add(item["id"])

    manifest = {
        "schema_version": data["schema_version"],
        "resource_count": len(resources),
        "resource_ids": sorted(ids),
        "source_classes": data.get("source_classes", []),
        "selection_policy": data.get("selection_policy", {}),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
