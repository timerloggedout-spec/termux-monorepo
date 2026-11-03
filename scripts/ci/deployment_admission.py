#!/usr/bin/env python3
"""Pure, fail-closed deployment admission and verified-lane selection.

Consumes observations supplied by existing quota/evidence producers. Performs
no network calls, secret reads, retries, deployment, or traffic mutation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from math import floor, isfinite
import re
from typing import Any

SCHEMA = "deployment-admission-input/v1"
DECISION_SCHEMA = "deployment-admission-decision/v1"


def _time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _verified_alternate(lane: Any, *, workload: str, source_sha: str) -> bool:
    if not isinstance(lane, dict) or lane.get("status") != "READY":
        return False
    if not isinstance(lane.get("lane_id"), str) or not lane.get("lane_id"):
        return False
    if lane.get("source_sha") != source_sha or not source_sha:
        return False
    if lane.get("workload") != workload:
        return False
    provider = lane.get("provider")
    if not isinstance(provider, str) or not provider.strip() or provider.lower() == "vercel":
        return False
    if lane.get("independent_failure_domain") is not True:
        return False
    required = (
        "project_verified", "root_verified", "domain_verified",
        "secrets_verified", "healthcheck_verified", "protocol_compatible",
        "state_dependency_verified",
    )
    return all(lane.get(field) is True for field in required)


def evaluate(document: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Return a deterministic decision; unknown evidence never grants admission."""
    if now is None:
        now = datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        return _blocked("INVALID_EVALUATION_TIME")
    now = now.astimezone(timezone.utc)
    if not isinstance(document, dict) or document.get("schema") != SCHEMA:
        return _blocked("INVALID_INPUT_SCHEMA")

    workload = document.get("workload")
    source_sha = document.get("source_sha")
    if (not isinstance(workload, str) or workload not in ("static", "http_api", "mcp")
            or not isinstance(source_sha, str)
            or not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", source_sha)):
        return _blocked("MISSING_OR_INVALID_WORKLOAD_SOURCE_SHA")

    quota = document.get("quota")
    reason = "QUOTA_EVIDENCE_UNAVAILABLE"
    allowed = False
    if isinstance(quota, dict):
        observed_at = _time(quota.get("observed_at"))
        used, limit = quota.get("used"), quota.get("limit")
        max_age = document.get("max_observation_age_seconds", 900)
        safety = document.get("safety_fraction", 0.9)
        valid_numbers = (
            isinstance(used, int) and not isinstance(used, bool) and used >= 0
            and isinstance(limit, int) and not isinstance(limit, bool) and limit > 0
            and isinstance(max_age, int) and not isinstance(max_age, bool) and max_age > 0
            and isinstance(safety, (int, float)) and not isinstance(safety, bool)
            and isfinite(safety) and 0 < safety <= 1
        )
        if not valid_numbers or observed_at is None:
            reason = "QUOTA_EVIDENCE_MALFORMED"
        elif quota.get("provider") != "vercel" or quota.get("resource_id") != "vercel.deployments":
            reason = "QUOTA_RESOURCE_MISMATCH"
        elif quota.get("authority") != "provider_enforcement":
            reason = "QUOTA_NOT_AUTHORITATIVE"
        elif (now - observed_at).total_seconds() < 0 or (now - observed_at).total_seconds() > max_age:
            reason = "QUOTA_OBSERVATION_STALE_OR_FUTURE"
        elif (not isinstance(quota.get("window_id"), str) or not quota.get("window_id")
              or not isinstance(quota.get("scope_id"), str) or not quota.get("scope_id")):
            reason = "QUOTA_WINDOW_OR_SCOPE_UNBOUND"
        elif used >= floor(limit * safety):
            reason = "QUOTA_SAFETY_THRESHOLD_REACHED"
        else:
            allowed = True
            reason = "QUOTA_WITHIN_SAFETY_BUDGET"

    if allowed:
        return {
            "schema": DECISION_SCHEMA,
            "decision": "ADMIT_PRIMARY",
            "selected_lane": "vercel",
            "reason": reason,
            "source_sha": source_sha,
            "traffic_mutated": False,
        }

    alternates = document.get("alternates", [])
    if isinstance(alternates, list):
        for lane in alternates:
            if _verified_alternate(lane, workload=workload, source_sha=source_sha):
                return {
                    "schema": DECISION_SCHEMA,
                    "decision": "SELECT_VERIFIED_ALTERNATE",
                    "selected_lane": lane.get("lane_id"),
                    "reason": reason,
                    "source_sha": source_sha,
                    "traffic_mutated": False,
                }
    elif "alternates" in document:
        reason = "ALTERNATE_EVIDENCE_MALFORMED"
    return _blocked(reason, source_sha=source_sha)


def _blocked(reason: str, *, source_sha: str | None = None) -> dict[str, Any]:
    return {
        "schema": DECISION_SCHEMA,
        "decision": "BLOCK_OPTIONAL_DEPLOYMENT",
        "selected_lane": None,
        "reason": reason,
        "source_sha": source_sha,
        "traffic_mutated": False,
    }
