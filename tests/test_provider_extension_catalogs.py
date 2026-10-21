import math
import pytest
from scripts import provider_extension_catalogs as ext
from scripts import provider_model_catalog as catalog
from llm_api_hub.server import provider_extensions as runtime


def test_endpoint_secret_and_public_catalog_definitions_match_actual_transports():
    assert set(ext.ENDPOINTS) == {"unorouter", "routeway", "requesty", "xkiro", "sealion"}
    assert ext.ENDPOINTS == runtime.CATALOG_ENDPOINTS
    assert all(catalog.ENDPOINTS[p] == url for p, url in ext.ENDPOINTS.items())
    assert all(catalog.SECRETS[p] == runtime.ENDPOINTS[p][1][0] for p in ext.ENDPOINTS)
    assert "typhoon" not in catalog.ENDPOINTS and "xfyun" not in catalog.ENDPOINTS
    assert set(ext.ENDPOINTS) & catalog.PUBLIC_CATALOGS == {"routeway", "requesty", "xkiro"}


def tier(inp=0, out=0, threshold=0, **kw):
    return {"prompt_tokens_threshold": threshold, "input_price": inp, "output_price": out, **kw}


def test_requesty_uses_documented_array_and_all_tiers_and_optional_charge_fields():
    assert ext._pricing({"pricing": [tier(), tier(threshold=1000)]}, "requesty") == ({"prompt": 0, "completion": 0}, "free_zero_price")
    assert ext._pricing({"pricing": [tier(), tier(out=2e-9, threshold=1000)]}, "requesty") == ({"prompt": 0, "completion": 2e-9}, "paid")
    assert ext._pricing({"pricing": [tier(caching_price=1)]}, "requesty")[1] == "paid"
    assert ext._pricing({"pricing": [tier()], "input_price": 1}, "requesty")[1] == "unknown"
    assert ext._pricing({"pricing": [tier()], "input_price": 0}, "requesty")[1] == "free_zero_price"
    # Obsolete invented {tiers:...} and flat-only prices cannot prove zero cost.
    assert ext._pricing({"pricing": {"tiers": [tier()]}}, "requesty")[1] == "unknown"
    assert ext._pricing({"input_price": 0, "output_price": 0}, "requesty")[1] == "unknown"


@pytest.mark.parametrize("bad", [True, -1, math.nan, math.inf, "0", 10**1000, None])
def test_requesty_invalid_numeric_prices_are_unknown(bad):
    assert ext._pricing({"pricing": [tier(out=bad)]}, "requesty")[1] == "unknown"


@pytest.mark.parametrize("tiers", [[], [None], [tier(threshold=10)], [tier(), tier()], [tier(), tier(threshold=-1)], [tier(threshold=False)]])
def test_requesty_bad_thresholds_and_shapes_are_unknown(tiers):
    assert ext._pricing({"pricing": tiers}, "requesty")[1] == "unknown"


def route_price(inp=0, out=0):
    return {"input": {"unit": "1M tokens", "price_per_million_t": inp}, "output": {"unit": "1M tokens", "price_per_million_t": out}}


def test_routeway_nested_per_million_rates_and_cache_prices():
    assert ext._pricing({"pricing": route_price(0, 2.5)}, "routeway") == ({"prompt": 0, "completion": 0.0000025}, "paid")
    assert ext._pricing({"pricing": route_price()}, "routeway")[1] == "free_zero_price"
    p = route_price()
    p["caching"] = {"read": {"unit": "1M tokens", "price_per_million_t": 1}}
    assert ext._pricing({"pricing": p}, "routeway")[1] == "paid"
    p["input"]["unit"] = "tokens"
    assert ext._pricing({"pricing": p}, "routeway")[1] == "unknown"
    assert ext._pricing({"pricing": route_price(1e-320, 0)}, "routeway")[1] == "paid"


@pytest.mark.parametrize("bad", [True, -1, math.nan, math.inf, "0", 10**1000, None])
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


def test_catalog_dispatch_uses_annotated_official_schema(monkeypatch):
    def get(url, token):
        return {"data": [{"id": "nvidia/model", "pricing": [tier()], "context_window": 4096}]}, {}
    monkeypatch.setattr(catalog, "get_json", get)
    row = catalog.poll("requesty", "synthetic")[0][0]
    assert row["pricing_classification"] == "free_zero_price"
    assert row["context_length"] == 4096
    assert "quota_remaining" not in row and "runtime_eligible" not in row


@pytest.mark.parametrize("payload", [None, [], {}, {"data": None}, {"data": [None]}, {"data": [{"id": []}]}, {"data": [{"id": "m\n"}]}])
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
