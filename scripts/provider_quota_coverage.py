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
    services = json.loads((root / "ops/quota/registry.json").read_text(encoding="utf-8"))["services"]
    aliases = {"google": "gemini"}
    # Existence of a URL in documentation is not an implemented live reader.
    reader_ids = set(quota_poll.LIVE) | {"render.bandwidth", "render.pipeline_minutes", "neon.compute", "neon.storage"}
    rows = []
    for family in _providers():
        matches = [svc for svc in services if svc.get("lane") == "model" and aliases.get(svc.get("provider", "").lower(), svc.get("provider", "").lower()) == family]
        ids = sorted({svc["id"] for svc in matches})
        machine_ids = sorted(set(ids) & reader_ids)
        if family == "gemini":
            scope = "per-project, per-model (gemini.api_free registry evidence)"
        elif family == "openrouter":
            scope = "API-key scoped reading; cross-key/account sharing not established"
        else:
            scope = "unknown; verify provider/model/project/account sharing before admission"
        rows.append({
            "provider_family": family,
            "quota_manager_owner": "Manager",
            "freshness_owner": "ChronoMancer",
            "registry": "ops/quota/registry.json",
            "service_ids": ids,
            "source_capability": "registered_service" if matches else "no_provider_specific_quota_capability",
            "observation_method": "implemented_read_only_reader" if machine_ids else "manual_or_unknown",
            "reader_service_ids": machine_ids,
            "reset": "unknown",
            "key_scope": scope,
            "runtime_admission": "unchanged; this inventory and opt-in quota check do not grant runtime admission",
            "covered": bool(matches),
            "quota_check": "scripts/provider_quota_coverage.py:evaluate (not wired to runtime)",
        })
    resources = [{"service_id": svc["id"], "provider": svc["provider"],
                  "quota_manager_owner": "Manager", "freshness_owner": "ChronoMancer",
                  "observation_method": "implemented_read_only_reader" if svc["id"] in reader_ids else "manual_or_unknown"}
                 for svc in services]
    return {"schema": "provider-quota-coverage/v1", "provider_families": rows,
            "service_resources": resources, "network_used": False, "live_inference_used": False,
            "policy": "Metadata only; no private balances, quota resets, free entitlement or runtime admission inferred."}

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
