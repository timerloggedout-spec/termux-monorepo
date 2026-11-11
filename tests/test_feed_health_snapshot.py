from scripts.dispatch.feed_health_snapshot import arm_state, build_snapshot


def test_census_api_evidence_uses_explicit_name_and_legacy_alias():
    state = arm_state({
        "provider": "gemini",
        "census_api_verified": True,
        "live_verified": False,
        "census": {"verdict": "free"},
    })
    assert state["census_api_verified"] is True
    # Kept only as a compatibility alias for existing snapshot consumers.
    assert state["live_verified"] is True


def test_legacy_feed_field_is_read_as_census_evidence_only():
    state = arm_state({
        "provider": "gemini",
        "live_verified": True,
        "census": {"verdict": "free"},
    })
    assert state["census_api_verified"] is True
    assert state["live_verified"] is True


def test_census_change_changes_snapshot_hash():
    feed = {
        "schema": "quota.swarm-feed/v1",
        "generated_at": "2026-11-10T00:00:00Z",
        "providers": [{"provider": "gemini", "census_api_verified": False}],
    }
    before = build_snapshot(feed, "2026-11-10T00:01:00Z")
    feed["providers"][0]["census_api_verified"] = True
    after = build_snapshot(feed, "2026-11-10T00:02:00Z")
    assert before["state_hash"] != after["state_hash"]
    assert after["arms"][0]["census_api_verified"] is True
