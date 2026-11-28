import math
from decimal import Decimal
import pytest
from scripts import provider_extension_catalogs as ext
from scripts import provider_model_catalog as catalog
from scripts import provider_catalog_protocols as protocols
from llm_api_hub.server import provider_extensions as runtime


def test_endpoint_secret_and_public_catalog_definitions_match_actual_transports():
    assert set(ext.ENDPOINTS) == {"unorouter", "routeway", "requesty", "xkiro", "sealion", "deepinfra", "novita", "friendli", "baseten", "agentrouter"}
    assert ext.ENDPOINTS == runtime.CATALOG_ENDPOINTS
    assert all(catalog.ENDPOINTS[p] == url for p, url in ext.ENDPOINTS.items())
    assert all(catalog.SECRETS[p] == runtime.CATALOG_SECRET_ENV[p] for p in ext.ENDPOINTS)
    assert "typhoon" not in catalog.ENDPOINTS and "xfyun" not in catalog.ENDPOINTS
    assert set(ext.ENDPOINTS) & catalog.PUBLIC_CATALOGS == {"routeway", "requesty", "xkiro"}


def tier(inp=0, out=0, threshold=0, **kw):
    return {"prompt_tokens_threshold": threshold, "input_price": inp, "output_price": out, **kw}


def test_requesty_uses_documented_array_and_all_tiers_and_optional_charge_fields():
    assert ext._pricing({"pricing": [tier(), tier(threshold=1000)]}, "requesty") == ({"prompt": 0, "completion": 0}, "free_zero_price")
    assert ext._pricing({"pricing": [tier(), tier(out=2e-9, threshold=1000)]}, "requesty") == ({"prompt": Decimal(0), "completion": Decimal("2e-9")}, "paid")
    assert ext._pricing({"pricing": [tier(caching_price=1)]}, "requesty")[1] == "paid"
    assert ext._pricing({"pricing": [tier()], "input_price": 1}, "requesty")[1] == "unknown"
    assert ext._pricing({"pricing": [tier()], "input_price": 0}, "requesty")[1] == "free_zero_price"
    # Obsolete invented {tiers:...} and flat-only prices cannot prove zero cost.
    assert ext._pricing({"pricing": {"tiers": [tier()]}}, "requesty")[1] == "unknown"
    assert ext._pricing({"input_price": 0, "output_price": 0}, "requesty")[1] == "unknown"


@pytest.mark.parametrize("bad", [True, -1, math.nan, math.inf, "0", None])
def test_requesty_invalid_numeric_prices_are_unknown(bad):
    assert ext._pricing({"pricing": [tier(out=bad)]}, "requesty")[1] == "unknown"


@pytest.mark.parametrize("tiers", [[], [None], [tier(threshold=10)], [tier(), tier()], [tier(), tier(threshold=-1)], [tier(threshold=False)]])
def test_requesty_bad_thresholds_and_shapes_are_unknown(tiers):
    assert ext._pricing({"pricing": tiers}, "requesty")[1] == "unknown"


def route_price(inp=0, out=0):
    return {"input": {"unit": "1M tokens", "price_per_million_t": inp}, "output": {"unit": "1M tokens", "price_per_million_t": out}}


def test_routeway_nested_per_million_rates_and_cache_prices():
    assert ext._pricing({"pricing": route_price(0, 2.5)}, "routeway") == ({"prompt": Decimal(0), "completion": Decimal("0.0000025")}, "paid")
    assert ext._pricing({"pricing": route_price()}, "routeway")[1] == "free_zero_price"
    p = route_price()
    p["caching"] = {"read": {"unit": "1M tokens", "price_per_million_t": 1}}
    assert ext._pricing({"pricing": p}, "routeway")[1] == "paid"
    p["input"]["unit"] = "tokens"
    assert ext._pricing({"pricing": p}, "routeway")[1] == "unknown"
    result = ext._pricing({"pricing": route_price(Decimal("1e-1000000"), 0)}, "routeway")
    assert result[1] == "paid"
    assert result[0]["prompt"] == Decimal((0, (1,), -1000006))


@pytest.mark.parametrize("bad", [True, -1, math.nan, math.inf, "0", None])
def test_routeway_invalid_numeric_prices_are_unknown(bad):
    assert ext._pricing({"pricing": route_price(bad)}, "routeway")[1] == "unknown"


def test_poller_uses_existing_transport_and_keeps_free_access_separate_from_price():
    seen = []
    def get(url, token):
        seen.append((url, token))
        return {"data": [{"id": "vendor/model", "access_tier": "free"}]}, {"retry-after": "1"}
    rows, headers = ext.poll("xkiro", "synthetic", get)
    assert seen == [(ext.ENDPOINTS["xkiro"], "synthetic")]
    assert headers == {"retry-after": "1"}
    row = rows[0]
    assert row["pricing_classification"] == "unknown"
    assert row["account_free_tier_candidate"] is True and row["quota_status"] == "unknown"
    assert row["access_classification"] == "catalog_pricing_only"
    assert row["raw_source"] == "xkiro:/v1/models"
    assert row["readiness"] == "unknown"


def test_catalog_dispatch_uses_annotated_official_schema(monkeypatch):
    def get(url, token):
        return {"data": [{"id": "nvidia/model", "pricing": [tier()], "context_window": 4096}]}, {}
    monkeypatch.setattr(catalog, "get_json", get)
    row = catalog.poll("requesty", "synthetic")[0][0]
    assert row["pricing_classification"] == "free_zero_price"
    assert row["context_length"] == 4096
    assert "quota_remaining" not in row and "runtime_eligible" not in row


@pytest.mark.parametrize("payload", [None, [], {}, {"data": None}])
def test_malformed_catalog_shapes_fail_closed(payload):
    with pytest.raises(ValueError):
        ext.poll("routeway", "", lambda *a: (payload, {}))


def test_suffix_does_not_invent_price_and_routeway_preserves_bounded_metadata():
    item = {"id": "model:free", "available": True, "capabilities": {"tools": True, "secret": "private"}}
    row = ext.poll("routeway", "", lambda *a: ({"data": [item]}, {}))[0][0]
    assert row["pricing_classification"] == "unknown" and row["free_suffix"] is True
    assert row["active"] is True and row["capabilities"] == {"tools": True}
    for p in ("unorouter", "sealion"):
        assert ext._pricing({"pricing": {}}, p) == ({}, "unknown")


def test_missing_keys_report_canonical_secret_name_only(monkeypatch):
    for provider, key in ext.SECRETS.items():
        monkeypatch.delenv(key, raising=False)
        value, env_name = catalog.resolve_secret(provider)
        assert value is None and env_name == key


def test_row_diagnostics_preserve_good_extension_rows_and_readiness_is_unknown():
    rows, _ = ext.poll("routeway", "", lambda *a: ({"data": [None, {"id": "good"}, {"id": "bad\n"}]}, {}))
    assert [row["id"] for row in rows] == ["good"]
    assert rows[0]["readiness"] == "unknown"
    assert rows.diagnostics == [
        {"row_index": 0, "error": "invalid_model"},
        {"row_index": 2, "error": "invalid_model"},
    ]


def test_official_catalog_diagnostics_keep_ovh_capability_and_pricing_metadata():
    rows = protocols.normalize_models("ovhcloud", {"data": [
        None,
        {"id": "available-model", "available": True, "metadata": {
            "model_specs": {"capabilities": {"chat": True}},
            "usage_information": {"pricing": {"token": "opaque"}},
        }},
        {"id": "bad", "available": "unknown"},
    ]})
    assert len(rows) == 1
    assert rows[0]["readiness"] == "unknown"
    assert rows[0]["active"] is True
    assert rows[0]["provider_capabilities"] == {"chat": True}
    assert rows[0]["raw_pricing_metadata"] == {"token": "opaque"}
    assert rows.diagnostics == [
        {"row_index": 0, "error": "invalid_model"},
        {"row_index": 2, "error": "invalid_model"},
    ]


def test_exact_decimal_serializer_emits_original_json_number_token():
    token = catalog.provider_catalog_json.ExactDecimal("1e-10000")
    serialized = catalog.provider_catalog_json.dumps_exact({"prompt": token})
    assert '"prompt": 1e-10000' in serialized


def test_agentrouter_is_catalog_only_not_an_admitted_inference_transport():
    assert ext.ENDPOINTS["agentrouter"] == "https://co.agentrouter.org/v1/models"
    assert ext.SECRETS["agentrouter"] == "AGENTROUTER_API_KEY"
    assert runtime.CATALOG_SECRET_ENV["agentrouter"] == "AGENTROUTER_API_KEY"
    assert "agentrouter" not in runtime.ENDPOINTS
