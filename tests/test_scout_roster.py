from scripts.scout_roster import build


def test_free_catalog_model_becomes_candidate_without_hardcoding_identity():
    result = build({
        "schema": "provider-model-catalog/v4",
        "observed_at": "2026-08-27T00:00:00Z",
        "models": [{
            "provider": "new-provider",
            "id": "new-free-model",
            "name": "New Free Model",
            "pricing_classification": "free_zero_price",
            "access_classification": "catalog_pricing_only",
            "free_suffix": False,
            "context_length": 1234,
            "max_output_tokens": 567,
            "raw_source": "new-provider:/v1/models",
        }],
        "errors": [],
    })
    assert result["candidates"][0]["provider"] == "new-provider"
    assert result["candidates"][0]["model"] == "new-free-model"
    assert result["candidates"][0]["status"] == "candidate"


def test_trial_candidate_retains_provenance():
    result = build({
        "schema": "provider-model-catalog/v4",
        "observed_at": "2026-08-27T00:00:00Z",
        "models": [{
            "provider": "felo",
            "id": "trial-model",
            "pricing_classification": "unknown",
            "access_classification": "free_trial",
            "access_source": "documented-model-page",
            "free_suffix": False,
        }],
        "errors": [],
    })
    row = result["candidates"][0]
    assert row["status"] == "candidate"
    assert row["access_source"] == "documented-model-page"


def test_paid_model_is_observed_not_automatically_admitted():
    result = build({
        "schema": "provider-model-catalog/v4",
        "observed_at": "2026-08-27T00:00:00Z",
        "models": [{
            "provider": "provider",
            "id": "paid-model",
            "pricing_classification": "paid",
            "access_classification": "catalog_pricing_only",
            "free_suffix": False,
        }],
        "errors": [],
    })
    assert result["candidates"][0]["status"] == "observed"
