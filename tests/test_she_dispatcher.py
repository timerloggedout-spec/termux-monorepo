"""P0.4 dispatcher scaffold — pure ranking, no network."""
from __future__ import annotations

import pytest

from she.recovery.dispatcher import dispatch_l0_plan, rank_actions
from she.recovery.l0 import L0Plan


def test_rank_prefers_retry_when_authorized() -> None:
    selected, deferred, denied = rank_actions(
        ("observe_only", "retry", "refresh"),
        authority=("L0-retry", "L0-observe"),
    )
    assert selected[0] == "retry"
    assert "observe_only" in selected
    assert deferred == ()
    assert denied == ()


def test_rank_denies_without_authority() -> None:
    selected, deferred, denied = rank_actions(
        ("retry", "observe_only"),
        authority=("L0-observe",),
    )
    assert selected == ("observe_only",)
    assert "retry" in denied


def test_low_moneyball_defers_aggressive_actions() -> None:
    selected, deferred, denied = rank_actions(
        ("retry", "refresh", "observe_only"),
        authority=("L0-retry", "L0-observe"),
        moneyball_score=0.1,
    )
    assert "retry" in deferred
    assert "refresh" in selected
    assert "observe_only" in selected
    assert denied == ()


def test_unknown_action_rejected() -> None:
    with pytest.raises(ValueError, match="unknown L0 action"):
        rank_actions(("mutate_source",), authority=("L0-retry",))


def test_dispatch_falls_back_to_observe() -> None:
    plan = L0Plan(
        incident_id="inc-1",
        actions=("retry",),
        reason="test",
        authority_scope=("L0-retry",),
    )
    decision = dispatch_l0_plan(plan, authority=("L0-observe",), live=False)
    assert decision.selected == ("observe_only",)
    assert decision.live is False
    assert decision.mutates_source is False
    assert "retry" in decision.denied
