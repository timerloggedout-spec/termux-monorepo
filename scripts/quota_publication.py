#!/usr/bin/env python3
"""Build a credential-free public quota payload from local quota metadata."""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import tempfile
import sys
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCHEMA = "quota-visibility/v1"
GROUPS = {
    "limits": {"limit", "metric", "unit", "window", "documented_limit", "quota_kind", "dimensions", "token_count", "request_count", "rpm", "tpm", "rpd", "free_model_daily_limit"},
    "usage": {"used", "usage", "count", "requests", "tokens", "requests_used", "tokens_used", "free_model_daily_used"},
    "availability": {"remaining", "free_model_daily_remaining", "available", "status", "availability", "covered", "source_capability", "mapping_state", "manager_status", "observation_method", "evidence_state", "remaining_state", "live_account_validation", "runtime_manager_state", "quota_source_unknown_including_documentation", "static_mapping_state", "static_mapping_live_account_state", "manager_metadata_state", "quota_mapping"},
    "scope": {"scope", "scope_class", "lane", "provider_family"},
    "reset": {"reset", "zone", "documented_reset_semantics", "observed_reset", "reset_at", "valid_until", "observed_at", "horizon", "evidence_status"},
    "sources": {"source", "official_evidence", "evidence", "static_mapping_evidence", "source_kind"},
    "entitlement": {"entitlement", "free_entitlement", "account_entitlement_state", "documented_limit"},
}
DEFAULT_GROUPS = {"limits": "public", "usage": "public", "availability": "public", "scope": "public", "reset": "public", "sources": "public", "entitlement": "public"}
SECRET_KEY = re.compile(r"(?:^|[_-])(account(?:_id)?|project(?:_id)?|user(?:_id)?|organization|org|tenant|credential|api[_-]?key|authorization|token|secret|password|cookie|scope[_-]?id)(?:$|[_-])", re.I)
SECRET_EXACT = {"account_id", "project_id", "user_id", "api_key", "authorization", "token", "secret", "password", "cookie", "credential", "account", "project", "user"}
ENUMS = {
    "status": {"ok", "watch", "exhausted", "cap_tripped", "unknown", "stale", "reported", "documented", "implemented_passive_parser", "unsupported_or_unknown", "actual_quota_service_mapping", "documentation_only"},
    "evidence_status": {"confirmed", "attributed_claim", "unknown"}, "horizon": {"H0", "H1", "H2"},
    "source_kind": {"official_endpoint_metadata", "caller_supplied_private_evidence", "official_documentation_only", "none_verified", "static_registry", "public_registry"},
    "mapping_state": {"documented_registry_mapping", "static_roster_link_only", "unknown"},
    "static_mapping_state": {"static_roster_link_only", "unknown"},
    "manager_status": {"implemented_passive_adapter", "public_documentation_only", "unsupported", "implemented_opt_in_private_service", "unknown"},
    "runtime_manager_state": {"not_established_by_this_inventory", "implemented_opt_in_private_service", "unknown"},
    "static_mapping_live_account_state": {"unknown", "not_published"}, "manager_metadata_state": {"documented_only", "unknown"},
    "scope_class": {"provider", "project", "organization", "user", "account", "unknown"},
}
OFFICIAL_HOSTS = {"docs.github.com", "ai.google.dev", "inference-docs.cerebras.ai", "aionlabs.ai", "openrouter.ai", "vercel.com", "render.com", "platform.openai.com", "docs.anthropic.com", "docs.mistral.ai", "docs.cohere.com", "docs.together.ai", "console.groq.com", "huggingface.co"}
SAFE_PUBLIC_ID = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z0-9_-]+)*$")


def _safe_url(value: Any) -> str | None:
    if not isinstance(value, str) or any(c in value for c in "\\\r\n\t"):
        return None
    u = urlsplit(value)
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.query or u.fragment or u.port not in (None, 443):
        return None
    host = u.hostname.lower()
    if host not in OFFICIAL_HOSTS or not u.path.startswith("/"):
        return None
    if any(x in u.path.lower() for x in ("{", "}", "...", "srv-", "project-", "account-", "user-", "token", "secret", "private")):
        return None
    return value


def _group_for(key: str) -> str | None:
    return next((g for g, keys in GROUPS.items() if key in keys), None)


def _public_value(key: str, value: Any, enabled: set[str]) -> Any:
    if key.lower() in SECRET_EXACT or (key.lower() not in {"token_count", "tokens"} and SECRET_KEY.search(key)):
        return None
    group = _group_for(key)
    if group is None or group not in enabled:
        return None
    if key in ENUMS:
        return value if isinstance(value, str) and value in ENUMS[key] else None
    if key in {"official_evidence", "evidence", "static_mapping_evidence"}:
        if not isinstance(value, list): return None
        return [url for item in value if (url := _safe_url(item))]
    if key == "source": return _safe_url(value)
    if key in {"used", "usage", "remaining", "available", "count", "requests", "tokens", "requests_used", "tokens_used", "free_model_daily_used", "free_model_daily_limit", "free_model_daily_remaining", "limit", "documented_limit", "reset_at", "valid_until", "token_count", "request_count", "rpm", "tpm", "rpd"}:
        if value is None: return None
        if type(value) not in (int, float) or (isinstance(value, float) and not math.isfinite(value)) or value < 0: return None
        return value
    if isinstance(value, bool) or value is None: return None
    if isinstance(value, str):
        if len(value) > 300 or re.search(r"https?://\S+", value) or SECRET_KEY.search(value): return None
        # Free-form scope is never publishable, even when the scope group is enabled.
        if key == "scope": return None
        return value
    if isinstance(value, list):
        return None
    if isinstance(value, dict): return _project_object(value, enabled)
    return None


def _project_object(obj: Mapping[str, Any], enabled: set[str]) -> dict[str, Any]:
    out = {}
    for key, value in obj.items():
        # Check group visibility and forbidden keys before inspecting or emitting a value,
        # including null values (which otherwise reveal disabled/secret field names).
        if not isinstance(key, str) or _group_for(key) is None or _group_for(key) not in enabled or key.lower() in SECRET_EXACT or (key.lower() not in {"token_count", "tokens"} and SECRET_KEY.search(key)):
            continue
        v = _public_value(key, value, enabled)
        if v is not None: out[key] = v
    return out


def _records(doc: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(doc, list): return [x for x in doc if isinstance(x, dict)]
    if isinstance(doc, dict):
        rows = doc.get(key)
        if isinstance(rows, list): return [x for x in rows if isinstance(x, dict)]
        return [doc]
    return []


def _observe_github(readings: Any, token: str | None, observer=None) -> Any:
    """Make an explicit, token-backed read-only observation and retain bounded values."""
    from datetime import datetime, timezone
    ids = {"github.api.github_token", "github.api.graphql"}
    rows = [r for r in _records(readings, "readings")
            if str(r.get("resource_id", r.get("service_id", ""))).removeprefix("quota:") not in ids]
    if not isinstance(token, str) or not token.strip():
        rows.extend({"provider_family": "github", "resource_id": sid, "status": "unknown"} for sid in sorted(ids))
        return {"readings": rows}
    from scripts.github_quota_manager import QuotaError, observe
    if observer is None: observer = observe
    try:
        result = observer(token, token_class="github_token", cache_seconds=0, sleeper=lambda _delay: None)
        resources = result.get("resources", {})
        observed_at = result.get("observed_at")
        parsed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None: raise ValueError("timestamp must have a timezone")
        observed_at = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        for resource, sid, unit in (("core", "github.api.github_token", "requests"), ("graphql", "github.api.graphql", "points")):
            counter = resources.get(resource)
            if not isinstance(counter, dict): continue
            used, limit, remaining, reset = (counter.get(k) for k in ("used", "limit", "remaining", "reset"))
            if any(type(v) is not int or v < 0 for v in (used, limit, remaining, reset)): continue
            rows.append({"provider_family": "github", "resource_id": sid, "service_id": sid,
                         "status": "ok" if remaining > 0 else "exhausted", "used": used, "limit": limit,
                         "remaining": remaining, "reset": datetime.fromtimestamp(reset, timezone.utc).isoformat().replace("+00:00", "Z"),
                         "observed_at": observed_at, "horizon": "H0", "evidence_status": "confirmed", "unit": unit})
        return {"readings": rows}
    except (QuotaError, KeyError, TypeError, ValueError, AttributeError, OverflowError):
        rows.extend({"provider_family": "github", "resource_id": sid, "status": "unknown"} for sid in sorted(ids))
        return {"readings": rows}


def _safe_id(value: Any) -> bool:
    # Public IDs are accepted only in stable dotted registry syntax; do not reject
    # legitimate service IDs such as github.api.github_token as if they were keys.
    return isinstance(value, str) and bool(SAFE_PUBLIC_ID.fullmatch(value))


def _project_reading(row: Mapping[str, Any], enabled: set[str]) -> dict[str, Any]:
    """Unlike curated documentation, dynamic responses may contain no free text."""
    from datetime import datetime, timezone
    allowed = {"used", "usage", "count", "requests", "tokens", "requests_used", "tokens_used",
               "free_model_daily_used", "free_model_daily_limit", "free_model_daily_remaining",
               "limit", "remaining", "rpm", "tpm", "rpd", "status", "horizon", "evidence_status"}
    result = _project_object({key: value for key, value in row.items() if key in allowed}, enabled)
    if "limits" in enabled and isinstance(row.get("unit"), str) and row["unit"] in {"requests", "points", "tokens", "minutes", "hours", "GB", "bytes", "count", "USD", "percent"}:
        result["unit"] = row["unit"]
    if "reset" in enabled:
        for key in ("observed_at", "reset", "valid_until"):
            value = row.get(key)
            if not isinstance(value, str):
                continue
            try:
                stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if stamp.tzinfo is not None and stamp.utcoffset() is not None:
                    result[key] = stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            except (ValueError, OverflowError):
                pass
    return result


def build_payload(registry: Any, coverage: Any, readings: Any, config: Any = None, *, observe_github: bool = False, token: str | None = None, observer=None) -> dict[str, Any]:
    if not isinstance(registry, dict) or not isinstance(coverage, dict): raise ValueError("registry and coverage must be JSON objects")
    configured = config or {"schema": SCHEMA, "families": {}}
    if not isinstance(configured, dict) or configured.get("schema") != SCHEMA or not isinstance(configured.get("families", {}), dict): raise ValueError(f"config schema must be {SCHEMA}")
    gh = configured.get("families", {}).get("github", {})
    if observe_github and (not isinstance(gh, dict) or (gh.get("visibility", "public") != "private" and any(gh.get("fields", {}).get(k, DEFAULT_GROUPS[k]) == "public" for k in ("usage", "availability", "limits")))):
        readings = _observe_github(readings, token, observer)
    services = _records(registry.get("services", []), "services")
    coverage_rows = _records(coverage.get("provider_families", []), "provider_families")
    reading_rows = _records(readings, "readings")
    by_id, by_family = {}, {}
    for row in services:
        sid, provider = row.get("id"), row.get("provider")
        if _safe_id(sid) and isinstance(provider, str):
            family = "gemini" if provider.lower() == "google" else provider.lower()
            by_id[sid] = family
            by_family.setdefault(family, set()).add(sid)
    all_names = set(by_family)
    all_names.update(r["provider_family"] for r in coverage_rows if isinstance(r.get("provider_family"), str) and _safe_id(r["provider_family"]))
    all_names.update(r["provider_family"] for r in reading_rows if isinstance(r.get("provider_family"), str) and _safe_id(r["provider_family"]))
    selections = configured.get("families", {})
    public_registry, public_coverage, public_readings, visible_metadata = [], [], [], {}
    for name in sorted(all_names):
        setting = selections.get(name, {})
        if not isinstance(setting, dict): raise ValueError(f"invalid visibility settings for {name}")
        visibility, fields = setting.get("visibility", "public"), setting.get("fields", {})
        if visibility not in ("public", "private") or not isinstance(fields, dict): raise ValueError(f"invalid visibility settings for {name}")
        if set(fields) - set(GROUPS) or any(v not in ("public", "private") for v in fields.values()): raise ValueError(f"unknown field visibility group for {name}")
        visible_metadata[name] = {"visibility": visibility, "fields": {g: fields.get(g, DEFAULT_GROUPS[g]) for g in GROUPS}}
        if visibility == "private": continue
        enabled = {g for g in GROUPS if fields.get(g, DEFAULT_GROUPS[g]) == "public"}
        for row in services:
            provider = row.get("provider")
            family = "gemini" if isinstance(provider, str) and provider.lower() == "google" else provider.lower() if isinstance(provider, str) else ""
            sid = row.get("id")
            if family == name and _safe_id(sid):
                projected = _project_object(row, enabled)
                projected.update({"id": sid, "provider": name})
                public_registry.append(projected)
        for row in coverage_rows:
            if row.get("provider_family") == name:
                projected = _project_object(row, enabled)
                projected["provider_family"] = name
                public_coverage.append(projected)
        for row in reading_rows:
            rid = row.get("resource_id")
            if isinstance(rid, str): rid = rid.removeprefix("quota:")
            if not _safe_id(rid):
                candidate = row.get("service_id")
                if _safe_id(candidate): rid = candidate
            family = by_id.get(rid) if _safe_id(rid) else None
            if family is None and isinstance(row.get("provider_family"), str) and row.get("provider_family") in all_names:
                family = row.get("provider_family")
            if family != name: continue
            if not _safe_id(rid) or by_id.get(rid) != name: continue
            projected = _project_reading(row, enabled)
            projected["resource_id"] = rid
            projected["provider_family"] = name
            public_readings.append(projected)
    # Derive visible-family counts from visible rows rather than publishing source aggregates.
    result_coverage = {"provider_families": public_coverage}
    keys = ("actual_mapping", "passive_parser", "documentation_only", "unknown_or_unsupported")
    counts = dict.fromkeys(keys, 0)
    for row in public_coverage:
        mapping = row.get("quota_mapping", {})
        status = mapping.get("status") if isinstance(mapping, dict) else None
        if row.get("runtime_manager_state") == "implemented_opt_in_private_service":
            counts["actual_mapping"] += 1
        key = "passive_parser" if status == "implemented_passive_parser" else "documentation_only" if status == "documentation_only" else "unknown_or_unsupported"
        counts[key] += 1
    result_coverage["mapping_capability_counts"] = counts
    result_coverage["coverage_counts"] = {"provider_families": len(public_coverage)}
    return {"schema": "quota-publication/v1", "registry": {"services": public_registry}, "coverage": result_coverage, "readings": {"readings": public_readings}, "visibility": {"schema": SCHEMA, "families": visible_metadata}}


def _read(path: str) -> Any: return json.loads(Path(path).read_text(encoding="utf-8"))


def _atomic_write(path: str, text: str) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", required=True); p.add_argument("--coverage", required=True); p.add_argument("--readings", required=True); p.add_argument("--config", required=True); p.add_argument("--output", required=True); p.add_argument("--check", action="store_true"); p.add_argument("--observe-github", action="store_true", help="explicitly read GitHub rate_limit once; requires GITHUB_TOKEN")
    args = p.parse_args(argv)
    try:
        payload = build_payload(_read(args.registry), _read(args.coverage), _read(args.readings), _read(args.config), observe_github=args.observe_github, token=os.environ.get("GITHUB_TOKEN"))
        text = json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n"
        if args.check:
            if Path(args.output).read_text(encoding="utf-8") != text: p.error("public quota payload is stale")
        else: _atomic_write(args.output, text)
    except (OSError, ValueError, json.JSONDecodeError) as exc: p.error(str(exc))
    return 0


if __name__ == "__main__": raise SystemExit(main())
