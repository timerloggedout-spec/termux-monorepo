#!/usr/bin/env python3
"""Generate deterministic cross-custom mapping retrieval benchmarks.

The dataset shape follows the useful LIMIT pattern: corpus + natural-language
queries + relevance judgments (qrels), with controlled hard negatives.
Mapping assertions retain their own grade, domain, kernel, and provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "linguist-mapping-benchmark/v1"
GRADES = {"exact", "approximate", "analogue", "lossy"}


def _required_text(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError(f"{key} must be a non-empty string")


def validate_mappings(mappings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate and normalize mapping records without upgrading their claims."""
    if len(mappings) == 0:
        raise ValueError("at least one mapping is required")
    normalized = []
    seen = set()
    required = (
        "mapping_id", "source_custom", "target_custom", "source_form",
        "target_form", "semantic_id", "domain", "grade",
    )
    for raw in mappings:
        if not isinstance(raw, dict):
            raise ValueError("each mapping must be an object")
        item = dict(raw)
        for key in required:
            item[key] = _required_text(item, key)
        if item["grade"] not in GRADES:
            raise ValueError(f"unsupported grade: {item['grade']}")
        if item["mapping_id"] in seen:
            raise ValueError(f"duplicate mapping_id: {item['mapping_id']}")
        seen.add(item["mapping_id"])
        provenance = item.get("provenance")
        if not isinstance(provenance, dict) or len(provenance) == 0:
            raise ValueError(f"{item['mapping_id']}: provenance is required")
        item.setdefault("relation", "maps_to")
        item.setdefault("kernel", None)
        normalized.append(item)
    return normalized


def _stable_id(*parts: str) -> str:
    raw = "\x1f".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def build_dataset(
    mappings: list[dict[str, Any]], *, seed: int = 42
) -> dict[str, Any]:
    """Build query/corpus/qrels plus pair-scoped hard negatives.

    Queries are grouped by custom pair, domain, and semantic concept. A
    candidate sharing a surface token across domains remains a hard negative
    unless its complete semantic key matches the query.
    """
    records = validate_mappings(mappings)
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    pair_records: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    surface_records: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        key = (
            record["source_custom"], record["target_custom"],
            record["domain"], record["semantic_id"],
        )
        grouped[key].append(record)
        pair_records[(record["source_custom"], record["target_custom"])].append(record)
        surface_records[(
            record["source_custom"], record["target_custom"], record["source_form"]
        )].append(record)

    queries: dict[str, dict[str, Any]] = {}
    qrels: dict[str, dict[str, int]] = {}
    candidates: dict[str, list[str]] = {}
    rng = random.Random(seed)

    for key in sorted(grouped):
        source_custom, target_custom, domain, semantic_id = key
        query_id = "q-" + _stable_id(*key)
        relevant = sorted(item["mapping_id"] for item in grouped[key])
        pool = pair_records[(source_custom, target_custom)]
        negatives = sorted(
            item["mapping_id"] for item in pool
            if item["mapping_id"] not in relevant
        )
        rng.shuffle(negatives)
        candidate_ids = sorted(relevant) + negatives
        queries[query_id] = {
            "text": (
                f"Map {semantic_id} from {source_custom} to {target_custom} "
                f"within the {domain} domain; preserve the recorded mapping grade."
            ),
            "source_custom": source_custom,
            "target_custom": target_custom,
            "domain": domain,
            "semantic_id": semantic_id,
        }
        qrels[query_id] = {mapping_id: 1 for mapping_id in relevant}
        candidates[query_id] = candidate_ids

    conflicts = []
    for key, items in sorted(surface_records.items()):
        semantic_keys = sorted({(item["domain"], item["semantic_id"]) for item in items})
        if len(semantic_keys) > 1:
            conflicts.append({
                "source_custom": key[0],
                "target_custom": key[1],
                "source_form": key[2],
                "mapping_ids": sorted(item["mapping_id"] for item in items),
                "semantic_keys": [
                    {"domain": domain, "semantic_id": semantic_id}
                    for domain, semantic_id in semantic_keys
                ],
            })

    return {
        "schema": SCHEMA,
        "seed": seed,
        "corpus": {item["mapping_id"]: item for item in records},
        "queries": queries,
        "qrels": qrels,
        "candidates": candidates,
        "conflicts": conflicts,
        "stats": {
            "mappings": len(records),
            "queries": len(queries),
            "relevance_judgments": sum(len(value) for value in qrels.values()),
            "conflict_groups": len(conflicts),
            "grades": {
                grade: sum(item["grade"] == grade for item in records)
                for grade in sorted(GRADES)
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON file containing a mappings array")
    parser.add_argument("--output", required=True, help="Output benchmark JSON path")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    mappings = source["mappings"] if isinstance(source, dict) else source
    dataset = build_dataset(mappings, seed=args.seed)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(dataset["stats"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
