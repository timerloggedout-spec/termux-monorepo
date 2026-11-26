"""Fail-closed admission for live MVT lanes.

Catalog price/free labels identify candidates, not an account's remaining quota.
A lane is admitted only when a separate exact-provider/model account-entitlement
record proves a current non-cash allowance and $0 request cost. This module is
pure and performs no network calls.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

MAX_QUOTA_EVIDENCE_AGE_SECONDS = 900
FREE_ALLOWANCE_SOURCES = {"free_plan", "free_trial", "promotional_free"}
ALLOWANCE_UNITS = {"credits", "requests", "tokens", "USD"}
CADENCES = {"hourly", "daily", "weekly", "monthly", "trial"}


def _utc_z(value: object) -> datetime | None:
    """Parse an explicitly UTC RFC3339 timestamp ending in Z."""
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _decimal(value: object) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def _catalog_claims_zero_cost(row: dict) -> bool:
    return (
        row.get("pricing_classification") == "free_zero_price"
        or row.get("free_suffix") is True
        or row.get("access_classification") == "free_trial"
    )


def is_mvt_model_admitted(
    row: object,
    *,
    expected_provider: str,
    expected_model: str,
    now: datetime | None = None,
) -> bool:
    """Return true only for a current, exact-model, verified $0 entitlement.

    `account_entitlement` must contain provider/model, free-account and terms
    assertions, public-data class, future `expires_at`, zero `cash_cost_usd`,
    positive `remaining_allowance` with an explicit non-cash source/unit/cadence,
    the current `cycle_start`/`cycle_end`, a fresh `observed_at`, and `source`.
    Quota observations older than 15 minutes fail closed.
    """
    if not isinstance(row, dict) or not _catalog_claims_zero_cost(row):
        return False
    if not expected_provider or not expected_model:
        return False
    if row.get("provider") != expected_provider or row.get("id") != expected_model:
        return False

    evidence = row.get("account_entitlement")
    if not isinstance(evidence, dict):
        return False
    if evidence.get("provider") != expected_provider or evidence.get("model") != expected_model:
        return False
    if evidence.get("free_account_verified") is not True or evidence.get("terms_accepted") is not True:
        return False
    if evidence.get("data_class") != "public":
        return False
    if evidence.get("allowance_source") not in FREE_ALLOWANCE_SOURCES:
        return False
    if evidence.get("allowance_unit") not in ALLOWANCE_UNITS:
        return False
    if evidence.get("cadence") not in CADENCES:
        return False
    if not isinstance(evidence.get("source"), str) or not evidence["source"].strip():
        return False

    cash_cost = _decimal(evidence.get("cash_cost_usd"))
    remaining = _decimal(evidence.get("remaining_allowance"))
    if cash_cost != Decimal("0") or remaining is None or remaining <= 0:
        return False

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        return False
    current = current.astimezone(timezone.utc)
    expires_at = _utc_z(evidence.get("expires_at"))
    observed_at = _utc_z(evidence.get("observed_at"))
    cycle_start = _utc_z(evidence.get("cycle_start"))
    cycle_end = _utc_z(evidence.get("cycle_end"))
    if None in (expires_at, observed_at, cycle_start, cycle_end):
        return False
    if expires_at <= current or observed_at > current:
        return False
    if (current - observed_at).total_seconds() > MAX_QUOTA_EVIDENCE_AGE_SECONDS:
        return False
    if not (cycle_start <= observed_at < cycle_end and cycle_start <= current < cycle_end):
        return False
    return True
