from scripts import orbit_arbitration as orbit


def candidate(provider="openrouter", model="qwen/qwen3-coder:free", **overrides):
    item = {
        "identity": {"kind": "provider_endpoint", "provider": provider, "model": model},
        "hard_gates": {
            "capability": True,
            "effect": True,
            "provenance": True,
            "policy": True,
            "endpoint": True,
            "credential": True,
            "authentication": True,
            "catalog_freshness": True,
            "health": True,
            "quota": True,
            "data_classification": True,
            "current_sha": True,
            "execution_authority": True,
        },
        "benefit": {
            "capability_fit": 0.9,
            "repository_outcome": 0.8,
            "task_suitability": 0.9,
            "integration_value": 0.8,
        },
        "risk_cost": {
            "uncertainty": 0.1,
            "failure_risk": 0.1,
            "latency_cost": 0.2,
            "quota_cost": 0.1,
            "context_cost": 0.2,
            "retry_cost": 0.1,
            "conflict_cost": 0.1,
            "human_intervention_cost": 0.1,
        },
        "evidence_refs": ["actions://run/123"],
    }
    item.update(overrides)
    return item


def test_selects_candidate_when_benefit_margin_clears_threshold():
    decision = orbit.arbitrate([candidate()], threshold=0.1)
    assert decision["schema"] == "orbit-decision/v1"
    assert decision["decision"] == "SELECT"
    assert decision["selected"]["provider"] == "openrouter"
    assert decision["candidates"][0]["benefit_accumulator"] > decision["candidates"][0]["risk_cost_accumulator"]


def test_hard_gate_failure_vetoes_candidate_before_scoring():
    item = candidate()
    item["hard_gates"]["execution_authority"] = False
    decision = orbit.arbitrate([item])
    assert decision["decision"] == "VETO"
    assert decision["selected"] is None
    assert decision["candidates"][0]["decision"] == "VETO"


def test_unknown_endpoint_or_catalog_evidence_defers_candidate():
    item = candidate()
    item["hard_gates"]["endpoint"] = None
    decision = orbit.arbitrate([item])
    assert decision["decision"] == "DEFER"
    assert decision["selected"] is None


def test_catalog_only_endpoint_cannot_be_selected():
    item = candidate()
    item["hard_gates"]["endpoint"] = False
    item["hard_gates"]["authentication"] = None
    item["evidence_state"] = "catalog_only"
    decision = orbit.arbitrate([item])
    assert decision["decision"] == "VETO"
    assert decision["selected"] is None


def test_low_benefit_margin_defers():
    item = candidate(
        benefit={"capability_fit": 0.2, "repository_outcome": 0.2, "task_suitability": 0.2, "integration_value": 0.2},
        risk_cost={"uncertainty": 0.4, "failure_risk": 0.4, "latency_cost": 0.4, "quota_cost": 0.4,
                   "context_cost": 0.4, "retry_cost": 0.4, "conflict_cost": 0.4, "human_intervention_cost": 0.4},
    )
    decision = orbit.arbitrate([item], threshold=0.1)
    assert decision["decision"] == "DEFER"
    assert decision["selected"] is None


def test_tied_top_candidates_defer_instead_of_arbitrary_selection():
    first = candidate(provider="alpha", model="model-a")
    second = candidate(provider="beta", model="model-b")
    decision = orbit.arbitrate([first, second])
    assert decision["decision"] == "DEFER"
    assert decision["selected"] is None
    assert decision["reason"] == "top candidates have indistinguishable benefit-risk margins"


def test_duplicate_endpoint_identity_is_vetoed():
    first = candidate()
    second = candidate()
    decision = orbit.arbitrate([first, second])
    assert decision["decision"] == "VETO"
    assert all(item["decision"] == "VETO" for item in decision["candidates"])


def test_missing_benefit_or_risk_evidence_is_not_coerced_to_zero():
    item = candidate()
    item["benefit"]["repository_outcome"] = None
    decision = orbit.arbitrate([item])
    assert decision["decision"] == "DEFER"
    assert decision["candidates"][0]["benefit_accumulator"] is None


def test_candidate_population_is_bounded_and_truncation_is_visible():
    items = [candidate(provider=f"p{i}", model=f"m{i}") for i in range(140)]
    decision = orbit.arbitrate(items, max_candidates=128)
    assert len(decision["candidates"]) == 128
    assert decision["candidate_population_truncated"] is True
    assert decision["decision"] == "DEFER"
