#!/usr/bin/env python3
"""Offline PRIVATE Gemini project/model quota evidence; never runtime admission.

Official semantics: https://ai.google.dev/gemini-api/docs/rate-limits and
https://ai.google.dev/gemini-api/docs/billing. Project quotas are not API-key
quotas; inherited billing-account tier is not observed headroom or entitlement.
The input below is an internal evidence contract, NOT a Google response schema.
No network, credentials, inference, retry, paid fallback or live binding collector.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Any, Mapping
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
PACIFIC = ZoneInfo("America/Los_Angeles")
DIMENSIONS = ("rpm", "input_tpm", "rpd")
TIERS = ("unknown", "free", "tier_1", "tier_2", "tier_3")
ENTITLEMENTS = ("unknown", "eligible", "ineligible")


def _alias(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value):
        raise ValueError(f"invalid {label}")
    return value


def _time(value: Any) -> dt.datetime:
    try:
        parsed = value if isinstance(value, dt.datetime) else (
            dt.datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None)
        if parsed is None or parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError
        return parsed.astimezone(UTC)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("invalid timezone-aware timestamp") from None


def _iso(value: dt.datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _count(value: Any, label: str) -> int:
    if type(value) is not int or not 0 <= value <= 10**15:
        raise ValueError(f"{label} must be a bounded non-negative integer")
    return value


def _dimensions(raw: Any, when: dt.datetime) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or set(raw) - {*DIMENSIONS, "tpd", "ipm"}:
        raise ValueError("invalid quota dimensions")
    safe: dict[str, Any] = {name: None for name in (*DIMENSIONS, "tpd", "ipm")}
    for name, item in raw.items():
        if item is None:
            continue
        if name in ("tpd", "ipm"):
            raise ValueError("unsupported quota dimension must remain unknown")
        if not isinstance(item, Mapping) or set(item) != {"limit", "used", "remaining", "window"}:
            raise ValueError("incomplete quota dimension")
        limit, used, remaining = (_count(item[key], key) for key in ("limit", "used", "remaining"))
        if used + remaining != limit:
            raise ValueError("inconsistent quota counters")
        window = item["window"]
        if not isinstance(window, Mapping) or set(window) != {"kind", "start", "end"}:
            raise ValueError("explicit quota window required")
        start, end = _time(window["start"]), _time(window["end"])
        if not start <= when < end:
            raise ValueError("quota window is not current")
        kind = window["kind"]
        if name in ("rpm", "input_tpm"):
            # The source must establish its window; do not infer rolling/fixed reset.
            if kind != "explicit":
                raise ValueError("minute quota requires explicit window evidence")
        else:
            local = when.astimezone(PACIFIC)
            day_start = dt.datetime.combine(local.date(), dt.time(), PACIFIC).astimezone(UTC)
            day_end = dt.datetime.combine(local.date() + dt.timedelta(days=1), dt.time(), PACIFIC).astimezone(UTC)
            if kind != "pacific_day" or (start, end) != (day_start, day_end):
                raise ValueError("daily quota must match current Pacific calendar day")
        safe[name] = {"limit": limit, "used": used, "remaining": remaining,
                      "window": {"kind": kind, "start": _iso(start), "end": _iso(end)}}
    return safe


def normalize_gemini_evidence(metadata: Mapping[str, Any], *, observed_at: str | dt.datetime,
                              scope: str) -> dict[str, Any]:
    """Allowlist caller-supplied PRIVATE evidence, never authenticate caller claims.

    Nonempty envelopes require source_kind='aistudio_project_quota', matching
    project_alias, credential_alias, exact model, tier, entitlement and dimensions.
    A dimension is unknown (None) or a complete integer limit/used/remaining triplet
    with an explicit window. Source observed_at wins over wrapper collection time.
    Empty evidence returns unknown rather than inventing a standard tier or quota.
    """
    scope_alias = _alias(scope, "private project alias")
    if not isinstance(metadata, Mapping):
        raise ValueError("Gemini evidence must be a mapping")
    allowed = {"source_kind", "project_alias", "credential_alias", "model", "tier", "entitlement", "dimensions", "observed_at"}
    if metadata:
        if (set(metadata) - allowed or not (allowed - {"observed_at"}) <= set(metadata)
                or metadata.get("source_kind") != "aistudio_project_quota"):
            raise ValueError("invalid Gemini evidence envelope")
        if _alias(metadata["project_alias"], "project alias") != scope_alias:
            raise ValueError("project scope mismatch")
        _alias(metadata["credential_alias"], "credential alias")  # Validate then discard.
        model = _alias(metadata["model"], "model identifier")
        if ":" in model:
            raise ValueError("invalid model identifier")
        tier = metadata["tier"]
        if tier is None:
            tier = "unknown"
        if tier not in TIERS or metadata["entitlement"] not in ENTITLEMENTS:
            raise ValueError("invalid tier or entitlement")
        entitlement = metadata["entitlement"]
    else:
        model, tier, entitlement = "unknown", "unknown", "unknown"
    when = _time(metadata.get("observed_at", observed_at))
    dims = _dimensions(metadata.get("dimensions", {}), when)
    return {"schema": "gemini-project-quota-observation/v1", "provider_family": "gemini",
            "source_kind": "aistudio_project_quota" if metadata else "unknown",
            "observed_at": _iso(when), "project_alias": scope_alias,
            "credential_alias": None, "binding_status": "unknown", "account_identity": "unknown",
            "quota_scope": "project", "tier_scope": "billing_account_inherited_or_unknown",
            "model": model, "tier": tier, "entitlement": entitlement, "dimensions": dims,
            "evidence_status": "caller_supplied_unverified",
            "tier_status": "caller_supplied_unverified" if tier != "unknown" else "unknown",
            "entitlement_status": "caller_supplied_unverified" if entitlement != "unknown" else "unknown",
            "status": "unknown", "runtime_admission": "unchanged",
            "reset_semantics": {"rpm": "explicit_window_only", "input_tpm": "explicit_window_only",
                                "rpd": "midnight_America/Los_Angeles", "tpd": "unknown", "ipm": "unknown"}}


def evaluate_gemini_quota(observation: Mapping[str, Any], *, now: str | dt.datetime,
                          model: str, project_alias: str, requests: int = 1,
                          input_tokens: int | None = None, max_age_seconds: int = 60) -> dict[str, Any]:
    """Reason-only advisory check; headroom never authenticates binding or admission.

    Every required dimension must be fresh and cover the proposed demand. Even a
    manually forged 'verified' flag cannot grant eligibility: no trusted live
    project/credential/entitlement evidence collector exists in this implementation.
    """
    try:
        now_utc = _time(now)
        alias = _alias(project_alias, "project alias")
        _alias(model, "model identifier")
        req = _count(requests, "requests")
        if req < 1 or (input_tokens is not None and _count(input_tokens, "input_tokens") < 1):
            raise ValueError
        if type(max_age_seconds) is not int or not 1 <= max_age_seconds <= 60:
            raise ValueError
    except (TypeError, ValueError, OverflowError):
        return _decision("unknown", "invalid_evaluation_context")
    if not isinstance(observation, Mapping):
        return _decision("unknown", "invalid_observation")
    try:
        observed = _time(observation.get("observed_at"))
        if observed > now_utc or (now_utc - observed).total_seconds() >= max_age_seconds:
            return _decision("unknown", "stale_or_future_evidence")
        if (observation.get("schema") != "gemini-project-quota-observation/v1"
                or observation.get("provider_family") != "gemini"
                or observation.get("source_kind") != "aistudio_project_quota"
                or observation.get("quota_scope") != "project"
                or observation.get("project_alias") != alias or observation.get("model") != model):
            return _decision("unknown", "binding_or_model_mismatch")
        # Revalidate at source time, then independently expire each window at now.
        dims = _dimensions(observation.get("dimensions"), observed)
        if input_tokens is None:
            return _decision("unknown", "input_token_demand_required")
        depleted = False
        for name in DIMENSIONS:
            item = dims[name]
            if item is None:
                return _decision("unknown", "required_quota_unknown")
            if not _time(item["window"]["start"]) <= now_utc < _time(item["window"]["end"]):
                return _decision("unknown", "quota_window_invalid_or_expired")
            demand = req if name in ("rpm", "rpd") else input_tokens
            depleted |= item["remaining"] < demand
    except (KeyError, TypeError, ValueError, OverflowError):
        return _decision("unknown", "required_quota_unknown")
    if depleted:
        return _decision("unknown", "supplied_quota_exhausted_unverified")
    if observation.get("entitlement") != "eligible":
        return _decision("unknown", "entitlement_not_confirmed")
    return _decision("unknown", "trusted_project_credential_binding_unavailable")


def _decision(status: str, reason: str) -> dict[str, Any]:
    return {"status": status, "reason": reason, "eligible": False,
            "evidence_status": "caller_supplied_unverified",
            "retry": False, "fallback": False, "runtime_admission": "unchanged"}
