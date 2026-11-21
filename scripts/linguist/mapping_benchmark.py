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
GRADES = {"exact", "approximate", "analogue", "lossy", "unverified"}


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


def mappings_from_panel_feed(feed: dict[str, Any]) -> list[dict[str, Any]]:
    """Project included Linguist feed entries into stable lookup records.

    Source IDs are family-scoped hints, not guaranteed unique. Prefer native
    mapping_id/label_id values, then disambiguate reused IDs with a digest of
    the complete source record. Exact duplicate records collapse into one
    benchmark mapping with an explicit occurrence count.
    """
    if feed.get("schema") != "linguist-panel-feed/v1":
        raise ValueError("unsupported Linguist panel feed schema")
    families = {item["id"]: item for item in feed.get("families", [])}
    records_by_id: dict[str, dict[str, Any]] = {}
    identity_ids: dict[str, set[str]] = defaultdict(set)

    for entry in feed.get("entries", []):
        family_id = entry.get("family")
        family = families.get(family_id)
        if not family or not family.get("entries_included", False):
            continue
        direction = entry.get("direction")
        variants = [str(value) for value in entry.get("variants", [])]
        source = str(entry.get("source", ""))
        if direction == "decode-only" and variants:
            source_form, target_form = " | ".join(variants), source
        else:
            source_form = source
            target_form = " | ".join(variants)
            if not target_form:
                target_form = str(entry.get("definition") or "∅ (elided)")
        verified = entry.get("round_trip_verified")
        raw_grade = entry.get("grade")
        grade = raw_grade if raw_grade in GRADES else "unverified"
        round_trip_status = (
            "verified" if verified is True
            else "failed" if verified is False
            else "unverified"
        )
        if entry.get("status") == "candidate":
            evidence_status = "candidate"
        elif verified is True:
            evidence_status = "roundtrip-verified"
        elif verified is False:
            evidence_status = "roundtrip-failed"
        else:
            evidence_status = "unverified"
        if family_id == "nomenclature-mappings":
            semantic_id = source
            domain = "nomenclature"
            source_custom, target_custom = "nomenclature-concepts", "nomenclature-concepts"
        elif family_id == "nomenclature-labels":
            semantic_id = str(entry.get("concept_id") or entry.get("id"))
            domain = str(semantic_id).split(".", 1)[0]
            source_custom, target_custom = "nomenclature-labels", "nomenclature-concepts"
        elif family_id == "nomenclature-concepts":
            semantic_id = str(entry.get("concept_id") or entry.get("id"))
            domain = str(entry.get("domain_id") or "nomenclature")
            source_custom, target_custom = "nomenclature-labels", "nomenclature-concepts"
        else:
            semantic_id = str(entry.get("id"))
            domain = str(entry.get("section") or family_id)
            source_custom = f"{family_id}:source"
            target_custom = f"{family_id}:target"

        provenance = entry.get("provenance") or {}
        native_identity = str(
            entry.get("mapping_id") or entry.get("label_id") or entry.get("id") or ""
        )
        if not native_identity:
            raise ValueError(f"{family_id}: feed entry has no stable identity")
        identity_key = f"{family_id}:{native_identity}"
        canonical_entry = json.dumps(
            entry, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )
        digest = hashlib.sha256(canonical_entry.encode("utf-8")).hexdigest()[:16]
        mapping_id = f"panel-feed:{identity_key}:{digest}"
        if mapping_id in records_by_id:
            records_by_id[mapping_id]["feed_duplicate_count"] += 1
            continue

        record = {
            "mapping_id": mapping_id,
            "source_custom": source_custom,
            "target_custom": target_custom,
            "source_form": source_form,
            "target_form": target_form,
            "semantic_id": semantic_id,
            "domain": domain,
            "relation": entry.get("relation") or (
                "maps_to"
            ),
            "grade": grade,
            "kernel": entry.get("kernel"),
            "evidence_status": evidence_status,
            "provenance": {
                "path": provenance.get("path") or provenance.get("source_path"),
                "locator": provenance.get("detail") or (
                    f"line {provenance['line']}" if provenance.get("line") else entry.get("id")
                ),
            },
            "feed_family": family_id,
            "feed_entry_id": entry.get("id"),
            "feed_identity_key": identity_key,
            "feed_duplicate_count": 1,
            "feed_identity_collision": False,
            "feed_generated_at": feed.get("generated_at"),
            "direction": direction,
            "round_trip_verified": verified,\n            "round_trip_status": round_trip_status,
        }
        for key in (
            "confidence", "status", "grade", "label_type", "label_id", "concept_id",
            "mapping_id", "definition", "meaning", "grimoire", "orchestra",
            "section",
        ):
            if key in entry:
                record[f"feed_{key}"] = entry[key]
        records_by_id[mapping_id] = record
        identity_ids[identity_key].add(mapping_id)

    for record in records_by_id.values():
        record["feed_identity_collision"] = (
            len(identity_ids[record["feed_identity_key"]]) > 1
        )
    return list(records_by_id.values())


def build_dataset(
    mappings: list[dict[str, Any]], *, seed: int = 42, metadata: dict[str, Any] | None = None
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
        "metadata": metadata or {},
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
            "evidence_status": {
                status: sum(item.get("evidence_status", "unspecified") == status
                            for item in records)
                for status in sorted({
                    item.get("evidence_status", "unspecified") for item in records
                })
            },
        },
    }



def evaluate_rankings(
    dataset: dict[str, Any],
    rankings: dict[str, list[str]],
    *,
    ks: tuple[int, ...] = (1, 3, 5),
) -> dict[str, Any]:
    """Score ranked mapping retrieval with macro precision/recall, MRR, and nDCG."""
    import math

    qrels = dataset["qrels"]
    corpus_ids = set(dataset["corpus"])
    unknown_queries = set(rankings) - set(qrels)
    if unknown_queries:
        raise ValueError(f"unknown query ids: {sorted(unknown_queries)}")
    if any(k < 1 for k in ks):
        raise ValueError("all cutoff values must be positive")

    per_query = {}
    for query_id in sorted(qrels):
        ranked = rankings.get(query_id, [])
        if len(ranked) != len(set(ranked)):
            raise ValueError(f"{query_id}: duplicate ranked mapping ids")
        unknown_mappings = set(ranked) - corpus_ids
        if unknown_mappings:
            raise ValueError(f"{query_id}: unknown mapping ids {sorted(unknown_mappings)}")
        relevant = set(qrels[query_id])
        reciprocal_rank = next(
            (1.0 / rank for rank, mapping_id in enumerate(ranked, 1)
             if mapping_id in relevant),
            0.0,
        )
        row = {"mrr": reciprocal_rank}
        for k in ks:
            hits = sum(mapping_id in relevant for mapping_id in ranked[:k])
            precision = hits / k
            recall = hits / len(relevant) if len(relevant) else 0.0
            dcg = sum(
                1.0 / math.log2(rank + 1)
                for rank, mapping_id in enumerate(ranked[:k], 1)
                if mapping_id in relevant
            )
            ideal_hits = min(len(relevant), k)
            idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
            row[f"precision@{k}"] = precision
            row[f"recall@{k}"] = recall
            row[f"ndcg@{k}"] = dcg / idcg if idcg else 0.0
        per_query[query_id] = row

    metric_names = sorted({name for row in per_query.values() for name in row})
    aggregate = {
        name: sum(row[name] for row in per_query.values()) / len(per_query)
        for name in metric_names
    } if per_query else {}
    return {
        "schema": "linguist-mapping-evaluation/v1",
        "query_count": len(per_query),
        "aggregate": aggregate,
        "per_query": per_query,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="JSON file containing a mappings array")
    parser.add_argument("--panel-feed", help="Linguist panel feed JSON to benchmark")
    parser.add_argument("--output", required=True, help="Output benchmark JSON path")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if bool(args.input) == bool(args.panel_feed):
        parser.error("provide exactly one of --input or --panel-feed")
    if args.panel_feed:
        source = json.loads(Path(args.panel_feed).read_text(encoding="utf-8"))
        mappings = mappings_from_panel_feed(source)
        metadata = {
            "source": "linguist-panel-feed",
            "feed_schema": source.get("schema"),
            "feed_generated_at": source.get("generated_at"),
            "feed_contract": source.get("contract"),
            "feed_source_entry_count": len(source.get("entries", [])),
            "feed_projected_mapping_count": len(mappings),
            "feed_duplicate_entries_collapsed": sum(
                item.get("feed_duplicate_count", 1) - 1 for item in mappings
            ),
            "feed_identity_collision_groups": len({
                item["feed_identity_key"] for item in mappings
                if item.get("feed_identity_collision")
            }),
        }
    else:
        source = json.loads(Path(args.input).read_text(encoding="utf-8"))
        mappings = source["mappings"] if isinstance(source, dict) else source
        metadata = source.get("metadata", {}) if isinstance(source, dict) else {}
    dataset = build_dataset(mappings, seed=args.seed, metadata=metadata)
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
