from scripts import capability_spine as spine


def candidate(**overrides):
    defaults = {
        "provider": "openrouter",
        "model": "qwen/qwen3-coder:free",
        "capability": "review",
        "declared_capabilities": {"review"},
        "effect": "read_only_analysis",
        "provenance": {
            "declared_source": "llm-peers.yaml/model-success-matrix.yaml",
            "trusted": True,
        },
        "policy_enabled": True,
        "requires_current_sha": False,
        "target_sha": None,
        "current_sha": None,
        "branch_write_confirmed": False,
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
    available = candidate(
        model="meta-llama/llama-3.3-70b-instruct:free",
        openrouter_models={"meta-llama/llama-3.3-70b-instruct:free"},
        limits={
            "openrouter/meta-llama/llama-3.3-70b-instruct:free": {"review": 10}
        },
    )
    assert blocked["eligible"] is False
    assert blocked["availability"] == "blocked"
    decision = spine.decide(capability="review", candidates=[blocked, available])
    assert decision["recommendation"] == available["specialist"]


def test_exhausted_quota_is_not_rankable():
    exhausted = candidate(usage=10)
    assert exhausted["eligible"] is False
    assert exhausted["exclusion"] == "soft budget exhausted (10/10)"


def test_missing_openrouter_catalog_blocks_nonlegacy_model():
    unavailable = candidate(
        openrouter_models=None,
        openrouter_catalog_state="unavailable",
    )
    assert unavailable["eligible"] is False
    assert unavailable["availability"] == "unavailable"


def test_undeclared_capability_is_not_rankable():
    rejected = candidate(declared_capabilities={"triage"})
    assert rejected["eligible"] is False
    assert rejected["exclusion"] == "requested capability is not declared for this specialist"


def test_undeclared_effect_is_not_rankable():
    rejected = candidate(effect="arbitrary_write")
    assert rejected["eligible"] is False
    assert rejected["exclusion"] == "candidate effect is not declared by the capability policy"


def test_untrusted_provenance_is_not_rankable():
    rejected = candidate(provenance={"declared_source": "review-body", "trusted": False})
    assert rejected["eligible"] is False
    assert rejected["exclusion"] == "candidate provenance is not trusted and declared"


def test_disabled_policy_is_not_rankable():
    rejected = candidate(policy_enabled=False)
    assert rejected["eligible"] is False
    assert rejected["exclusion"] == "candidate policy gate is disabled"


def test_stale_current_sha_is_not_rankable():
    rejected = candidate(
        requires_current_sha=True,
        target_sha="a" * 40,
        current_sha="b" * 40,
    )
    assert rejected["eligible"] is False
    assert rejected["exclusion"] == "current-SHA gate is missing or stale"


def test_branch_write_requires_explicit_confirmation():
    rejected = candidate(effect="branch_write")
    assert rejected["eligible"] is False
    assert rejected["exclusion"] == "branch-write effect lacks explicit confirmation"
    confirmed = candidate(effect="branch_write", branch_write_confirmed=True)
    assert confirmed["eligible"] is True


def test_local_outcome_weight_exceeds_external_feature_weight():
    scored = candidate()
    components = scored["score_components"]
    assert components["repository_outcome_weight"] > components["external_inference_weight"]
    assert scored["repository_evidence"]["sample_count"] == 0
    assert scored["repository_evidence"]["confidence"] == 0.2


def test_decision_is_observe_only_and_bounded():
    first = candidate()
    second = candidate(
        model="meta-llama/llama-3.3-70b-instruct:free",
        openrouter_models={"meta-llama/llama-3.3-70b-instruct:free"},
        limits={
            "openrouter/meta-llama/llama-3.3-70b-instruct:free": {"review": 10}
        },
        success_entry={"elo": 1200, "role_suitability": {"review": 1.0}},
    )
    compact = spine.compact_envelope(
        spine.decide(capability="review", candidates=[first, second])
    )
    assert compact["mode"] == "observe"
    assert compact["state"] == "recommended"
    assert compact["recommendation"] is not None
    assert compact["candidates"][0]["effect"] == "read_only_analysis"
    assert compact["candidates"][0]["sha_binding"]["required"] is False


def test_active_mode_is_rejected():
    try:
        spine.decide(capability="review", candidates=[], mode="active")
    except ValueError as error:
        assert "observe mode only" in str(error)
    else:
        raise AssertionError("active mode must be rejected")


def test_validation_status_is_explicit_and_population_is_reported():
    observed = candidate(
        success_entry={},
        declared_capabilities=set(),
    )
    validated = candidate(
        success_entry={
            "elo": 1250,
            "role_suitability": {"review": 1.3},
            "validation_status": "validated",
        }
    )
    assert observed["validation_status"] == "unvalidated"
    assert validated["validation_status"] == "validated"
    decision = spine.decide(capability="review", candidates=[observed, validated])
    assert decision["population"]["candidate_count"] == 2
    assert decision["population"]["unvalidated_count"] == 1
    assert decision["population"]["validated_count"] == 1
    compact = spine.compact_envelope(decision)
    assert compact["population"]["validated_count"] == 1
    assert "validation_status" in compact["candidates"][0]



def test_capability_surface_join_is_observational_and_preserves_authority():
    surfaces = [
        {
            "kind": "mcp",
            "id": "github-mcp",
            "provider": "openrouter",
            "model": "qwen/qwen3-coder:free",
            "capabilities": ["repository_read", "issue_query"],
            "availability": "available",
            "authority": "read/query",
            "evidence_refs": ["workflow://run/123"],
            "observed_at": "2026-09-18T20:00:00Z",
            "freshness": "current",
        }
    ]
    matched = spine.match_capability_surfaces(
        "openrouter", "qwen/qwen3-coder:free", surfaces
    )
    assert matched[0]["kind"] == "mcp"
    candidate = spine.make_candidate(
        provider="openrouter",
        model="qwen/qwen3-coder:free",
        capability="review",
        declared_capabilities={"review"},
        effect="read_only_analysis",
        provenance={"declared_source": "test", "trusted": True},
        policy_enabled=True,
        requires_current_sha=False,
        target_sha=None,
        current_sha=None,
        branch_write_confirmed=False,
        has_provider=True,
        openrouter_models={"qwen/qwen3-coder:free"},
        openrouter_catalog_state="live",
        limits={"openrouter/qwen/qwen3-coder:free": {"review": 1}},
        usage=0,
        success_entry={},
        surface_evidence=matched,
    )
    assert candidate["eligible"] is True
    assert candidate["capability_surfaces"][0]["authority"] == "read/query"
    assert candidate["capability"] == "review"
    assert "repository_write" not in candidate["capability_surfaces"][0]["capabilities"]


def test_capability_surface_catalog_loader_is_fail_soft(tmp_path):
    valid = tmp_path / "surfaces.json"
    valid.write_text(json.dumps({
        "schema": "capability-surfaces/v1",
        "surfaces": [{
            "kind": "skill",
            "id": "adaptive-wait",
            "capabilities": ["wait", "recheck"],
            "freshness": "current",
        }],
    }))
    rows = spine.load_capability_surface_catalog(str(valid))
    assert rows[0]["kind"] == "skill"
    assert rows[0]["authority"] == "unknown"
    broken = tmp_path / "broken.json"
    broken.write_text("{not-json")
    assert spine.load_capability_surface_catalog(str(broken)) == []
