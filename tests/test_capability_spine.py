from scripts import capability_spine as spine


def candidate(**overrides):
    defaults = {
        "provider": "openrouter",
        "model": "qwen/qwen3-coder:free",
        "capability": "review",
        "has_provider": True,
        "openrouter_models": {"qwen/qwen3-coder:free"},
        "openrouter_catalog_state": "live",
        "limits": {"openrouter/qwen/qwen3-coder:free": {"review": 10}},
        "usage": 2,
        "success_entry": {"elo": 1250, "role_suitability": {"review": 1.3}},
    }
    defaults.update(overrides)
    return spine.make_candidate(**defaults)


def test_unavailable_provider_is_not_rankable():
    blocked = candidate(has_provider=False)
    available = candidate(model="meta-llama/llama-3.3-70b-instruct:free",
                          openrouter_models={"meta-llama/llama-3.3-70b-instruct:free"},
                          limits={"openrouter/meta-llama/llama-3.3-70b-instruct:free": {"review": 10}})
    assert blocked["eligible"] is False
    assert blocked["availability"] == "blocked"
    decision = spine.decide(capability="review", candidates=[blocked, available])
    assert decision["recommendation"] == available["specialist"]


def test_exhausted_quota_is_not_rankable():
    exhausted = candidate(usage=10)
    assert exhausted["eligible"] is False
    assert exhausted["exclusion"] == "soft budget exhausted (10/10)"


def test_missing_openrouter_catalog_blocks_nonlegacy_model():
    unavailable = candidate(openrouter_models=None, openrouter_catalog_state="unavailable")
    assert unavailable["eligible"] is False
    assert unavailable["availability"] == "unavailable"


def test_local_outcome_weight_exceeds_external_feature_weight():
    scored = candidate()
    components = scored["score_components"]
    assert components["repository_outcome_weight"] > components["external_inference_weight"]
    assert scored["repository_evidence"]["sample_count"] == 0
    assert scored["repository_evidence"]["confidence"] == 0.2


def test_decision_is_observe_only_and_bounded():
    first = candidate()
    second = candidate(model="meta-llama/llama-3.3-70b-instruct:free",
                       openrouter_models={"meta-llama/llama-3.3-70b-instruct:free"},
                       limits={"openrouter/meta-llama/llama-3.3-70b-instruct:free": {"review": 10}},
                       success_entry={"elo": 1200, "role_suitability": {"review": 1.0}})
    compact = spine.compact_envelope(spine.decide(capability="review", candidates=[first, second]))
    assert compact["mode"] == "observe"
    assert compact["state"] == "recommended"
    assert compact["recommendation"] is not None
    assert "effect" not in compact["candidates"][0]


def test_active_mode_is_rejected():
    try:
        spine.decide(capability="review", candidates=[], mode="active")
    except ValueError as error:
        assert "observe mode only" in str(error)
    else:
        raise AssertionError("active mode must be rejected")
