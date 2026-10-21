"""Synthetic-only Gemini quota evidence tests; no provider, account, key, or network calls."""
import datetime as dt
import json

import pytest

from scripts.provider_quota_gemini import normalize_gemini_evidence, evaluate_gemini_quota

UTC = dt.timezone.utc
NOW = dt.datetime(2030, 3, 10, 12, tzinfo=UTC)  # Pacific DST transition day
SCOPE = "project:synthetic"


def pacific_day_window(now=NOW):
    local = now.astimezone(__import__("zoneinfo").ZoneInfo("America/Los_Angeles"))
    start = dt.datetime.combine(local.date(), dt.time(), local.tzinfo).astimezone(UTC)
    end = dt.datetime.combine(local.date() + dt.timedelta(days=1), dt.time(), local.tzinfo).astimezone(UTC)
    return {"kind": "pacific_day", "start": start.isoformat(), "end": end.isoformat()}


def evidence(**overrides):
    data = {
        "source_kind": "aistudio_project_quota",
        "project_alias": SCOPE,
        "credential_alias": "claimed-credential",
        "model": "gemini-synthetic-model",
        "tier": "tier_1",
        "entitlement": "eligible",
        "dimensions": {
            "rpm": {"limit": 10, "used": 2, "remaining": 8,
                     "window": {"kind": "explicit", "start": "2030-03-10T11:59:00Z", "end": "2030-03-10T12:01:00Z"}},
            "input_tpm": {"limit": 1000, "used": 200, "remaining": 800,
                          "window": {"kind": "explicit", "start": "2030-03-10T11:59:00Z", "end": "2030-03-10T12:01:00Z"}},
            "rpd": {"limit": 100, "used": 10, "remaining": 90, "window": pacific_day_window()},
            "tpd": None, "ipm": None,
        },
    }
    data.update(overrides)
    return data


def normalized(data=None, observed_at=NOW):
    return normalize_gemini_evidence(evidence() if data is None else data, observed_at=observed_at, scope=SCOPE)


def test_normalization_keeps_project_scope_separate_from_tier_and_account_identity_unknown():
    result = normalized()
    assert result["status"] == "unknown"
    assert result["project_alias"] == SCOPE
    assert result["binding_status"] == "unknown"
    assert result["account_identity"] == "unknown"
    assert result["quota_scope"] == "project"
    assert result["tier_scope"] == "billing_account_inherited_or_unknown"
    assert result["tier"] == "tier_1" and result["entitlement"] == "eligible"
    assert result["dimensions"]["rpm"]["remaining"] == 8
    assert result["dimensions"]["tpd"] is None and result["dimensions"]["ipm"] is None
    assert result["runtime_admission"] == "unchanged"


def test_parser_discards_all_unrecognized_input_and_secret_canaries():
    data = evidence()
    data["credential_alias"] = "SECRET CREDENTIAL CANARY"
    data["extra_secret"] = "RAW PAYLOAD CANARY"
    # Unknown members are rejected with a generic, non-echoing error.
    with pytest.raises(ValueError) as error:
        normalized(data)
    assert "CANARY" not in str(error.value)
    data.pop("extra_secret")
    data["credential_alias"] = "safe-alias"
    data["project_alias"] = "raw-project-id-canary"
    with pytest.raises(ValueError, match="project scope mismatch"):
        normalized(data)
    data["project_alias"] = SCOPE
    result = normalized(data)
    encoded = json.dumps(result)
    assert "raw-project-id-canary" not in encoded
    assert "safe-alias" not in encoded
    assert "SECRET" not in encoded


@pytest.mark.parametrize("bad", [
    {"limit": True, "used": 0, "remaining": 1},
    {"limit": -1, "used": 0, "remaining": 0},
    {"limit": 10, "used": 2, "remaining": 7},
    {"limit": 10**16, "used": 0, "remaining": 10**16},
])
def test_parser_rejects_bad_or_inconsistent_counters(bad):
    data = evidence()
    data["dimensions"]["rpm"] = {**bad, "window": data["dimensions"]["rpm"]["window"]}
    with pytest.raises(ValueError):
        normalized(data)


def test_parser_rejects_incomplete_dimensions_bad_enums_and_inferred_minute_resets():
    for changes in (
        {"tier": "tier_4"}, {"entitlement": True},
        {"dimensions": {**evidence()["dimensions"], "rpm": {"limit": 10}}},
        {"dimensions": {**evidence()["dimensions"], "rpm": {**evidence()["dimensions"]["rpm"], "window": {"kind": "minute", "start": "2030-03-10T11:59:00Z", "end": "2030-03-10T12:01:00Z"}}}},
        {"dimensions": {**evidence()["dimensions"], "tpd": {"limit": 1}}},
    ):
        with pytest.raises(ValueError):
            normalized(evidence(**changes))


def test_rpd_window_respects_pacific_dst_day_length():
    # On spring-forward day, midnight-to-midnight is 23 elapsed hours, not 24.
    window = pacific_day_window()
    start = dt.datetime.fromisoformat(window["start"].replace("Z", "+00:00"))
    end = dt.datetime.fromisoformat(window["end"].replace("Z", "+00:00"))
    assert (end - start).total_seconds() == 23 * 3600
    assert normalized()["dimensions"]["rpd"]["window"]["end"] == window["end"].replace("+00:00", "Z")


def test_parser_rejects_wrong_pacific_day_and_windows_not_covering_observation():
    data = evidence()
    data["dimensions"]["rpd"]["window"]["end"] = "2030-03-11T08:00:00Z"
    with pytest.raises(ValueError):
        normalized(data)
    data = evidence()
    data["dimensions"]["rpm"]["window"]["end"] = "2030-03-10T11:59:59Z"
    with pytest.raises(ValueError):
        normalized(data)


def test_parser_rejects_naive_or_invalid_scope_and_timestamp():
    for scope, timestamp in (("raw/project", NOW), (SCOPE, "2030-03-10T12:00:00")):
        with pytest.raises(ValueError):
            normalize_gemini_evidence(evidence(), observed_at=timestamp, scope=scope)


def test_source_observation_timestamp_is_not_refreshed_by_wrapper_time():
    old = NOW - dt.timedelta(minutes=10)
    data = evidence(observed_at=old.isoformat())
    for name in ("rpm", "input_tpm"):
        data["dimensions"][name]["window"] = {
            "kind": "explicit", "start": "2030-03-10T11:49:00Z",
            "end": "2030-03-10T11:51:00Z",
        }
    result = normalized(data, observed_at=NOW)
    assert result["observed_at"] == old.isoformat().replace("+00:00", "Z")
    decision = evaluate_gemini_quota(result, now=NOW, model="gemini-synthetic-model",
                                     project_alias=SCOPE, input_tokens=1)
    assert decision["reason"] == "stale_or_future_evidence"
    assert decision["eligible"] is False


def test_evaluator_never_enables_admission_without_trusted_binding_even_with_claimed_eligibility():
    result = evaluate_gemini_quota(normalized(), now=NOW, model="gemini-synthetic-model",
                                   project_alias=SCOPE, requests=1, input_tokens=100)
    assert result["eligible"] is False
    assert result["status"] == "unknown"
    assert result["reason"] == "trusted_project_credential_binding_unavailable"
    assert result["runtime_admission"] == "unchanged"
    assert result["retry"] is False and result["fallback"] is False


def test_evaluator_fails_closed_for_missing_dimensions_stale_future_and_invalid_demand():
    observation = normalized()
    observation["binding_status"] = "trusted_upstream_bound"  # even an asserted flag is not evidence
    for now, demand in ((NOW + dt.timedelta(seconds=61), 1),
                        (NOW - dt.timedelta(seconds=1), 1), (NOW, None), (NOW, 0)):
        result = evaluate_gemini_quota(observation, now=now, model="gemini-synthetic-model",
                                       project_alias=SCOPE, input_tokens=demand)
        assert result["eligible"] is False and result["runtime_admission"] == "unchanged"
    missing = dict(observation, dimensions={})
    result = evaluate_gemini_quota(missing, now=NOW, model="gemini-synthetic-model",
                                   project_alias=SCOPE, input_tokens=1)
    assert result["eligible"] is False


def test_evaluator_does_not_mistake_tier_or_pricing_for_counters_or_identity():
    observation = normalized()
    result = evaluate_gemini_quota(observation, now=NOW, model="gemini-synthetic-model",
                                   project_alias="another-project", input_tokens=1)
    assert result["status"] == "unknown" and result["eligible"] is False
    assert "billing" not in json.dumps(result)


@pytest.mark.parametrize("tier", ["unknown", "free", "tier_1", "tier_2", "tier_3", None])
def test_tier_never_fills_missing_thresholds(tier):
    result = normalized(evidence(tier=tier, dimensions={}))
    assert all(value is None for value in result["dimensions"].values())
    assert result["binding_status"] == "unknown"
    decision = evaluate_gemini_quota(result, now=NOW, model=result["model"], project_alias=SCOPE, input_tokens=1)
    assert decision["reason"] == "required_quota_unknown"
    assert decision["eligible"] is False


@pytest.mark.parametrize("dimension", ["rpm", "input_tpm", "rpd"])
def test_each_dimension_exhaustion_is_unverified_not_authenticated_denial(dimension):
    data = evidence()
    data["dimensions"][dimension].update(used=data["dimensions"][dimension]["limit"], remaining=0)
    observation = normalized(data)
    observation.update(binding_status="trusted_upstream_bound", status="observed")
    decision = evaluate_gemini_quota(observation, now=NOW, model=observation["model"], project_alias=SCOPE, input_tokens=1)
    assert decision["status"] == "unknown"
    assert decision["reason"] == "supplied_quota_exhausted_unverified"
    assert decision["evidence_status"] == "caller_supplied_unverified"
    assert decision["eligible"] is False


@pytest.mark.parametrize("field,bad", [("now", "PRIVATE-CLOCK-CANARY"), ("now", dt.datetime(2030, 3, 10)),
                                        ("requests", True), ("requests", -1), ("input_tokens", float("nan")),
                                        ("max_age_seconds", 61), ("max_age_seconds", True)])
def test_invalid_evaluator_inputs_are_fixed_unknown(field, bad):
    kwargs = {"now": NOW, "model": "gemini-synthetic-model", "project_alias": SCOPE, "input_tokens": 1, field: bad}
    result = evaluate_gemini_quota(normalized(), **kwargs)
    assert result["reason"] == "invalid_evaluation_context"
    assert "PRIVATE-CLOCK-CANARY" not in json.dumps(result)
    assert result["eligible"] is False


def test_rpd_fall_back_day_has_twenty_five_hours():
    when = dt.datetime(2030, 11, 3, 12, tzinfo=UTC)
    window = pacific_day_window(when)
    start, end = (dt.datetime.fromisoformat(window[key]) for key in ("start", "end"))
    assert (end - start).total_seconds() == 25 * 3600
    data = evidence(dimensions={"rpd": {"limit": 100, "used": 0, "remaining": 100, "window": window}})
    assert normalized(data, observed_at=when)["dimensions"]["rpd"]["window"]["end"] == end.isoformat().replace("+00:00", "Z")


def test_pacific_midnight_expires_quota_even_inside_freshness_ttl():
    observed = dt.datetime(2030, 3, 11, 6, 59, 50, tzinfo=UTC)
    data = evidence()
    data["dimensions"]["rpd"]["window"] = pacific_day_window(observed)
    for name in ("rpm", "input_tpm"):
        data["dimensions"][name]["window"] = {"kind": "explicit", "start": observed.isoformat(),
                                                  "end": (observed + dt.timedelta(seconds=50)).isoformat()}
    observation = normalized(data, observed_at=observed)
    decision = evaluate_gemini_quota(observation, now=observed + dt.timedelta(seconds=10),
                                     model=observation["model"], project_alias=SCOPE, input_tokens=1)
    assert decision["reason"] == "quota_window_invalid_or_expired"


def test_exact_ttl_boundary_requires_refresh_and_never_resets_counters():
    observation = normalized()
    result = evaluate_gemini_quota(observation, now=NOW + dt.timedelta(seconds=60),
                                   model=observation["model"], project_alias=SCOPE, input_tokens=1)
    assert result["reason"] == "stale_or_future_evidence"
    assert observation["dimensions"]["rpd"]["used"] == 10


def test_direct_observation_cannot_smuggle_utc_rpd_reset_or_bad_counter():
    observation = normalized()
    observation["dimensions"]["rpd"]["window"]["end"] = "2030-03-12T00:00:00Z"
    result = evaluate_gemini_quota(observation, now=NOW, model=observation["model"], project_alias=SCOPE, input_tokens=1)
    assert result["reason"] == "required_quota_unknown"


def test_empty_evidence_and_explicit_unknown_dimensions_stay_unknown():
    empty = normalized({})
    assert empty["tier"] == empty["model"] == empty["entitlement"] == "unknown"
    assert all(value is None for value in empty["dimensions"].values())
    result = normalized(evidence(dimensions={"rpm": None, "input_tpm": None, "rpd": None}))
    assert all(value is None for value in result["dimensions"].values())
