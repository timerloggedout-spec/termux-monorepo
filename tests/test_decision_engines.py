#!/usr/bin/env python3
"""Regression coverage for comparative decision engines + Canny gate."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_matrix_policy_comparative():
    de = _load("decision_engines", ROOT / "scripts" / "decision_engines.py")
    m = de.matrix_summary()
    assert m["policy"] == "comparative_only_no_primary"
    assert m["latency_rank"] == "low_value_moneyball"
    assert "laya" in m["engines"]
    assert "kev-4b" in m["engines"]
    assert "canny_pattern" in m["engines"]
    assert "jev" in m["engines"]
    assert "HOLD" in m["invalid_agent_states"]
    assert "laya" in m["families"]
    assert "jev" in m["families"]
    assert "min_score" in m["high_value_dims"]


def test_select_free_only_excludes_hosted():
    de = _load("decision_engines", ROOT / "scripts" / "decision_engines.py")
    ranked = de.select(free_only=True, allow_hosted=False)
    ids = {r["engine"] for r in ranked}
    assert "jev" not in ids
    assert "laya" in ids
    assert "canny_pattern" in ids


def test_select_family_kev_only():
    de = _load("decision_engines", ROOT / "scripts" / "decision_engines.py")
    ranked = de.select(family="kev")
    ids = {r["engine"] for r in ranked}
    assert ids == {"kev-0.8b", "kev-4b", "kev-9b"}


def test_select_hosted_applies_cost_penalty():
    de = _load("decision_engines", ROOT / "scripts" / "decision_engines.py")
    ranked = de.select(free_only=False, allow_hosted=True)
    jev = next(r for r in ranked if r["engine"] == "jev")
    assert "hosted_cost_penalty" in jev["reasons"]
    assert jev["score"] <= 0


def test_select_min_score_drops_hosted_jev():
    de = _load("decision_engines", ROOT / "scripts" / "decision_engines.py")
    ranked = de.select(free_only=False, allow_hosted=True, min_score=1)
    ids = {r["engine"] for r in ranked}
    assert "jev" not in ids
    assert "laya" in ids
    assert all(r["score"] >= 1 for r in ranked)


def test_recommend_pair_keeps_canny_gate():
    de = _load("decision_engines", ROOT / "scripts" / "decision_engines.py")
    pair = de.recommend_pair(domain="route")
    assert pair["policy"] == "comparative_pair_no_primary"
    assert pair["completion_gate"][0]["engine"] == "canny_pattern"
    assert "HOLD" in pair["invalid_agent_states"]
    assert "NEED_EVIDENCE" in pair["valid_gate_decisions"]
    sys1_ids = {r["engine"] for r in pair["system1"]}
    assert "canny_pattern" not in sys1_ids


def test_select_done_domain_prefers_canny():
    de = _load("decision_engines", ROOT / "scripts" / "decision_engines.py")
    ranked = de.select(domain="done", self_host_required=True)
    assert ranked[0]["engine"] == "canny_pattern"


def test_canny_block_on_test_failed():
    canny = _load("canny_completion_gate", ROOT / "scripts" / "canny_completion_gate.py")
    facts = [{"kind": "test_failed", "detail": "pytest exit 1"}]
    result = canny.gate("done", facts=facts, state={"evidence": facts})
    assert result["decision"] == "BLOCK"
    assert result["hard_block"] is True


def test_canny_allow_when_exit_zero():
    canny = _load("canny_completion_gate", ROOT / "scripts" / "canny_completion_gate.py")
    facts = [
        {"kind": "file_changed", "paths": ["scripts/decision_engines.py"]},
        {"kind": "command_exit_nonzero", "exit_code": 0, "cmd": "pytest -q"},
    ]
    result = canny.gate("done", facts=facts, state={"evidence": facts})
    assert result["hard_block"] is False
    assert result["decision"] == "ALLOW"
    assert result["noul_advice"]["advice"] == "relax_allowed"
    assert result["positives"]
    assert result["positives"][0]["kind"] == "file_changed"


def test_canny_file_changed_is_not_hard_block():
    canny = _load("canny_completion_gate", ROOT / "scripts" / "canny_completion_gate.py")
    facts = [{"kind": "file_changed", "paths": ["scripts/canny_completion_gate.py"]}]
    ev = canny.evaluate_facts(facts)
    assert ev["hard_block"] is False
    assert ev["positives"][0]["kind"] == "file_changed"


def test_canny_need_evidence_not_hold():
    canny = _load("canny_completion_gate", ROOT / "scripts" / "canny_completion_gate.py")
    facts: list = []
    result = canny.gate("I am done", facts=facts, state={"evidence": facts})
    assert result["decision"] == "NEED_EVIDENCE"
    assert result["decision"] not in canny.INVALID_AGENT_STATES
    assert result["noul_advice"]["advice"] == "need_evidence"
