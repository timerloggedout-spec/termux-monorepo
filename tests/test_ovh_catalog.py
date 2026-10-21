import pytest

from scripts import provider_catalog_protocols as catalog

URL = "https://catalog.endpoints.ai.ovh.net/rest/v1/models_v2"


def model(**updates):
    item = {
        "id": "vendor/model-qualified", "name": "Display Name", "available": True,
        "metadata": {"aliases": ["alias/model", "another"],
                     "model_specs": {"capabilities": {"input_modality": ["text", "image"], "output_modality": ["text"]}},
                     "usage_information": {"pricing": [{"price": 0.12, "price_unit": "million_input_tokens"}],
                                           "rate_limit": {"calls": 3}}},
    }
    item.update(updates)
    return item


def test_ovh_fixed_endpoint_exact_id_safe_metadata_and_availability():
    assert "ovhcloud" in catalog.PROVIDERS
    assert catalog.endpoint("ovhcloud") == URL
    assert catalog.SECRET_ENV["ovhcloud"] == ("OVHCLOUD_API_KEY",)
    item = model()
    rows = catalog.normalize_models("ovhcloud", {"data": [item]})
    row = rows[0]
    assert row["id"] == "vendor/model-qualified"
    assert row["id"] not in item["metadata"]["aliases"]
    assert row["active"] is True
    assert row["provider_capabilities"] == item["metadata"]["model_specs"]["capabilities"]
    assert row["raw_pricing_metadata"] == item["metadata"]["usage_information"]["pricing"]
    assert row["pricing"] == {} and row["pricing_classification"] == "unknown"
    assert row["context_length"] is None


def test_ovh_poll_uses_single_fixed_public_call_with_no_auth_or_pagination():
    calls = []
    payload = {"data": [model(available=False)]}

    def get_json(url, token):
        calls.append((url, token))
        return payload, {"x-catalog": "ok"}

    rows, headers = catalog.poll("ovhcloud", "provided-inference-token-must-not-be-sent", get_json)
    assert calls == [(URL, None)]
    assert headers == {"x-catalog": "ok"}
    assert len(rows) == 1 and rows[0]["active"] is False


@pytest.mark.parametrize("body", [
    [], {}, {"data": {}}, {"data": ["not an object"]},
    {"data": [dict(model(), available="true")]},
])
def test_ovh_invalid_shapes_fail_closed(body):
    with pytest.raises(ValueError):
        catalog.normalize_models("ovhcloud", body)


def test_ovh_request_errors_propagate_without_retry_or_inference():
    calls = []

    def get_json(url, token):
        calls.append((url, token))
        raise RuntimeError("catalog unavailable")

    with pytest.raises(RuntimeError, match="catalog unavailable"):
        catalog.poll("ovhcloud", "token", get_json)
    assert calls == [(URL, None)]
