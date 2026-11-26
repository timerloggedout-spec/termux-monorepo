from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.mvt_admission import is_mvt_model_admitted

NOW = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)


def _entitlement(**changes):
    record = {
        "provider": "openrouter",
        "model": "peer/model-free",
        "free_account_verified": True,
        "terms_accepted": True,
        "data_class": "public",
        "expires_at": "2026-11-27T00:00:00Z",
        "cash_cost_usd": 0,
        "allowance_source": "promotional_free",
        "remaining_allowance": 0.5,
        "allowance_unit": "USD",
        "cadence": "daily",
        "observed_at": "2026-11-26T11:55:00Z",
        "cycle_start": "2026-11-26T00:00:00Z",
        "cycle_end": "2026-11-27T00:00:00Z",
        "source": "authenticated provider quota response",
    }
    record.update(changes)
    return record


def _row(entitlement=None, **changes):
    row = {
        "provider": "openrouter",
        "id": "peer/model-free",
        "pricing_classification": "free_zero_price",
        "free_suffix": False,
        "access_classification": "unknown",
    }
    if entitlement is not None:
        row["account_entitlement"] = entitlement
    row.update(changes)
    return row


def test_catalog_free_label_alone_does_not_admit_model():
    assert not is_mvt_model_admitted(
        _row(), expected_provider="openrouter", expected_model="peer/model-free", now=NOW
    )


def test_current_exact_model_free_dollar_allowance_is_admitted():
    row = _row(_entitlement())
    assert is_mvt_model_admitted(
        row, expected_provider="openrouter", expected_model="peer/model-free", now=NOW
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"provider": "other-provider"},
        {"model": "peer/different-model"},
        {"free_account_verified": False},
        {"terms_accepted": False},
        {"data_class": "confidential"},
        {"expires_at": "2026-11-26T11:59:59Z"},
        {"cash_cost_usd": 0.01},
        {"allowance_source": "paid_balance"},
        {"remaining_allowance": 0},
        {"allowance_unit": "unknown"},
        {"cadence": "unknown"},
        {"observed_at": "2026-11-26T11:44:59Z"},
        {"cycle_start": "2026-11-26T11:56:00Z"},
        {"cycle_end": "2026-11-26T11:59:59Z"},
        {"source": "  "},
    ],
)
def test_incomplete_stale_or_nonzero_cost_entitlement_fails_closed(changes):
    row = _row(_entitlement(**changes))
    assert not is_mvt_model_admitted(
        row, expected_provider="openrouter", expected_model="peer/model-free", now=NOW
    )


def test_nonzero_catalog_price_cannot_be_overridden_by_entitlement():
    row = _row(_entitlement(), pricing_classification="paid")
    assert not is_mvt_model_admitted(
        row, expected_provider="openrouter", expected_model="peer/model-free", now=NOW
    )


def test_expected_lane_identity_must_match_exact_catalog_model():
    row = _row(_entitlement())
    assert not is_mvt_model_admitted(
        row, expected_provider="felo", expected_model="peer/model-free", now=NOW
    )
    assert not is_mvt_model_admitted(
        row, expected_provider="openrouter", expected_model="peer/another-model", now=NOW
    )


def test_both_mvt_workflows_use_shared_admission_gate():
    root = Path(__file__).resolve().parents[1]
    team_mvt = (root / ".github/workflows/team-mvt.yml").read_text(encoding="utf-8")
    continuous = (root / ".github/workflows/continuous-evaluation.yml").read_text(encoding="utf-8")
    assert "from scripts.mvt_admission import is_mvt_model_admitted" in team_mvt
    assert "is_mvt_model_admitted(" in team_mvt
    assert "from scripts.mvt_admission import is_mvt_model_admitted" in continuous
    candidate_gate = continuous.split("- name: Verify dynamic candidate is still eligible", 1)[1]
    candidate_gate = candidate_gate.split("\n      - name:", 1)[0]
    assert "is_mvt_model_admitted(" in candidate_gate
    assert "eligible=(r['pricing_classification']" not in candidate_gate
