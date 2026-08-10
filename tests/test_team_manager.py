import os
import tempfile
import pytest
from pathlib import Path
from src.team_manager import AgentCandidate, TeamRoster, MoneyBallScout, BettingArena

def test_agent_candidate_serialization():
    agent = AgentCandidate(
        id="test-id",
        name="Test Agent",
        role="Engineer",
        elo=1200.0,
        skills=["python"],
        wallet=100.0,
        tools=["ast-grep"]
    )
    d = agent.to_dict()
    assert d["id"] == "test-id"
    assert d["name"] == "Test Agent"
    assert d["role"] == "Engineer"
    assert d["elo"] == 1200.0
    assert d["skills"] == ["python"]
    assert d["wallet"] == 100.0
    assert d["tools"] == ["ast-grep"]

    restored = AgentCandidate.from_dict(d)
    assert restored.id == "test-id"
    assert restored.name == "Test Agent"
    assert restored.elo == 1200.0


def test_team_roster_initialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "roster.json"
        # Since it does not exist, it should initialize defaults
        roster = TeamRoster(filepath=tmp_path)
        assert len(roster.get_all_candidates()) > 0

        # Verify defaults are in place (CTO, CFO, Engineers, etc.)
        all_roles = [c.role for c in roster.get_all_candidates()]
        assert "CTO" in all_roles
        assert "CFO" in all_roles
        assert "Engineer" in all_roles
        assert "l337 4@xπ$" in all_roles

        # Retrieve active team
        active_team = roster.get_active_team()
        assert len(active_team) > 0


def test_moneyball_scout_cull_and_clone():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "roster.json"
        roster = TeamRoster(filepath=tmp_path)

        # Force a small, controllable roster of 5 agents
        roster.candidates = {
            "a1": AgentCandidate(id="a1", name="Agent 1", role="Engineer", elo=1300.0, is_active=True),
            "a2": AgentCandidate(id="a2", name="Agent 2", role="Engineer", elo=1200.0, is_active=True),
            "a3": AgentCandidate(id="a3", name="Agent 3", role="Engineer", elo=1100.0, is_active=True),
            "a4": AgentCandidate(id="a4", name="Agent 4", role="Engineer", elo=1000.0, is_active=True),
            "a5": AgentCandidate(id="a5", name="Agent 5", role="Engineer", elo=900.0, is_active=True),
        }
        roster.save()

        scout = MoneyBallScout(roster)
        # Cull bottom 20% (1 agent: a5) and clone top 20% (1 agent: a1)
        culled_ids, cloned_ids = scout.rotate_and_cull(bottom_pct=0.20, top_pct=0.20)

        assert "a5" in culled_ids
        assert not roster.candidates["a5"].is_active

        assert len(cloned_ids) == 1
        clone_id = cloned_ids[0]
        assert clone_id.startswith("a1-clone-v1")
        assert roster.candidates[clone_id].is_active
        assert roster.candidates[clone_id].parent_id == "a1"
        assert roster.candidates[clone_id].mutation_count == 1


def test_moneyball_evaluate_role_necessity():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "roster.json"
        roster = TeamRoster(filepath=tmp_path)
        scout = MoneyBallScout(roster)

        # Simulating failed tasks related to security
        failed_tasks = [
            {"instructions": "Fix privilege settings", "error": "Access denied error"},
            {"instructions": "Secure configuration directory", "error": "Security check fail"}
        ]
        specialist_id = scout.evaluate_role_necessity(failed_tasks)
        assert specialist_id is not None
        specialist = roster.candidates[specialist_id]
        assert specialist.role == "l337 4@xπ$"
        assert "security-audit" in specialist.skills


def test_betting_arena():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "roster.json"
        roster = TeamRoster(filepath=tmp_path)

        # Setup standard participants
        roster.candidates = {
            "agent-x": AgentCandidate(id="agent-x", name="Agent X", role="Engineer", wallet=100.0, is_active=True),
            "spec-y": AgentCandidate(id="spec-y", name="Spec Y", role="Researcher", wallet=50.0, is_active=True),
            "spec-z": AgentCandidate(id="spec-z", name="Spec Z", role="Script Kiddies", wallet=50.0, is_active=True)
        }
        roster.save()

        arena = BettingArena(roster)

        # 1. Place bid
        assert arena.place_bid("agent-x", "task-100", 20.0)
        assert roster.candidates["agent-x"].wallet == 80.0
        assert arena.active_bids["task-100"] == {"agent_id": "agent-x", "amount": 20.0}

        # 2. Place spectator bets (spec-y bets success, spec-z bets failure)
        assert arena.place_spectator_bet("spec-y", "task-100", "success", 10.0)
        assert arena.place_spectator_bet("spec-z", "task-100", "failure", 20.0)

        assert roster.candidates["spec-y"].wallet == 40.0
        assert roster.candidates["spec-z"].wallet == 30.0

        # 3. Resolve bets as success
        payouts = arena.resolve_bets("task-100", "PASS")

        # Agent payout: bid returned + 1.5x bonus = 20.0 + 30.0 = 50.0
        assert payouts["agent_payouts"]["agent-x"] == 50.0
        assert roster.candidates["agent-x"].wallet == 130.0
        assert roster.candidates["agent-x"].successes == 1

        # Spectator payout: total pool of spectator bets = 10.0 + 20.0 = 30.0
        # Winner was spec-y (bet 10.0 on success). Total winning bet amount was 10.0.
        # So spec-y gets 100% of the total spectator pool = 30.0.
        assert payouts["spectator_payouts"]["spec-y"] == 30.0
        assert roster.candidates["spec-y"].wallet == 70.0
        assert "spec-z" not in payouts["spectator_payouts"]
        assert roster.candidates["spec-z"].wallet == 30.0
