#!/usr/bin/env python3
"""Safe provider quota coverage inventory; never performs network or inference."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _providers():
    # Load registries as source-of-truth rather than freezing a provider list.
    from llm_api_hub.server import research_providers
    from scripts import provider_model_catalog
    return sorted(set(research_providers.ENDPOINTS) | set(provider_model_catalog.ENDPOINTS))

def build_coverage(root: Path = ROOT) -> dict[str, Any]:
    from scripts import quota_poll
    from scripts.provider_quota_mapping import capability, service_capability
    from scripts.provider_quota_service import SERVICES as private_services
    services = json.loads((root / "ops/quota/registry.json").read_text(encoding="utf-8"))["services"]
    # This offline roster link is deliberately separate from quota-service
    # registration and from provider manager/account observation state.
    mappings_path = root / "ops/quota/static-service-mappings.json"
    mapping_doc = json.loads(mappings_path.read_text(encoding="utf-8")) if mappings_path.is_file() else {}
    mapping_rows = mapping_doc.get("provider_families", []) if isinstance(mapping_doc, dict) else []
    mapping_by_family = {r.get("provider_family"): r for r in mapping_rows if isinstance(r, dict) and isinstance(r.get("provider_family"), str)}
    # Optional, independently curated public manager metadata. Its existence is
    # documentation, not proof that a mapping is deployed or live validated.
    managers_path = root / "ops/quota/provider-managers.json"
    managers = json.loads(managers_path.read_text(encoding="utf-8")) if managers_path.is_file() else {}
    manager_rows = managers.get("provider_families", []) if isinstance(managers, dict) else []
    manager_by_family = {r.get("provider_family"): r for r in manager_rows if isinstance(r, dict) and isinstance(r.get("provider_family"), str)}
    def public_manager_row(row: Mapping[str, Any]) -> dict[str, Any]:
        """Copy only documented, non-account-specific display metadata."""
        result: dict[str, Any] = {}
        for field in ("scope", "reset", "status", "documented_limit", "free_entitlement"):
            value = row.get(field)
            if isinstance(value, str) or value is None:
                result[field] = value
        refs = row.get("official_evidence", [])
        if not refs and isinstance(row.get("source"), str): refs = [row["source"]]
        if isinstance(refs, list):
            result["official_evidence"] = [ref for ref in refs if isinstance(ref, str) and ref.startswith(("https://", "http://"))]
        signals = row.get("signals", [])
        if isinstance(signals, list):
            result["documented_signals"] = [
                {key: signal[key] for key in ("header", "path", "field") if isinstance(signal.get(key), str)}
                for signal in signals if isinstance(signal, dict)
                and isinstance(signal.get("field"), str)
                and (isinstance(signal.get("header"), str) or isinstance(signal.get("path"), str))
            ]
        return result
    aliases = {"google": "gemini"}
    # Existence of a URL in documentation is not an implemented live reader.
    reader_ids = set(quota_poll.LIVE) | {"render.bandwidth", "render.pipeline_minutes", "neon.compute", "neon.storage"}
    rows = []
    for family in _providers():
        matches = [svc for svc in services if (svc.get("lane") in {"model", "model-observation"} or svc.get("id") in private_services) and aliases.get(svc.get("provider", "").lower(), svc.get("provider", "").lower()) == family]
        ids = sorted({svc["id"] for svc in matches})
        machine_ids = sorted(set(ids) & reader_ids)
        opt_in_ids = sorted(set(ids) & set(private_services) - ({"siliconflow.balance"} if family == "siliconflow" else set()))
        raw_manager = manager_by_family.get(family, {})
        manager = public_manager_row(raw_manager)
        quota_capability = capability(family, raw_manager)
        static_mapping = mapping_by_family.get(family, {})
        scope = manager.get("scope") or "unknown; verify provider/model/project/account sharing"
        status = quota_capability["status"]
        if quota_capability["source_kind"] == "caller_supplied_private_evidence":
            method = "offline_caller_supplied_evidence_parser; live account validation not established"
        elif status == "implemented_passive_parser":
            method = "implemented_passive_parser; live account validation not established"
        elif status == "documentation_only":
            method = "official_documentation_only; no passive parser"
        elif status == "unsupported_or_unknown":
            method = "unsupported_or_no_verified_official_counter"
        else:
            method = "unknown"
        if opt_in_ids:
            method = "opt_in_private_quota_service; live account validation not established"
        rows.append({
            "provider_family": family,
            "quota_manager_owner": "Manager",
            "freshness_owner": "ChronoMancer",
            "registry": "ops/quota/registry.json",
            "service_ids": ids,
            "source_capability": "registered_service" if matches else "no_provider_specific_quota_capability",
            "observation_method": method,
            "evidence_state": "unknown",
            "mapping_state": "documented_registry_mapping" if ids else "missing_provider_registry_mapping",
            "static_mapping_id": static_mapping.get("mapping_id"),
            "static_mapping_state": "static_roster_link_only" if static_mapping else "missing_static_mapping",
            "static_mapping_evidence": static_mapping.get("evidence", []),
            "static_mapping_live_account_state": "unknown",
            "quota_kind": quota_capability["dimensions"],
            "documented_limit": manager.get("documented_limit"),
            "free_entitlement": manager.get("free_entitlement"),
            "account_entitlement_state": "unknown; public descriptions are not account validation",
            "remaining_state": "not_publicly_observed",
            "private_balance": "not_published",
            "scope": manager.get("scope", "unknown"),
            "documented_reset_semantics": manager.get("reset", "unknown"),
            "observed_reset": "unknown",
            "official_evidence": manager.get("official_evidence", []),
            "documented_signals": manager.get("documented_signals", []),
            "manager_status": manager.get("status", "unknown"),
            "manager_metadata_state": "documented_only" if manager else "unavailable",
            "quota_capability": quota_capability,
            "quota_mapping": {"status": ("implemented_passive_parser" if quota_capability["status"] in {"implemented_passive_parser", "opt_in_private_monetary_parser", "unsupported_live_source_historical_parser"} else quota_capability["status"]), "dimensions": quota_capability["dimensions"], "source_kind": quota_capability["source_kind"]},
            "reader_service_ids": machine_ids,
            "registry_reader_service_ids": machine_ids,
            "opt_in_private_service_ids": opt_in_ids,
            "runtime_manager_state": "implemented_opt_in_private_service" if opt_in_ids else "not_established_by_this_inventory",
            "live_account_validation": "unknown",
            "runtime_admission": "unchanged; this inventory and opt-in quota check do not grant runtime admission",
            "covered": bool(matches),
            "quota_check": "scripts/provider_quota_coverage.py:evaluate (not wired to runtime)",
        })
    resources = [{"service_id": svc["id"], "provider": svc["provider"],
                  "quota_manager_owner": "Manager", "freshness_owner": "ChronoMancer",
                  "observation_method": ("implemented_opt_in_private_service" if svc["id"] in private_services
                                         else "implemented_read_only_reader" if svc["id"] in reader_ids else "manual_or_unknown")}
                  | {"quota_capability": service_capability(svc)}
                 for svc in services]
    static_mapped = sum(r["static_mapping_state"] == "static_roster_link_only" for r in rows)
    registry_mapped = sum(r["mapping_state"] == "documented_registry_mapping" for r in rows)
    mapping_counts = {"actual_mapping": sum(bool(r["reader_service_ids"] or r["opt_in_private_service_ids"]) for r in rows), "passive_parser": sum(r["quota_mapping"]["status"] == "implemented_passive_parser" for r in rows), "documentation_only": sum(r["quota_mapping"]["status"] == "documentation_only" for r in rows), "unknown_or_unsupported": sum(r["quota_mapping"]["status"] == "unsupported_or_unknown" for r in rows)}
    return {"schema": "provider-quota-coverage/v2", "provider_families": rows, "mapping_capability_counts": mapping_counts,
            "service_resources": resources, "network_used": False, "live_inference_used": False,
            "coverage_counts": {"provider_families": len(rows), "registered_provider_family_mappings": registry_mapped,
                                "executable_quota_service_mappings": sum(bool(r["reader_service_ids"] or r["opt_in_private_service_ids"]) for r in rows),
                                "actual_quota_service_mappings": mapping_counts["actual_mapping"],
                                "missing_registered_provider_family_mappings": len(rows) - registry_mapped,
                                "static_adapter_mappings": static_mapped,
                                "missing_actual_quota_service_mappings": len(rows) - mapping_counts["actual_mapping"],
                                "missing_static_adapter_mappings": len(rows) - static_mapped,
                                "opt_in_private_service_managers": sum(bool(r["opt_in_private_service_ids"]) for r in rows),
                                "implemented_passive_adapters": sum(r["quota_capability"]["parser_available"] for r in rows),
                                "documentation_only": sum(r["quota_capability"]["status"] == "documentation_only" for r in rows),
                                "unknown_or_unsupported": sum(r["quota_capability"]["status"] == "unsupported_or_unknown" for r in rows),
                                "quota_source_unknown_including_documentation": sum(r["quota_capability"]["status"] in {"unsupported_or_unknown", "documentation_only"} for r in rows)},
            "policy": "Metadata only; remaining, resets, freshness and entitlement are unknown unless explicitly documented; fail closed; no private values or runtime admission inferred.",
            "manager_metadata_source": "ops/quota/provider-managers.json" if manager_rows else None}

_PRIVATE = {"key", "api_key", "token", "secret", "prompt", "request", "used", "remaining", "account_id", "account"}
def _safe_public(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _safe_public(v) for k, v in obj.items() if k.lower() not in _PRIVATE and not any(x in k.lower() for x in ("api_key", "secret", "prompt", "request_body"))}
    if isinstance(obj, list): return [_safe_public(x) for x in obj]
    return obj

def evaluate(provider: str, model: str, evidence: list[Mapping[str, Any]], *, now: dt.datetime | None = None, safety: float = 0.9, cooldown_seconds: float = 0, max_age_seconds: float = 300) -> dict[str, str]:
    """Reason-only private quota CHECK; ``admit`` is quota-only, not authorization.

    Trusted adapters supply provider/model, horizon=H0, evidence_status=confirmed,
    observed_at/reset_at timezone-aware timestamps, and private limit/used values.
    This function neither authenticates that adapter nor atomically reserves quota.
    """
    def result(reason: str, decision: str = "deny") -> dict[str, str]:
        return {"admit": decision, "reason": reason}

    def finite_number(value: Any) -> bool:
        try:
            return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
        except (TypeError, OverflowError, ValueError):
            return False

    if (not isinstance(provider, str) or not provider or not isinstance(model, str) or not model
            or model == "<model>" or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in model)
            or any(c in model for c in "*?#\\")
            or any(part in ("", ".", "..") for part in model.split("/"))):
        return result("invalid_provider_or_model")
    try:
        known = _providers()
    except Exception:
        return result("unknown_provider")
    if provider not in known:
        return result("unknown_provider")
    if not finite_number(safety) or not 0 < safety <= 1:
        return result("invalid_safety_margin")
    if not finite_number(max_age_seconds) or not 0 < max_age_seconds <= 900:
        return result("invalid_evidence_ttl")
    if not finite_number(cooldown_seconds) or cooldown_seconds < 0:
        return result("invalid_cooldown")
    if cooldown_seconds > 0:
        return result("cooldown_active")
    if now is None:
        now = dt.datetime.now(dt.timezone.utc)
    if not isinstance(now, dt.datetime) or now.tzinfo is None or now.utcoffset() is None:
        return result("invalid_now")
    if not isinstance(evidence, list) or not evidence:
        return result("unknown_evidence")
    matched = [e for e in evidence if isinstance(e, Mapping) and e.get("provider") == provider and e.get("model") == model]
    if len(matched) != 1:
        return result("duplicate_or_missing_evidence")
    e = matched[0]
    try:
        if e.get("evidence_status") != "confirmed" or e.get("horizon") != "H0":
            return result("unconfirmed_or_unauthorized_evidence")
        limit, used = e["limit"], e["used"]
        if not finite_number(limit) or not finite_number(used) or limit <= 0 or used < 0:
            return result("invalid_numeric_bounds")
        observed_raw, reset_raw = e["observed_at"], e["reset_at"]
        if not isinstance(observed_raw, str) or not isinstance(reset_raw, str):
            return result("unknown_reset_or_timestamp")
        observed = dt.datetime.fromisoformat(observed_raw.replace("Z", "+00:00"))
        reset = dt.datetime.fromisoformat(reset_raw.replace("Z", "+00:00"))
        if observed.tzinfo is None or observed.utcoffset() is None or reset.tzinfo is None or reset.utcoffset() is None:
            return result("unknown_reset_or_timestamp")
        if observed > now:
            return result("future_evidence")
        if (now - observed).total_seconds() > max_age_seconds:
            return result("stale_evidence")
        if reset <= now:
            return result("reset_due_refresh_required")
        if used + 1 > safety * limit:
            return result("safety_budget_exhausted")
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        return result("unknown_or_malformed_evidence")
    return result("fresh_scoped_evidence_within_safety_budget", "allow")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true", help="emit JSON (default)")
    p.add_argument("--output", help="write public metadata to path; otherwise stdout")
    p.add_argument("--check", help="fail if checked-in public metadata differs from current registries")
    args = p.parse_args()
    text = json.dumps(_safe_public(build_coverage()), indent=2, sort_keys=True) + "\n"
    if args.check:
        if Path(args.check).read_text(encoding="utf-8") != text:
            raise SystemExit("provider quota coverage is stale; regenerate with --output")
        return
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
