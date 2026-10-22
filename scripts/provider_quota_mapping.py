#!/usr/bin/env python3
"""Typed, offline quota-source mapping for already-received provider responses.

No networking, polling, entitlement inference, or admission decision occurs here.
"""
from __future__ import annotations
import datetime as dt
import importlib
from typing import Any, Mapping

MAX_TTL_SECONDS = 60
SOURCES = {
    "groq": {"https://api.groq.com/openai/v1/models": ("organization_model_metric", "requests_and_tokens")},
    "sambanova": {"https://api.sambanova.ai/v1/models": ("user_key_metric", "requests_only")},
    "huggingface": {"https://huggingface.co/api/models": ("hub_api_user_or_org", "hub_api_requests_only")},
    "ollama": {"https://ollama.com/api/balance": ("account_or_shared_team_pool", "monetary_balance_only")},
    "openrouter": {"https://openrouter.ai/api/v1/key": ("api_key_daily_counter_and_separate_monetary", "requests_and_monetary_separate")},
    "siliconflow": {"https://api.siliconflow.com/v1/user/info": ("user_account", "monetary_balance_only_not_request_quota")},
}
PASSIVE = {"groq", "sambanova", "huggingface", "ollama", "openrouter"}


def _gemini_evidence_parser_available(manager: Mapping[str, Any]) -> bool:
    # PR #1441 owns this internal PRIVATE evidence contract, not an HTTP reader.
    # A metadata status alone must not turn absent code into parser coverage.
    if manager.get("status") != "implemented_passive_adapter":
        return False
    try:
        module = importlib.import_module("scripts.provider_quota_gemini")
    except ModuleNotFoundError as exc:
        if exc.name != "scripts.provider_quota_gemini":
            raise
        return False
    return callable(getattr(module, "normalize_gemini_evidence", None))


def capability(family: str, manager: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manager = manager if isinstance(manager, Mapping) else {}
    if family in SOURCES:
        status = "implemented_passive_parser" if family in PASSIVE else "opt_in_private_monetary_parser"
        dims = SOURCES[family][next(iter(SOURCES[family]))][1]
        scope = manager.get("scope") or next(iter(SOURCES[family].values()))[0]
        source = "official_endpoint_metadata"
        parser = True
    elif family == "gemini" and _gemini_evidence_parser_available(manager):
        status, dims = "implemented_passive_parser", "project_model_rpm_input_tpm_rpd"
        scope = manager.get("scope") or "project_and_exact_model"
        source, parser = "caller_supplied_private_evidence", True
    elif family == "gemini" or manager.get("status") == "public_documentation_only":
        status, dims, scope, source, parser = "documentation_only", "unknown", "unknown", "official_documentation_only", False
    else:
        status, dims, scope, source, parser = "unsupported_or_unknown", "unknown", "unknown", "none_verified", False
    return {"status": status, "dimensions": dims, "scope": scope,
            "entitlement": "unknown; not inferred", "remaining": "not_observed",
            "reset": manager.get("reset", "unknown"), "freshness": "unknown_until_timestamped_observation",
            "fail_closed": True, "parser_available": parser, "source_kind": source,
            "evidence": [x for x in ([manager.get("source")] + list(manager.get("official_evidence", []))) if isinstance(x, str) and x.startswith("https://")]}


def _unknown(family: str, reason: str) -> dict[str, Any]:
    return {"provider_family": family, "status": "unknown", "reason": reason,
            "signals": {}, "remaining": "not_observed", "entitlement": "unknown",
            "reset": "unknown", "scope": "unknown", "valid_until": None,
            "runtime_admission": "unchanged"}


def observe_family(family: str, *, source: str, observed_at: str,
                   headers: Mapping[str, Any] | None = None,
                   metadata: Mapping[str, Any] | None = None,
                   scope: str | None = None, now: dt.datetime | None = None,
                   ttl_seconds: float = MAX_TTL_SECONDS) -> dict[str, Any]:
    """Normalize response metadata only if its origin, scope and timestamp are valid."""
    if not isinstance(family, str) or family not in SOURCES:
        return _unknown(family, "unsupported_source")
    if not isinstance(source, str) or source not in SOURCES[family]:
        return _unknown(family, "source_not_allowlisted_for_family")
    if not isinstance(scope, str) or not scope.strip():
        return _unknown(family, "scope_required")
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, (int, float)) or not 0 < ttl_seconds <= MAX_TTL_SECONDS:
        return _unknown(family, "invalid_ttl")
    try:
        if not isinstance(observed_at, str):
            return _unknown(family, "invalid_timestamp")
        stamp = dt.datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError
        stamp = stamp.astimezone(dt.timezone.utc)
        current = dt.datetime.now(dt.timezone.utc) if now is None else now
        if not isinstance(current, dt.datetime) or current.tzinfo is None or current.utcoffset() is None:
            return _unknown(family, "invalid_now")
        age = (current.astimezone(dt.timezone.utc) - stamp).total_seconds()
        if age < 0:
            return _unknown(family, "future_timestamp")
        if age >= ttl_seconds:
            return _unknown(family, "stale_timestamp")
        if family == "siliconflow" and (not isinstance(metadata, Mapping)
                or metadata.get("status") is not True or type(metadata.get("code")) is not int
                or metadata["code"] != 20000):
            return _unknown(family, "source_success_not_established")
        from scripts.provider_quota_managers import normalize_observation
        parsed = normalize_observation(family, headers=headers, metadata=metadata,
                                       observed_at=observed_at, scope=scope)
        if parsed["status"] != "observed":
            return _unknown(family, "no_signals")
        signals = parsed["signals"]
        resets = []
        for field in ("ollama_included_period_until", "ollama_session_resets_at",
                      "ollama_weekly_resets_at", "effective_budget_resets_at"):
            if isinstance(signals.get(field), str):
                resets.append(dt.datetime.fromisoformat(signals[field].replace("Z", "+00:00")))
        if "ollama_included_period_from" in signals:
            start = dt.datetime.fromisoformat(signals["ollama_included_period_from"].replace("Z", "+00:00"))
            if start > current:
                return _unknown(family, "source_period_not_current")
        for field in ("reset_after_requests", "reset_after_tokens", "reset_after_requests_day", "ratelimit_reset_after_seconds"):
            if field in signals:
                resets.append(stamp + dt.timedelta(seconds=signals[field]))
        if any(reset <= current for reset in resets):
            return _unknown(family, "source_reset_due_refresh_required")
        valid_until = min([stamp + dt.timedelta(seconds=ttl_seconds), *resets])
        expected_scope, dimensions = SOURCES[family][source]
        return {**parsed, "source": source, "dimensions": dimensions,
                "scope_class": expected_scope, "freshness_seconds": age,
                "ttl_seconds": ttl_seconds, "entitlement": "unknown",
                "reset": min(resets).isoformat() if resets else "unknown",
                "valid_until": valid_until.isoformat(),
                "remaining": "not_observed", "runtime_admission": "unchanged"}
    except (TypeError, ValueError, OverflowError, KeyError):
        return _unknown(family, "malformed_or_unavailable_signal")


def service_capability(service: Mapping[str, Any]) -> dict[str, Any]:
    readers = {"github.actions.cache": ("scripts.quota_poll.gh_cache", "repository cache bytes/count, not Actions billing or job capacity"),
               "vercel.deployments": ("scripts.quota_poll.vercel_deploys", "rolling deployment listing; enforcement undercount possible"),
               "render.bandwidth": ("scripts.quota_poll.render_reader", "service outbound bandwidth"),
               "render.pipeline_minutes": ("scripts.quota_poll.render_reader", "deploy wall-clock estimate, not authoritative billed minutes"),
               "neon.compute": ("scripts.quota_poll.neon_reader", "busiest returned project compute; not complete account usage"),
               "neon.storage": ("scripts.quota_poll.neon_reader", "busiest returned project storage; not complete account usage"),
               "openrouter.free_models": ("scripts.quota_poll.openrouter_reader", "daily free-model request counter; no monetary inference"),
               "ollama.balance": ("scripts.provider_quota_service.observe_service", "opt-in monetary or legacy percent; not requests"),
               "openrouter.key": ("scripts.provider_quota_service.observe_service", "opt-in key budget and daily request dimensions separate"),
               "siliconflow.balance": ("scripts.provider_quota_service.observe_service", "opt-in monetary strings; currency/request quota unknown"),
               "github.api.github_token": ("scripts.github_quota_manager.observe", "REST resources; caller declares token class"),
               "github.api.user_token": ("scripts.github_quota_manager.observe", "REST resources; caller declares token class"),
               "github.api.graphql": ("scripts.github_quota_manager.observe", "GraphQL points/hour; separate from REST"),
               "github.api.app_installation": ("scripts.github_quota_manager.observe", "REST installation token resources; thresholds not inferred")}
    entry = readers.get(service.get("id"))
    return {"status": "typed_reader" if entry else "unknown_unless_explicit_reader_registered",
            "reader": entry[0] if entry else None,
            "reader_dimensions": entry[1] if entry else "unknown",
            "dimension": entry[1] if entry else service.get("unit", "unknown"),
            "scope": service.get("lane", "unknown"),
            "entitlement": "registry_limit_is_documentation_not_account_entitlement",
            "remaining": "not_observed_by_public_coverage_inventory",
            "reset": service.get("reset", "unknown"),
            "freshness": "unknown_until_timestamped_observation", "fail_closed": True}
