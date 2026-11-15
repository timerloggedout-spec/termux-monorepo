#!/usr/bin/env python3
"""Read-only, source-pinned census of QUE provider and inference-arm populations.

This tool performs no network requests and never reads or prints secret values.
It keeps provider counts, route-wiring records, provider×model endpoint counts,
g4f universe enumeration, historical probe successes, and build-arm counts
separate so they cannot be accidentally presented as interchangeable.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _digest(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError:
        return {"exists": False}
    return {"exists": True, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _timestamp(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        # The canonical endpoint census records a date plus prose; use only
        # that explicit date, never infer a time-of-day.
        match = re.match(r"^(\d{4}-\d{2}-\d{2})", value)
        if not match:
            return None
        parsed = dt.datetime.fromisoformat(match.group(1)).replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _age_hours(value: Any, now: dt.datetime) -> float | None:
    parsed = _timestamp(value)
    if parsed is None:
        return None
    return round((now - parsed).total_seconds() / 3600, 2)


def _load_receipts(directory: Path | None) -> dict[str, Any]:
    if directory is None or not directory.exists():
        return {"supplied": False, "receipt_count": 0, "latest_pair_count": 0,
                "validation_status_counts": {}, "inference_status_counts": {},
                "inference_validated": 0, "dispatch_eligible": 0}
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    raw_count = 0
    for path in sorted(directory.rglob("*.json")):
        receipt = _read_json(path)
        if not receipt or receipt.get("schema") != "provider-inference-validation/v1":
            continue
        provider, model = receipt.get("provider"), receipt.get("model") or ""
        if not isinstance(provider, str) or not provider:
            continue
        raw_count += 1
        key = (provider, str(model))
        previous = latest.get(key)
        current_time = _timestamp(receipt.get("observed_at"))
        previous_time = _timestamp(previous.get("observed_at")) if previous else None
        if previous is None or (current_time and (previous_time is None or current_time > previous_time)):
            latest[key] = receipt
    rows = list(latest.values())
    return {
        "supplied": True,
        "receipt_count": raw_count,
        "latest_pair_count": len(rows),
        "validation_status_counts": dict(Counter(str(x.get("validation_status", "unknown")) for x in rows)),
        "inference_status_counts": dict(Counter(str(x.get("inference_status", "unknown")) for x in rows)),
        "inference_validated": sum(x.get("validation_status") == "inference_validated" and x.get("inference_status") == "passed" for x in rows),
        "dispatch_eligible": sum(x.get("dispatch_eligible") is True for x in rows),
        "policy_admitted": sum(x.get("policy_admitted") is True for x in rows),
        "no_cost_verified": sum(x.get("no_cost_verified") is True for x in rows),
    }


def _load_policy(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"supplied": False, "schema": None, "entry_count": None, "provider_count": None, "exact_pair_count": None}
    value = _read_json(path)
    if value is None:
        return {"supplied": True, "valid_json": False, "schema": None, "entry_count": 0, "provider_count": 0, "exact_pair_count": 0}
    entries = value.get("entries") if isinstance(value.get("entries"), list) else []
    providers = {x.get("provider") for x in entries if isinstance(x, dict) and isinstance(x.get("provider"), str)}
    pairs = {(x.get("provider"), x.get("model")) for x in entries
             if isinstance(x, dict) and isinstance(x.get("provider"), str) and isinstance(x.get("model"), str)}
    return {"supplied": True, "valid_json": True, "schema": value.get("schema"),
            "entry_count": len(entries), "provider_count": len(providers), "exact_pair_count": len(pairs)}


def _load_availability(path: Path | None) -> dict[str, Any]:
    value = _read_json(path) if path else None
    if value is None or not isinstance(value.get("providers"), list):
        return {"supplied": False, "provider_count": None, "catalog_ok": None, "inference_ok": None,
                "observed_at": None, "age_hours": None}
    rows = value["providers"]
    return {"supplied": True, "provider_count": len(rows),
            "credential_present": sum(x.get("credential_present") is True for x in rows if isinstance(x, dict)),
            "catalog_ok": sum(x.get("catalog_ok") is True for x in rows if isinstance(x, dict)),
            "inference_ok": sum(x.get("inference_ok") is True for x in rows if isinstance(x, dict)),
            "observed_at": value.get("observed_at")}


def _load_g4f_receipt(path: Path | None, now: dt.datetime) -> dict[str, Any]:
    value = _read_json(path) if path else None
    if value is None or value.get("schema") != "g4f-inference-smoke/v1":
        return {"supplied": False, "attempted": None, "inference_ok": None,
                "providers_ok": None, "observed_at": None, "age_hours": None,
                "dispatch_eligible": 0, "quota_class": "unclassified"}
    rows = value.get("results") if isinstance(value.get("results"), list) else []
    errors = Counter(str(x.get("error") or "none") for x in rows if isinstance(x, dict))
    attempted = value.get("attempted", len(rows))
    inference_ok = value.get("inference_ok", sum(x.get("inference_ok") is True for x in rows if isinstance(x, dict)))
    providers_ok = value.get("providers_ok") if isinstance(value.get("providers_ok"), list) else []
    return {
        "supplied": True,
        "schema": value.get("schema"),
        "source": value.get("source"),
        "offset": value.get("offset"),
        "limit": value.get("limit"),
        "source_population_total": value.get("source_population_total"),
        "attempted": attempted,
        "inference_ok": inference_ok,
        "success_rate": round(inference_ok / attempted, 4) if isinstance(attempted, int) and attempted > 0 and isinstance(inference_ok, int) else None,
        "providers_ok_count": len(providers_ok),
        "error_classes": dict(errors),
        "observed_at": value.get("observed_at"),
        "age_hours": _age_hours(value.get("observed_at"), now),
        "dispatch_eligible": 0,
        "quota_class": "unclassified",
    }


def _load_cadence(path: Path | None, now: dt.datetime) -> dict[str, Any]:
    value = _read_json(path) if path else None
    if value is None:
        return {"supplied": False, "schema": None, "eligible_arms": None, "deferred_arms": None,
                "generated_at": None, "age_hours": None}
    pool = value.get("pool") if isinstance(value.get("pool"), dict) else {}
    return {"supplied": True, "schema": value.get("schema"),
            "eligible_arms": len(pool.get("eligible", [])) if isinstance(pool.get("eligible"), list) else None,
            "deferred_arms": len(pool.get("deferred", [])) if isinstance(pool.get("deferred"), list) else None,
            "generated_at": value.get("generated_at"), "age_hours": _age_hours(value.get("generated_at"), now)}


def build_census(repo_root: Path = ROOT, *, policy_path: Path | None = None,
                 receipts_dir: Path | None = None, availability_path: Path | None = None,
                 cadence_path: Path | None = None, g4f_receipt_path: Path | None = None,
                 now: dt.datetime | None = None,
                 adapter_counts: dict[str, Any] | None = None) -> dict[str, Any]:
    now = now or dt.datetime.now(dt.timezone.utc)
    paths = {
        "desk_feed": repo_root / "ops/challenge/desk-feed.json",
        "quota_registry": repo_root / "ops/quota/registry.json",
        "g4f_catalog": repo_root / "data/g4f-working/providers.json",
        "g4f_universe": repo_root / "data/g4f-working/universe.json",
        "g4f_working_probe": repo_root / "data/g4f-working/working-endpoints.json",
        "build_arms": repo_root / "ops/dispatch/build-arms.json",
        "arm_census": repo_root / "ops/que/feeds/arm-census.json",
    }
    docs = {name: _read_json(path) for name, path in paths.items()}
    desk = docs["desk_feed"] or {}
    provider_catalog = ((desk.get("dispatch") or {}).get("provider_catalog") or {})
    registry = ((provider_catalog.get("census") or {}).get("registry") or {})
    wiring = provider_catalog.get("inference_wiring") or {}
    wired = wiring.get("wired_invoke") or {}
    not_wired = wiring.get("not_wired") or {}
    endpoint_census = provider_catalog.get("endpoint_census") or {}
    availability_registry = provider_catalog.get("inference_availability") or {}
    availability_summary = availability_registry.get("summary") or {}

    g4f_catalog = docs["g4f_catalog"] or {}
    g4f_universe = docs["g4f_universe"] or {}
    g4f_probe = docs["g4f_working_probe"] or {}
    g4f_rows = g4f_catalog.get("providers") if isinstance(g4f_catalog.get("providers"), list) else []
    g4f_endpoints = g4f_probe.get("endpoints") if isinstance(g4f_probe.get("endpoints"), list) else []
    g4f_distinct_working_providers = len({x.get("provider") for x in g4f_endpoints if isinstance(x, dict) and x.get("provider")})

    build_arms = docs["build_arms"] or {}
    arms = build_arms.get("arms") if isinstance(build_arms.get("arms"), list) else []
    arm_census = docs["arm_census"] or {}
    census_arms = arm_census.get("arms") if isinstance(arm_census.get("arms"), list) else []
    arm_verdicts = dict(Counter(str(x.get("verdict", "unknown")) for x in census_arms if isinstance(x, dict)))

    if adapter_counts is None:
        try:
            from scripts import provider_model_catalog
            from llm_api_hub.server import research_providers
            catalog_adapters = len(provider_model_catalog.ENDPOINTS)
            native_adapters = len(research_providers.ENDPOINTS)
            try:
                import yaml
                workflow = yaml.safe_load((repo_root / ".github/workflows/provider-invoke.yml").read_text(encoding="utf-8")) or {}
                events = workflow.get("on", workflow.get(True, {}))
                menu = events.get("workflow_dispatch", {}).get("inputs", {}).get("provider", {}).get("options", [])
                menu = menu if isinstance(menu, list) else []
            except Exception:
                menu = []
            menu_supported = sorted(set(menu) & set(research_providers.ENDPOINTS))
            menu_unadapted = sorted(set(menu) - set(research_providers.ENDPOINTS))
            adapters_not_in_menu = sorted(set(research_providers.ENDPOINTS) - set(menu))
            adapter_counts = {"catalog_adapters": catalog_adapters, "native_invoke_adapters": native_adapters,
                              "workflow_menu_choices": len(menu), "menu_supported_by_native_adapter": len(menu_supported),
                              "menu_without_native_adapter": menu_unadapted,
                              "native_adapters_not_in_menu": adapters_not_in_menu,
                              "native_provider_ids": sorted(research_providers.ENDPOINTS),
                              "catalog_provider_ids": sorted(provider_model_catalog.ENDPOINTS),
                              "menu_supported_provider_ids": menu_supported}
        except Exception as exc:
            adapter_counts = {"error_class": type(exc).__name__}

    wiring_total = wired.get("of")
    wiring_count = wired.get("count")
    unwired_count = not_wired.get("count", 0)
    excluded_count = max(0, wiring_total - wiring_count - unwired_count) if all(isinstance(x, int) for x in (wiring_total, wiring_count, unwired_count)) else None

    result = {
        "schema": "que-provider-population-census/v1",
        "generated_at": now.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "semantics": {
            "provider_counts_are_not_endpoint_counts": True,
            "invoke_wiring_records_are_not_unique_provider_counts": True,
            "historical_success_is_not_current_activation": True,
            "catalog_visibility_is_not_inference_validation": True,
            "inference_validation_is_not_dispatch_eligibility": True,
        },
        "canonical_population": {
            "all_lane_services": registry.get("services_total"),
            "all_lane_distinct_providers": registry.get("distinct_providers_all_lanes"),
            "model_lane_records": registry.get("model_records"),
            "model_lane_distinct_providers": registry.get("model_distinct_providers"),
            "inference_availability_records": availability_summary.get("records"),
            "inference_availability_by_class": availability_summary.get("by_class"),
            "availability_covered_records": availability_summary.get("availability_covered"),
            "availability_secret_only_records": availability_summary.get("availability_secret_only"),
            "availability_not_covered_records": availability_summary.get("availability_not_covered"),
            "batch_endpoint_wired_records": availability_summary.get("batch_endpoint_wired"),
            "invoke_wiring_records": wiring_count,
            "invoke_wiring_record_denominator": wiring_total,
            "invoke_wiring_unwired_records": unwired_count,
            "invoke_wiring_excluded_by_kind_records": excluded_count,
            "endpoint_verified_floor": endpoint_census.get("verified_floor"),
            "endpoint_census_counted_at": endpoint_census.get("counted_at"),
            "endpoint_census_age_hours": _age_hours(endpoint_census.get("counted_at"), now),
            "endpoint_census_note": endpoint_census.get("not_yet_counted"),
        },
        "adapter_population": adapter_counts,
        "g4f_population": {
            "catalog_provider_rows": len(g4f_rows),
            "catalog_model_records_raw": sum(int(x.get("model_count", 0) or 0) for x in g4f_rows if isinstance(x, dict)),
            "catalog_fork_pairs_distinct": g4f_universe.get("fork_pairs_distinct"),
            "catalog_fork_pairs_raw": g4f_universe.get("fork_pairs_raw"),
            "universe_provider_total": g4f_universe.get("providers_total"),
            "universe_pairs_total": g4f_universe.get("pairs_total"),
            "historical_probe_attempted": g4f_probe.get("attempted"),
            "historical_probe_inference_ok": g4f_probe.get("inference_ok"),
            "historical_probe_distinct_working_providers": g4f_distinct_working_providers,
            "historical_probe_at": g4f_probe.get("probed_at"),
            "historical_probe_age_hours": _age_hours(g4f_probe.get("probed_at"), now),
        },
        "build_dispatch": {
            "configured_build_arms": len(arms),
            "arm_census_arms": len(census_arms),
            "arm_census_generated_at": arm_census.get("generated_at"),
            "arm_census_age_hours": _age_hours(arm_census.get("generated_at"), now),
            "arm_census_verdicts": arm_verdicts,
            "configured_arm_ids": [x.get("arm_id") for x in arms if isinstance(x, dict)],
        },
        "policy": _load_policy(policy_path),
        "validation_receipts": _load_receipts(receipts_dir),
        "availability_observation": _load_availability(availability_path),
        "cadence": _load_cadence(cadence_path, now),
        "g4f_live_validation": _load_g4f_receipt(g4f_receipt_path, now),
        "sources": {name: {"path": str(path.relative_to(repo_root)), **_digest(path)} for name, path in paths.items()},
    }
    result["status"] = "complete_inventory" if all(docs.get(k) is not None for k in ("desk_feed", "quota_registry", "g4f_catalog", "g4f_universe", "g4f_working_probe", "build_arms", "arm_census")) else "partial_inventory"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--policy", type=Path, default=Path(os.environ["LLM_API_HUB_PROVIDER_POLICY"]) if os.environ.get("LLM_API_HUB_PROVIDER_POLICY") else None)
    parser.add_argument("--receipts-dir", type=Path)
    parser.add_argument("--availability", type=Path)
    parser.add_argument("--cadence", type=Path)
    parser.add_argument("--g4f-receipt", type=Path)
    parser.add_argument("--out", type=Path, default=Path("-"))
    args = parser.parse_args()
    report = build_census(args.repo_root, policy_path=args.policy, receipts_dir=args.receipts_dir,
                          availability_path=args.availability, cadence_path=args.cadence,
                          g4f_receipt_path=args.g4f_receipt)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if str(args.out) == "-":
        print(payload, end="")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
