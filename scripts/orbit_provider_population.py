"""Read-only projection of the canonical provider dispatch population.

This is an adapter over the desk feed and G4F evidence files, not a registry.
It never probes providers, reads secrets, or claims that a catalog route is
currently healthy or authenticated.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA = "orbit-provider-population/v1"
DESK_FEED_SCHEMA = "desk-feed/v1.3"
G4F_SCHEMA = "g4f-working-endpoints/v1"


def _strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted({value.strip() for value in values
                   if isinstance(value, str) and value.strip()})


def _safe_count(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _route_surfaces(wiring: dict[str, Any]) -> dict[str, set[str]]:
    surfaces: dict[str, set[str]] = {}

    def add(provider: str, surface: str) -> None:
        if provider:
            surfaces.setdefault(provider, set()).add(surface)

    for provider in _strings(wiring.get("named_providers")):
        add(provider, "named_invoke")

    by_surface = wiring.get("by_surface", {})
    if not isinstance(by_surface, dict):
        by_surface = {}
    for surface_name, value in by_surface.items():
        if surface_name == "g4f-working/gpt4free route":
            if isinstance(value, dict):
                for provider in _strings(value.get("composite")):
                    add(provider, "g4f_composite")
            continue
        if not isinstance(value, list):
            continue
        for entry in value:
            if not isinstance(entry, str):
                continue
            if surface_name.startswith("connector-config"):
                provider = entry.split("—", 1)[0].strip()
            else:
                provider = entry.strip()
            if provider:
                add(provider, surface_name.split(" ", 1)[0].strip("()"))
    return surfaces


def build_population(feed: dict[str, Any], g4f_working: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(feed, dict) or feed.get("schema") != DESK_FEED_SCHEMA:
        raise ValueError("unsupported_desk_feed_schema")
    catalog = feed.get("dispatch", {}).get("provider_catalog", {})
    availability = catalog.get("inference_availability", {})
    records = availability.get("records", [])
    if not isinstance(records, list):
        raise ValueError("inference_availability_records_must_be_list")

    wiring = catalog.get("inference_wiring", {}).get("wired_invoke", {})
    surfaces = _route_surfaces(wiring)
    g4f_route = wiring.get("by_surface", {}).get("g4f-working/gpt4free route", {})
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        provider = record.get("provider")
        if isinstance(provider, str) and provider.strip():
            grouped.setdefault(provider.strip(), []).append(record)

    catalog_names = set(_strings(catalog.get("inference_only", {}).get("distinct_providers")))
    provider_names = catalog_names | set(grouped) | set(surfaces)
    g4f_records = _safe_count(g4f_route.get("records")) if isinstance(g4f_route, dict) else None
    if g4f_records:
        for provider in provider_names:
            if provider.startswith("g4f/"):
                surfaces.setdefault(provider, set()).add("g4f_catalogued_route")

    g4f_doc = g4f_working if isinstance(g4f_working, dict) else {}
    if g4f_doc.get("schema") not in (None, G4F_SCHEMA):
        raise ValueError("unsupported_g4f_working_schema")
    g4f_endpoints = g4f_doc.get("endpoints", [])
    if not isinstance(g4f_endpoints, list):
        g4f_endpoints = []
    sandbox_by_provider: dict[str, int] = {}
    for endpoint in g4f_endpoints:
        if not isinstance(endpoint, dict):
            continue
        provider = endpoint.get("provider")
        model = endpoint.get("model")
        if isinstance(provider, str) and provider.strip() and isinstance(model, str) and model.strip():
            sandbox_by_provider[provider.strip()] = sandbox_by_provider.get(provider.strip(), 0) + 1

    providers = []
    for provider in sorted(provider_names):
        provider_records = grouped.get(provider, [])
        classes = sorted({
            record.get("class") for record in provider_records
            if isinstance(record.get("class"), str) and record.get("class").strip()
        })
        record_ids = sorted({
            record.get("id") for record in provider_records
            if isinstance(record.get("id"), str) and record.get("id").strip()
        })
        provider_surfaces = sorted(surfaces.get(provider, set()))
        g4f_name = provider.split("/", 1)[1] if provider.startswith("g4f/") else None
        providers.append({
            "id": provider,
            "dispatch_classes": classes,
            "availability_record_count": len(provider_records),
            "availability_record_ids": record_ids,
            "invoke_route_registered": bool(provider_surfaces),
            "invoke_route_surfaces": provider_surfaces,
            "g4f_sandbox_verified_pairs": sandbox_by_provider.get(g4f_name) if g4f_name else None,
        })

    census = catalog.get("endpoint_census", {})
    verified_floor = _safe_count(census.get("verified_floor")) if isinstance(census, dict) else None
    g4f_universe = g4f_doc.get("universe", {}) if isinstance(g4f_doc, dict) else {}
    if not isinstance(g4f_universe, dict):
        g4f_universe = {}
    providers_ok = g4f_doc.get("providers_ok", {}) if isinstance(g4f_doc, dict) else {}

    return {
        "schema": SCHEMA,
        "source": {
            "desk_feed_schema": DESK_FEED_SCHEMA,
            "g4f_schema": g4f_doc.get("schema") if g4f_doc else None,
        },
        "provider_count": len(providers),
        "inference_wiring": {
            "wired": _safe_count(wiring.get("count")),
            "total": _safe_count(wiring.get("of")),
            "named_provider_count": len(_strings(wiring.get("named_providers"))),
            "g4f_route_records": g4f_records,
            "route_surface_provider_count": len(surfaces),
        },
        "endpoint_census": {
            "verified_floor": verified_floor,
            "counted_at": census.get("counted_at") if isinstance(census, dict) else None,
            "unit": census.get("unit") if isinstance(census, dict) else None,
        },
        "g4f": {
            "universe_providers": _safe_count(g4f_universe.get("providers_total")),
            "universe_pairs": _safe_count(g4f_universe.get("pairs_total")),
            "sandbox_verified_pairs": _safe_count(g4f_doc.get("inference_ok")) if g4f_doc else None,
            "sandbox_verified_provider_count": len(providers_ok) if isinstance(providers_ok, dict) else None,
            "actions_verified_pairs": None,
            "actions_verified_evidence": "not_machine_readable_in_desk_feed",
        },
        "providers": providers,
    }


def load_population(repo_root: Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]
    feed_path = root / "ops" / "challenge" / "desk-feed.json"
    g4f_path = root / "data" / "g4f-working" / "working-endpoints.json"
    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    g4f = json.loads(g4f_path.read_text(encoding="utf-8")) if g4f_path.exists() else None
    return build_population(feed, g4f)


def as_orbit_candidates(population: dict[str, Any]) -> list[dict[str, Any]]:
    """Project every registered provider route into ORBIT without inventing scores."""
    if not isinstance(population, dict) or population.get("schema") != SCHEMA:
        raise ValueError("unsupported_provider_population")
    providers = population.get("providers", [])
    if not isinstance(providers, list):
        raise ValueError("provider_population_must_be_list")

    candidates = []
    for provider in providers:
        if not isinstance(provider, dict):
            continue
        provider_id = provider.get("id")
        if not isinstance(provider_id, str) or not provider_id:
            continue
        route_registered = provider.get("invoke_route_registered") is True
        candidates.append({
            "identity": {
                "kind": "provider_route",
                "provider": provider_id,
                "endpoint_id": provider_id,
            },
            "hard_gates": {
                "capability": None,
                "effect": None,
                "provenance": True if provider.get("availability_record_count", 0) > 0 else None,
                "policy": None,
                "endpoint": route_registered,
                "credential": None,
                "authentication": None,
                "catalog_freshness": None,
                "health": None,
                "quota": None,
                "data_classification": None,
                "current_sha": None,
                "execution_authority": None,
            },
            "benefit": {
                "capability_fit": None,
                "repository_outcome": None,
                "task_suitability": None,
                "integration_value": None,
            },
            "risk_cost": {
                "uncertainty": None,
                "failure_risk": None,
                "latency_cost": None,
                "quota_cost": None,
                "context_cost": None,
                "retry_cost": None,
                "conflict_cost": None,
                "human_intervention_cost": None,
            },
            "evidence_refs": [
                "ops/challenge/desk-feed.json#dispatch.provider_catalog.inference_wiring",
                "ops/challenge/desk-feed.json#dispatch.provider_catalog.inference_availability",
            ],
        })
    return candidates
