from __future__ import annotations

import json
from pathlib import Path

from scripts import provider_model_catalog as catalog


def test_canonical_catalog_polls_loopback_puter_models_with_x_api_key(monkeypatch):
    monkeypatch.setenv("PUTER_POOL_BASE_URL", "http://127.0.0.1:4321")
    calls = []

    def fake_get_json(url, token=None, header_name="Authorization"):
        calls.append((url, token, header_name))
        return {"data": [{"id": "model-a"}, {"id": "model-a"}, {"id": "model-b"}]}, {"x-request-id": "synthetic"}

    monkeypatch.setattr(catalog, "get_json", fake_get_json)
    rows, headers = catalog.poll("puter_pool", "local-key")
    assert calls == [("http://127.0.0.1:4321/v1/models", "local-key", "x-api-key")]
    assert [row["id"] for row in rows] == ["model-a", "model-b"]
    assert all(row["provider"] == "puter_pool" for row in rows)
    assert all(row["provider_id"] == "g4f.puter" for row in rows)
    assert all(row["provider_family"] == "g4f/Puter" for row in rows)
    assert all(row["pricing_classification"] == "unknown" for row in rows)
    assert headers["x-request-id"] == "synthetic"


def test_puter_pool_is_a_public_catalog_with_optional_credential():
    assert "puter_pool" in catalog.PUBLIC_CATALOGS
    assert catalog.SECRETS["puter_pool"] == "PUTER_POOL_API_KEY"


def test_existing_g4f_puter_datastore_points_to_pool_adapters():
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "data/g4f-working/providers.json").read_text())
    puter = next(row for row in registry["providers"] if row["id"] == "Puter")
    assert puter["pool_datastore_id"] == "g4f.puter"
    assert puter["pool_source_repository"] == "timerloggedout-spec/puter-pool_fork"
    assert puter["catalog_adapter"] == "scripts/provider_model_catalog.py:puter_pool"
    assert puter["runtime_adapter"] == "llm_api_hub/server/research_providers.py:puter_pool"
    assert puter["runtime_eligible"] is False
    assert puter["quota_state"] == "unknown_until_provider_authoritative_signal"
