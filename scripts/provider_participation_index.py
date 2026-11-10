#!/usr/bin/env python3
"""Build an evidence-backed provider participation index; no provider calls."""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

def load(root: Path, rel: str) -> dict:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(f"required source missing: {rel}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {rel}")
    return value

def norm(value: object) -> str:
    return str(value or "").strip().casefold()

def known_model(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    if value.strip().casefold() in {"not established", "not_established", "n∅"}:
        return None
    return value.strip()

def participation_by_provider(nested: dict) -> dict:
    result = {}
    for provider_row in nested.get("providers", []) or []:
        if not isinstance(provider_row, dict):
            continue
        key = norm(provider_row.get("provider"))
        if not key:
            continue
        bucket = result.setdefault(key, {
            "roles": set(), "models": set(), "tasks": [], "proofs": []
        })
        for model_row in provider_row.get("models", []) or []:
            if not isinstance(model_row, dict):
                continue
            model_id = known_model(model_row.get("model"))
            if model_id:
                bucket["models"].add(model_id)
            for role in model_row.get("roles", []) or []:
                if isinstance(role, str) and role.strip():
                    bucket["roles"].add(role.strip())
            for task in model_row.get("tasks", []) or []:
                if not isinstance(task, dict):
                    continue
                outcome = task.get("outcome")
                if isinstance(outcome, dict):
                    outcome = outcome.get("status")
                evidence = {
                    "model_id": model_id,
                    "role": task.get("role") or None,
                    "task_class": task.get("task_class") or None,
                    "source": task.get("source") or None,
                    "source_ref": task.get("source_ref") or None,
                    "run_id": task.get("run_id"),
                    "session_id": task.get("session_id"),
                    "outcome": outcome or None,
                }
                bucket["tasks"].append(evidence)
                if task.get("role"):
                    bucket["roles"].add(str(task["role"]).strip())
                if (norm(task.get("task_class")) == "inference-invoke"
                        and norm(outcome) == "passed"):
                    bucket["proofs"].append(evidence)
    return result

def build(root: Path, generated_at: str | None = None) -> dict:
    registry = load(root, "ops/quota/registry.json")
    desk = load(root, "ops/challenge/desk-feed.json")
    nested = load(root, "ops/tracking/nested-family.json")
    design = load(root, "experiments/doe/util-1-provider-rotation/DESIGN.json")
    catalog = desk.get("dispatch", {}).get("provider_catalog", {})
    dispatch = {}
    for row in catalog.get("inference_availability", {}).get("records", []) or []:
        if not isinstance(row, dict) or not row.get("id"):
            continue
        if row["id"] in dispatch:
            raise ValueError(f"duplicate dispatch record: {row['id']}")
        dispatch[row["id"]] = row

    participation = participation_by_provider(nested)
    records = []
    seen = set()
    for service in registry.get("services", []) or []:
        if not isinstance(service, dict) or service.get("lane") != "model":
            continue
        record_id = service.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("model-lane registry row missing id")
        if record_id in seen:
            raise ValueError(f"duplicate registry record: {record_id}")
        seen.add(record_id)
        route = dispatch.get(record_id)
        evidence = participation.get(norm(service.get("provider")), {
            "roles": set(), "models": set(), "tasks": [], "proofs": []
        })
        dispatch_class = route.get("class") if route else "unmapped"
        inference_route = route.get("inference_route", []) if route else []
        if not isinstance(inference_route, list):
            inference_route = []
        claim_text = " ".join(str(value or "") for value in (service.get("metric"), (service.get("planned_use") or {}).get("note")))
        has_free_claim_text = bool(re.search(r"\bfree\b|no-auth", claim_text, re.IGNORECASE))
        records.append({
            "id": record_id,
            "provider": service.get("provider"),
            "family": record_id.split(".", 1)[0],
            "dispatch_class": dispatch_class,
            "dispatch_mapping_status": "mapped" if route else "unmapped",
            "availability_probe": route.get("availability_probe") if route else None,
            "batch_route": route.get("batch") if route else None,
            "inference_route": inference_route,
            "inference_dispatchable": (
                dispatch_class in {"proven", "wired-unproven", "inference-only"}
                and bool(inference_route)
            ),
            "catalog_probe_declared": bool(
                route and norm(route.get("availability_probe"))
                not in {"", "none", "not-covered"}
            ),
            "registry_live_field": service.get("live"),
            "quota": {key: service.get(key)
                      for key in ("limit", "unit", "window", "reset", "source")},
            "free_tier_claim_text_present": has_free_claim_text,
            "free_tier_claim_source": "ops/quota/registry.json#services[id].metric|planned_use.note" if has_free_claim_text else None,
            "free_eligibility": None,
            "free_eligibility_reason": (
                "No exact account + model admission receipt is asserted by this index. "
                "Catalog price, public plan claims, configured credentials, and "
                "provider-family status are not sufficient."
            ),
            "observed_models": sorted(evidence["models"]),
            "observed_roles": sorted(evidence["roles"]),
            "participation": {
                "task_count": len(evidence["tasks"]),
                "inference_invocations_passed": len(evidence["proofs"]),
            },
        })

    grouped = {}
    for record in records:
        key = norm(record["provider"])
        if not key:
            continue
        provider = grouped.setdefault(key, {
            "provider": record["provider"], "record_count": 0, "record_ids": [],
            "observed_roles": set(), "observed_models": set(),
            "task_count": 0, "inference_invocations_passed": 0,
            "participation_evidence": [], "invocation_proofs": [],
        })
        provider["record_count"] += 1
        provider["record_ids"].append(record["id"])
        provider["observed_roles"].update(record["observed_roles"])
        provider["observed_models"].update(record["observed_models"])
        provider["task_count"] += record["participation"]["task_count"]
        provider["inference_invocations_passed"] += record["participation"]["inference_invocations_passed"]
        evidence = participation.get(key, {})
        provider["participation_evidence"].extend(evidence.get("tasks", []))
        provider["invocation_proofs"].extend(evidence.get("proofs", []))

    providers = [{
        **{key: value for key, value in provider.items()
           if key not in {"observed_roles", "observed_models"}},
        "record_ids": sorted(provider["record_ids"]),
        "observed_roles": sorted(provider["observed_roles"]),
        "observed_models": sorted(provider["observed_models"]),
    } for provider in grouped.values()]
    providers.sort(key=lambda item: str(item["provider"]).casefold())

    classes = {}
    for record in records:
        classes[record["dispatch_class"]] = classes.get(record["dispatch_class"], 0) + 1
    summary = {
        "registry_model_records": len(records),
        "distinct_provider_names": len(providers),
        "id_prefix_families": len({record["family"] for record in records}),
        "dispatch_mapped_records": sum(record["dispatch_mapping_status"] == "mapped" for record in records),
        "dispatch_unmapped_records": sum(record["dispatch_mapping_status"] == "unmapped" for record in records),
        "dispatch_classes": dict(sorted(classes.items())),
        "inference_dispatchable_records": sum(record["inference_dispatchable"] for record in records),
        "catalog_only_records": classes.get("catalog-only", 0),
        "providers_with_observed_roles": sum(bool(provider["observed_roles"]) for provider in providers),
        "providers_with_passed_inference_receipts": sum(
            provider["inference_invocations_passed"] > 0 for provider in providers
        ),
        "records_mentioning_free_tier_claim_text": sum(record["free_tier_claim_text_present"] for record in records),
        "providers_mentioning_free_tier_claim_text": len({record["provider"].casefold() for record in records if record["free_tier_claim_text_present"] and record["provider"]}),
        "free_eligibility_established_records": sum(record["free_eligibility"] is not None for record in records),
        "free_eligibility_unknown_records": sum(record["free_eligibility"] is None for record in records),
    }
    arms = [{
        key: arm.get(key)
        for key in ("provider", "status", "protocols", "activation_gates", "activation_rule")
    } for arm in design.get("conditional_provider_arms", []) or [] if isinstance(arm, dict)]
    return {
        "schema": "provider-participation-index/v1",
        "generated_at": generated_at or datetime.now(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z"),
        "generated_by": "scripts/provider_participation_index.py",
        "sources": {
            "registry": "ops/quota/registry.json",
            "dispatch": "ops/challenge/desk-feed.json#dispatch.provider_catalog.inference_availability",
            "participation": "ops/tracking/nested-family.json",
            "role_contract": "docs/ops/PROVIDER-COLLABORATOR-CAPABILITY-MAP.md",
            "tournament": "experiments/doe/util-1-provider-rotation/DESIGN.json",
        },
        "semantics": {
            "provider_identity": "Registry provider strings are preserved; case-folding is used only for evidence joins.",
            "model_identity": "Exact model IDs appear only where nested-family evidence supplies them; unknown labels become schema null.",
            "roles": "Observed task roles come from nested-family evidence; declared role capabilities remain a separate contract.",
            "inference": "Dispatch route/class is distinct from an actual passed inference-invoke receipt.",
            "free_tier_claims": "Text mentions in the quota registry are indexed as claims only; they do not establish account/model entitlement.",
            "free_eligibility": "Null unless an exact account+model admission receipt exists; this generator does not infer eligibility.",
            "quota": "Limits and resets are copied from the quota registry; null is not zero.",
        },
        "summary": summary,
        "providers": providers,
        "records": records,
        "tournament": {
            "campaign_id": design.get("campaign_id"),
            "status": design.get("status"),
            "assignment": design.get("design", {}).get("assignment"),
            "window_rule": design.get("design", {}).get("window_rule"),
            "cull_rule": design.get("design", {}).get("cull_rule"),
            "provider_stamp_required": ["provider", "selection_reason", "ts"],
            "desk_rotation_rule": catalog.get("rotation_rule", {}).get("rule"),
            "conditional_provider_arms": arms,
        },
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="ops/quota/provider-participation-index.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    document = build(root)
    output = root / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(document["summary"], sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
