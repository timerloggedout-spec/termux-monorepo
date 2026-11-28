#!/usr/bin/env python3
"""Compile the full provider/model candidate pool from canonical repository sources.

Offline reconciliation only: candidate presence never grants runtime eligibility,
provider admission, entitlement, quota, or inference permission.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
from typing import Any

SCHEMA = "provider-model-population/v1"
DEFAULTS = {
    "desk_feed": "ops/challenge/desk-feed.json",
    "quota_registry": "ops/quota/registry.json",
    "g4f_catalog": "data/g4f-working/providers.json",
    "g4f_universe": "data/g4f-working/universe.json",
}

def _read(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes(); value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict): raise ValueError(f"{path}: expected_object")
    return value, raw

def _key(value: str) -> str: return value.strip().casefold()
def _sha(raw: bytes) -> str: return hashlib.sha256(raw).hexdigest()
def _write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".provider-pool-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def compile_population(desk_feed: dict, quota_registry: dict, g4f_catalog: dict,
                       g4f_universe: dict, incumbent_v5: dict | None = None) -> dict:
    if desk_feed.get("schema") != "desk-feed/v1.3": raise ValueError("unsupported_desk_feed_schema")
    services = quota_registry.get("services")
    if not isinstance(services, list) or any(not isinstance(x, dict) for x in services):
        raise ValueError("invalid_quota_registry_services")
    providers = g4f_catalog.get("providers")
    if g4f_catalog.get("schema_version") != "g4f-working-catalog-v1" or not isinstance(providers, list):
        raise ValueError("unsupported_g4f_catalog_schema")
    pairs = g4f_universe.get("pairs")
    if g4f_universe.get("schema") != "g4f-endpoint-universe/v1" or not isinstance(pairs, list):
        raise ValueError("unsupported_g4f_universe_schema")
    if isinstance(g4f_universe.get("pairs_total"), int) and g4f_universe["pairs_total"] != len(pairs):
        raise ValueError("g4f_universe_pair_count_mismatch")
    if any(not isinstance(x, dict) or not isinstance(x.get("provider"), str) or not isinstance(x.get("model"), str) for x in pairs):
        raise ValueError("invalid_g4f_universe_pair")
    if incumbent_v5 is not None and incumbent_v5.get("schema") != "provider-model-catalog/v5":
        raise ValueError("unsupported_incumbent_schema")

    bench = desk_feed.get("dispatch", {}).get("provider_catalog", {})
    inference = bench.get("inference_only", {})
    if not isinstance(inference, dict): raise ValueError("invalid_dispatch_provider_catalog")
    lane_providers = inference.get("distinct_providers", [])
    registry_ids = inference.get("registry_ids", [])
    if not isinstance(lane_providers, list) or not isinstance(registry_ids, list):
        raise ValueError("invalid_model_lane_registry_bench")

    provider_rows: dict[str, dict] = {}
    def add_provider(source: str, name: str, evidence: str, **attrs: Any) -> None:
        if not isinstance(name, str) or not name.strip(): return
        sid = f"{source}:{name.strip()}"
        row = provider_rows.setdefault(sid, {"provider_id": sid, "source_provider_id": name,
            "identity_key": _key(name), "sources": [], "evidence_classes": [], "attributes": {}})
        if source not in row["sources"]: row["sources"].append(source)
        if evidence not in row["evidence_classes"]: row["evidence_classes"].append(evidence)
        for k, v in attrs.items():
            if v is None: continue
            if isinstance(v, list):
                target = row["attributes"].setdefault(k, [])
                target.extend(x for x in v if x not in target)
            else: row["attributes"][k] = v

    for name in lane_providers: add_provider("dispatch-model-lane-registry", str(name), "MODEL_LANE_REGISTRY")
    service_provider_keys = set()
    for row in services:
        name = row.get("provider")
        if isinstance(name, str):
            service_provider_keys.add(_key(name))
            add_provider("quota-service-registry", name, "REGISTERED_SERVICE",
                         service_ids=[row.get("id")], lanes=[row.get("lane")])
    for row in providers:
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            add_provider("g4f-working-catalog", row["id"], str(row.get("evidence_class") or "UNKNOWN"),
                         runtime_eligible=row.get("runtime_eligible"), catalog_model_count=row.get("model_count"))

    models: dict[str, dict] = {}
    def add_model(provider: str, model: str, source: str, evidence: str, **detail: Any) -> None:
        if not provider.strip() or not model.strip(): return
        identity = f"{_key(provider)}\x1f{model.strip()}"
        row = models.setdefault(identity, {"candidate_id": hashlib.sha256(identity.encode()).hexdigest()[:24],
            "provider_id": provider, "model_id": model, "sources": [], "evidence_classes": [],
            "source_details": [], "runtime_eligible": False, "inference_admitted": False})
        if source not in row["sources"]: row["sources"].append(source)
        if evidence not in row["evidence_classes"]: row["evidence_classes"].append(evidence)
        item = {"source": source, "evidence_class": evidence, **detail}
        if item not in row["source_details"]: row["source_details"].append(item)

    for pair in pairs:
        add_provider("g4f-endpoint-universe", pair["provider"], "ENUMERATED_PROVIDER")
        add_model(pair["provider"], pair["model"], "g4f-endpoint-universe", "ENUMERATED_CANDIDATE", g4f_source=pair.get("source"))

    raw_pairs, catalog_pairs, working_pairs = 0, set(), set()
    for row in providers:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str): continue
        name = row["id"]
        for model in row.get("models", []) if isinstance(row.get("models"), list) else []:
            if isinstance(model, str) and model.strip():
                raw_pairs += 1; catalog_pairs.add((name, model))
                add_model(name, model, "g4f-working-catalog", str(row.get("evidence_class") or "REFERENCE_ONLY"),
                          runtime_eligible=row.get("runtime_eligible", False))
        for item in row.get("working_models", []) if isinstance(row.get("working_models"), list) else []:
            if isinstance(item, dict) and isinstance(item.get("model"), str):
                working_pairs.add((name, item["model"]))
                add_model(name, item["model"], "g4f-working-probe-summary", "REPORTED_WORKING_ENTRY",
                          modality=item.get("type"), runtime_eligible=False)

    incumbent_count = 0
    if incumbent_v5 is not None:
        incumbent_models = incumbent_v5.get("models", [])
        if not isinstance(incumbent_models, list): raise ValueError("invalid_incumbent_models")
        for row in incumbent_models:
            if isinstance(row, dict) and isinstance(row.get("provider"), str) and isinstance(row.get("id"), str):
                incumbent_count += 1
                add_provider("incumbent-v5", row["provider"], "CATALOG_PROVIDER_OBSERVED")
                add_model(row["provider"], row["id"], "incumbent-v5", "CATALOG_MODEL_OBSERVED",
                          pricing_classification=row.get("pricing_classification"),
                          access_classification=row.get("access_classification"), active=row.get("active"))

    census = bench.get("endpoint_census", {})
    summary = g4f_catalog.get("summary", {})
    return {
        "schema": SCHEMA, "population_version": "1.0.0", "population_scope": "full-provider-model-candidate-pool",
        "provider_candidates": sorted(provider_rows.values(), key=lambda x: x["provider_id"]),
        "model_candidates": sorted(models.values(), key=lambda x: (x["provider_id"].casefold(), x["model_id"])),
        "source_benchmarks": {
            "quota_service_registry": {"service_records": len(services), "distinct_provider_keys": len(service_provider_keys),
                "model_lane_registry_records": len(registry_ids), "distinct_model_lane_providers": len({_key(str(x)) for x in lane_providers})},
            "dispatch_model_bench": {"model_records": inference.get("model_records"), "distinct_providers": lane_providers,
                "provider_classes": inference.get("provider_classes", {})},
            "g4f_working_catalog": {"providers": len(providers), "declared_model_rows": summary.get("models_catalogued"),
                "raw_model_pairs": raw_pairs, "distinct_model_pairs": len(catalog_pairs),
                "reported_working_pairs": len(working_pairs), "evidence_class": "REFERENCE_ONLY_WITH_REPORTED_WORKING_SUBSET"},
            "g4f_endpoint_universe": {"g4f_version": g4f_universe.get("g4f_version"),
                "providers_total": g4f_universe.get("providers_total"), "pairs_total": len(pairs),
                "counts_by_source": g4f_universe.get("counts_by_source", {}),
                "evidence_class": "ENUMERATION_NOT_LIVE_AVAILABILITY"},
            "historical_actions_verified_endpoint_floor": {"count": census.get("verified_floor"),
                "counted_at": census.get("counted_at"), "sources": census.get("sources", {}),
                "evidence_class": "HISTORICAL_ACTIONS_CENSUS"},
            "incumbent_v5": {"model_rows": incumbent_count, "included": incumbent_v5 is not None},
        },
        "pool_counts": {"source_scoped_provider_candidates": len(provider_rows), "distinct_model_candidates": len(models),
            "g4f_universe_candidates": len(pairs), "inference_admitted_candidates": 0, "runtime_eligible_candidates": 0},
        "tournament_policy": {"population_mode": "candidate-enumeration-first", "all_candidates_seeded": True,
            "execution_requires_separate_admission": True, "candidate_evidence_is_not_runtime_eligibility": True,
            "provider_aliasing": "source-scoped; exact pair joins only; no fuzzy provider merges",
            "stratification": ["source", "evidence_class", "provider", "modality_when_observed"]},
    }

def populate(paths: dict[str, Path], output_dir: Path) -> dict:
    docs, sources = {}, {}
    for name, path in paths.items():
        docs[name], raw = _read(path)
        sources[name] = {"path": str(path), "sha256": _sha(raw), "bytes": len(raw)}
    population = compile_population(docs["desk_feed"], docs["quota_registry"], docs["g4f_catalog"],
                                    docs["g4f_universe"], docs.get("incumbent_v5"))
    population["sources"] = sources
    encoded = (json.dumps(population, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    _write(output_dir / "population-v1.json", encoded)
    manifest = {"schema": "provider-model-population-manifest/v1", "population_schema": SCHEMA,
        "population_version": population["population_version"], "population_sha256": _sha(encoded),
        "sources": sources, "pool_counts": population["pool_counts"],
        "source_benchmarks": population["source_benchmarks"],
        "execution": {"mode": "offline_source_reconciliation", "network_requests": 0,
                      "credentials_required": False, "inference_calls": 0}}
    _write(output_dir / "manifest.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    return manifest

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for key, default in DEFAULTS.items(): parser.add_argument(f"--{key.replace('_', '-')}", type=Path, default=Path(default))
    parser.add_argument("--incumbent-v5", type=Path); parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    paths = {key: getattr(args, key) for key in DEFAULTS}
    if args.incumbent_v5: paths["incumbent_v5"] = args.incumbent_v5
    result = populate(paths, args.output_dir); counts = result["pool_counts"]
    print(f"providers={counts['source_scoped_provider_candidates']} models={counts['distinct_model_candidates']} "
          f"g4f_universe={counts['g4f_universe_candidates']} inference_admitted=0")
    return 0

if __name__ == "__main__": raise SystemExit(main())
