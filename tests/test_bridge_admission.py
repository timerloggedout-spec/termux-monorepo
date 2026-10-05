from datetime import datetime, timezone

from scripts.termux.bridge_admission import classify


NOW = datetime(2026, 10, 5, 1, 20, tzinfo=timezone.utc)


def test_seeded_unknown_manifest_is_admission_failure():
    verdict = classify(
        {
            "status": "unknown",
            "endpoint": "example.invalid",
            "port": 46627,
            "ssh_user": None,
            "expires_at": None,
            "stale_reason": "no live channel",
        },
        now=NOW,
    )
    assert verdict["admitted"] is False
    assert verdict["reason"] == "status_not_active"
    assert "ssh_user" in verdict["missing"]
    assert "expires_at" in verdict["missing"]


def test_active_manifest_is_admitted():
    verdict = classify(
        {
            "status": "active",
            "endpoint": "example.invalid",
            "port": 22,
            "ssh_user": "u0",
            "expires_at": "2026-10-05T02:00:00Z",
        },
        now=NOW,
    )
    assert verdict["admitted"] is True
    assert verdict["reason"] == "admitted"


def test_expired_active_manifest_is_not_admitted():
    verdict = classify(
        {
            "status": "active",
            "endpoint": "example.invalid",
            "port": 22,
            "ssh_user": "u0",
            "expires_at": "2026-10-05T00:00:00Z",
        },
        now=NOW,
    )
    assert verdict["admitted"] is False
    assert verdict["reason"] == "expired"
