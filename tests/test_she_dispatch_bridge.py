"""SHE P0.5 — dispatch_l0_plan dry-run wire into Actions bridge."""
from __future__ import annotations

from she.recovery.actions_bridge import dispatch_then_bridge
from she.recovery.l0 import L0Plan


def _wf_plan() -> L0Plan:
    return L0Plan(
        incident_id="inc-p05",
        actions=("retry", "refresh", "restart"),
        reason="p0.5 canary",
        authority_scope=("L0-retry", "L0-observe"),
        metadata={
            "classification": "workflow-failure",
            "fingerprint": "gha:77",
            "source": "actions",
        },
    )


def test_dispatch_then_bridge_dry_run_default(monkeypatch) -> None:
    monkeypatch.delenv("SHE_L0_LIVE", raising=False)
    result = dispatch_then_bridge(
        _wf_plan(),
        owner="timerloggedout-spec",
        repo="termux-monorepo",
        run_id=77,
        workflow_id="repo-gate.yml",
    )
    assert result.executed is False
    assert result.mutates_source is False
    assert result.dispatch is not None
    assert result.dispatch["live"] is False
    assert "retry" in result.dispatch["selected"]
    paths = [c.path for c in result.commands if c.path]
    assert any("rerun-failed-jobs" in p for p in paths)
    assert all(o.get("dry_run") for o in result.outcomes)


def test_observe_authority_does_not_plan_rerun() -> None:
    result = dispatch_then_bridge(
        _wf_plan(),
        owner="o",
        repo="r",
        run_id=77,
        authority=("L0-observe",),
        force_live=False,
    )
    assert result.dispatch["selected"] == ["observe_only"]
    assert "retry" in result.dispatch["denied"]
    assert not any(c.method == "POST" and c.path for c in result.commands)
    assert result.executed is False


def test_low_moneyball_defers_retry_commands() -> None:
    result = dispatch_then_bridge(
        _wf_plan(),
        owner="o",
        repo="r",
        run_id=77,
        authority=("L0-retry", "L0-observe"),
        moneyball_score=0.1,
        force_live=False,
    )
    selected = set(result.dispatch["selected"])
    assert "retry" not in selected
    assert "refresh" in selected
    assert not any("rerun-failed-jobs" in (c.path or "") for c in result.commands)
    assert result.executed is False
    assert result.mutates_source is False
