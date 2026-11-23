from __future__ import annotations

import os

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
