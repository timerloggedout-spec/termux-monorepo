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
        matches = [svc for svc in services if (svc.get("lane") == "model" or svc.get("id") in private_services) and aliases.get(svc.get("provider", "").lower(), svc.get("provider", "").lower()) == family]
        ids = sorted({svc["id"] for svc in matches})
        machine_ids = sorted(set(ids) & reader_ids)
        opt_in_ids = sorted(set(ids) & set(private_services))
        raw_manager = manager_by_family.get(family, {})
        manager = public_manager_row(raw_manager)
        static_mapping = mapping_by_family.get(family, {})
        scope = manager.get("scope") or "unknown; verify provider/model/project/account sharing"
        status = manager.get("status", "unknown")
        if status == "implemented_passive_adapter":
            method = "implemented_passive_parser; live account validation not established"
        elif status == "public_documentation_only":
            method = "official_documentation_only; no passive parser"
        elif status == "unsupported":
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
            "quota_kind": "private_balance_not_publicly_observed",
            "documented_limit": None,
            "free_entitlement": None,
            "private_balance": "not_published",
            "scope": manager.get("scope", "unknown"),
            "documented_reset_semantics": manager.get("reset", "unknown"),
            "observed_reset": "unknown",
            "official_evidence": manager.get("official_evidence", []),
            "documented_signals": manager.get("documented_signals", []),
            "manager_status": manager.get("status", "unknown"),
            "manager_metadata_state": "documented_only" if manager else "unavailable",
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
                 for svc in services]
    static_mapped = sum(r["static_mapping_state"] == "static_roster_link_only" for r in rows)
    registry_mapped = sum(r["mapping_state"] == "documented_registry_mapping" for r in rows)
    return {"schema": "provider-quota-coverage/v1", "provider_families": rows,
            "four_counts": build_four_counts(root),
            "service_resources": resources, "network_used": False, "live_inference_used": False,
            "coverage_counts": {"provider_families": len(rows), "actual_quota_service_mappings": registry_mapped,
                                "static_adapter_mappings": static_mapped,
                                "missing_actual_quota_service_mappings": len(rows) - registry_mapped,
                                "missing_static_adapter_mappings": len(rows) - static_mapped,
                                "opt_in_private_service_managers": sum(bool(r["opt_in_private_service_ids"]) for r in rows),
                                "implemented_passive_adapters": sum(r.get("status") == "implemented_passive_adapter" for r in manager_rows)},
            "policy": "Metadata only; no private balances, quota resets, free entitlement or runtime admission inferred.",
            "manager_metadata_source": "ops/quota/provider-managers.json" if manager_rows else None}

def build_four_counts(root: Path = ROOT) -> dict[str, Any]:
    """The enumeration dossier's four counts, each from its own source.

    wired       = families in ops/quota/provider-managers.json
    callable    = endpoints in scripts/provider_model_catalog.py ENDPOINTS
    provisioned = families in ops/quota/provisioned-families.json whose recorded
                  secret name matches the catalog's canonical SECRETS entry
    executed    = rows of the newest pinned availability observation in
                  ops/quota/ (credential_present / catalog_ok / inference_ok)

    The counts are never blended: each carries its source so a reader can
    re-derive it. Offline only, like the rest of this module.
    """
    from scripts import provider_model_catalog
    managers = json.loads((root / "ops/quota/provider-managers.json").read_text(encoding="utf-8"))
    wired_families = sorted({r.get("provider_family") for r in managers.get("provider_families", [])
                             if isinstance(r, dict) and isinstance(r.get("provider_family"), str)})
    callable_count = len(provider_model_catalog.ENDPOINTS)
    prov_path = root / "ops/quota/provisioned-families.json"
    prov_doc = json.loads(prov_path.read_text(encoding="utf-8")) if prov_path.is_file() else {}
    inconsistencies = []
    provisioned = []
    for entry in prov_doc.get("families", []):
        if not isinstance(entry, dict):
            continue
        family, secret_name = entry.get("family"), entry.get("secret_name")
        if provider_model_catalog.SECRETS.get(family) != secret_name:
            inconsistencies.append({"family": family, "recorded_secret_name": secret_name,
                                    "catalog_secret_name": provider_model_catalog.SECRETS.get(family)})
        else:
            provisioned.append(family)
    provisioned = sorted(provisioned)
    unprovisioned = sorted(set(provider_model_catalog.SECRETS) - set(provisioned))
    snapshots = sorted((root / "ops/quota").glob("availability-observation-*.json"))
    executed: dict[str, Any] = {"source_snapshot": None, "observed_at": None,
                                "rows": None, "credential_present": None,
                                "catalog_ok": None, "inference_ok": None}
    if snapshots:
        snap_path = snapshots[-1]
        snap = json.loads(snap_path.read_text(encoding="utf-8"))
        snap_rows = snap.get("providers", []) if isinstance(snap, dict) else []
        executed = {"source_snapshot": f"ops/quota/{snap_path.name}",
                    "observed_at": snap.get("observed_at") if isinstance(snap, dict) else None,
                    "rows": len(snap_rows),
                    "credential_present": sum(bool(r.get("credential_present")) for r in snap_rows),
                    "catalog_ok": sum(bool(r.get("catalog_ok")) for r in snap_rows),
                    "inference_ok": sum(bool(r.get("inference_ok")) for r in snap_rows)}
    return {"schema": "provider-four-counts/v1",
            "wired": {"count": len(wired_families), "source": "ops/quota/provider-managers.json"},
            "callable": {"count": callable_count, "source": "scripts/provider_model_catalog.py ENDPOINTS"},
            "provisioned": {"count": len(provisioned), "families": provisioned,
                            "unprovisioned_catalog_families": unprovisioned,
                            "inconsistencies": inconsistencies,
                            "source": "ops/quota/provisioned-families.json",
                            "derived_at": prov_doc.get("derived_at")},
            "executed": executed,
            "note": "Counts are never blended; each cites its own source. Generated by scripts/provider_quota_coverage.py."}


def render_four_counts_md(four_counts: Mapping[str, Any]) -> str:
    """Render the four-count table as markdown (ops/quota/four-counts.md)."""
    w, c, p, e = (four_counts[k] for k in ("wired", "callable", "provisioned", "executed"))
    lines = ["# Provider four counts",
             "",
             "Generated by `scripts/provider_quota_coverage.py --four-counts-md`. Do not edit by hand;",
             "each count cites its own source and the four are never blended.",
             "",
             "| Count | Value | Source |",
             "|---|---|---|",
             f"| wired | {w['count']} | {w['source']} |",
             f"| callable | {c['count']} | {c['source']} |",
             f"| provisioned | {p['count']} | {p['source']} (derived {p['derived_at']}) |",
             f"| executed (credential_present / catalog_ok / inference_ok) | {e['credential_present']} / {e['catalog_ok']} / {e['inference_ok']} of {e['rows']} rows | {e['source_snapshot']} (observed {e['observed_at']}) |",
             "",
             f"Provisioned families ({p['count']}): {', '.join(p['families'])}",
             "",
             f"Catalog families not provisioned ({len(p['unprovisioned_catalog_families'])}): {', '.join(p['unprovisioned_catalog_families'])}",
             ""]
    if p["inconsistencies"]:
        lines += ["", f"⚠ provisioned-record inconsistencies: {json.dumps(p['inconsistencies'])}", ""]
    return "\n".join(lines)


_PRIVATE = {"key", "api_key", "token", "secret", "prompt", "request", "used", "remaining", "account_id", "account"}
_SENSITIVE_SUBSTRINGS = ("api_key", "secret", "prompt", "request_body")

def _safe_public(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _safe_public(v) for k, v in obj.items() if k.lower() not in _PRIVATE and not any(x in k.lower() for x in _SENSITIVE_SUBSTRINGS)}
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

    matched = None
    for item in evidence:
        if isinstance(item, Mapping) and item.get("provider") == provider and item.get("model") == model:
            if matched is not None:
                return result("duplicate_or_missing_evidence")
            matched = item
    if matched is None:
        return result("duplicate_or_missing_evidence")
    e = matched
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
    p.add_argument("--four-counts-md", help="also write the four-count table (markdown) to this path")
    args = p.parse_args()
    coverage = build_coverage()
    if args.four_counts_md:
        Path(args.four_counts_md).write_text(render_four_counts_md(coverage["four_counts"]), encoding="utf-8")
    text = json.dumps(_safe_public(coverage), indent=2, sort_keys=True) + "\n"
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
