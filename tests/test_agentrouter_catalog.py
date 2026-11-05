from unittest.mock import patch

from scripts import provider_model_catalog
from scripts import provider_quota_managers


def test_agentrouter_catalog_is_authenticated_dynamic_and_not_admission():
    assert provider_model_catalog.ENDPOINTS["agentrouter"] == "https://co.agentrouter.org/v1/models"
    assert provider_model_catalog.SECRETS["agentrouter"] == "AGENTROUTER_API_KEY"

    payload = {
        "data": [
            {"id": "account-pool/model-alpha", "name": "Model Alpha"},
            {"id": "account-pool/model-beta", "name": "Model Beta"},
        ]
    }
    with patch.object(provider_model_catalog, "get_json", return_value=(payload, {})) as request:
        rows, headers = provider_model_catalog.poll("agentrouter", "credential-canary")

    request.assert_called_once_with("https://co.agentrouter.org/v1/models", "credential-canary")
    assert headers == {}
    assert [row["id"] for row in rows] == ["account-pool/model-alpha", "account-pool/model-beta"]
    assert all(row["provider"] == "agentrouter" for row in rows)
    assert all(row["access_classification"] == "catalog_pricing_only" for row in rows)
    assert all(row["pricing_classification"] == "unknown" for row in rows)


def test_agentrouter_secret_resolution_uses_names_only():
    with patch.dict("os.environ", {"AGENTROUTER_API_KEY": "credential-canary"}, clear=True):
        token, env_name = provider_model_catalog.resolve_secret("agentrouter")
    assert token == "credential-canary"
    assert env_name == "AGENTROUTER_API_KEY"


def test_agentrouter_quota_stays_unknown_until_documented_account_signal_exists():
    managers = provider_quota_managers.load_managers()
    assert managers["agentrouter"]["status"] == "unsupported"
    assert managers["agentrouter"]["reset"] == "unknown"

    status = provider_quota_managers.catalog_quota_status(
        "agentrouter",
        {"x-ratelimit-remaining-requests": "999"},
        observed_at="2026-11-05T00:00:00Z",
        source="https://co.agentrouter.org/v1/models",
    )
    assert status == {"status": "unknown", "manager_status": "unsupported"}

    # No public or guessed counter may be promoted to a private observation.
    try:
        provider_quota_managers.normalize_observation(
            "agentrouter",
            {"x-ratelimit-remaining-requests": "999"},
            observed_at="2026-11-05T00:00:00Z",
            scope="key",
        )
    except ValueError as exc:
        assert str(exc) == "provider has no implemented passive adapter"
    else:
        raise AssertionError("AgentRouter quota adapter must fail closed")
