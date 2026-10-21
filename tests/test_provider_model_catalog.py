import json
import pytest
from unittest.mock import patch
from scripts import provider_model_catalog


def test_resolve_secret():
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "hf_test_123"}, clear=True):
        tok, env = provider_model_catalog.resolve_secret("huggingface")
        assert tok == "hf_test_123"
        assert env == "HUGGINGFACE_TOKEN"

    with patch.dict("os.environ", {"HF_API_TOKEN": "hf_alias_456"}, clear=True):
        tok, env = provider_model_catalog.resolve_secret("huggingface")
        assert tok == "hf_alias_456"
        assert env == "HF_API_TOKEN"

    with patch.dict("os.environ", {}, clear=True):
        tok, env = provider_model_catalog.resolve_secret("openrouter")
        assert tok is None
        assert env == "OPENROUTER_API_KEY"


def test_price_classification():
    # Fast path zero price checks
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "0", "completion": "0"}}) == "free_zero_price"
    assert provider_model_catalog.price_classification({"pricing": {"prompt": 0, "completion": 0}}) == "free_zero_price"
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "0.0", "completion": "0.0"}}) == "free_zero_price"

    # Float conversions
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "0.000", "completion": "0.000"}}) == "free_zero_price"
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "0.001", "completion": "0.002"}}) == "paid"

    # Invalid or non-dict pricing
    assert provider_model_catalog.price_classification({"pricing": {}}) == "unknown"
    assert provider_model_catalog.price_classification({"pricing": "invalid"}) == "unknown"
    assert provider_model_catalog.price_classification({"pricing": {"prompt": "abc", "completion": "0"}}) == "unknown"


def test_get_json():
    class MockHeaders(dict):
        def items(self):
            return [("X-RateLimit-Remaining", "100"), ("User-Agent", "Ignored"), ("Retry-After", "10")]

    class MockResponse:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        @property
        def headers(self):
            return MockHeaders()
        def read(self, size):
            return b'{"data": []}'

    class MockOpener:
        def open(self, request, timeout):
            assert request.get_header("Authorization") == "Bearer tok"
            return MockResponse()

    with patch("urllib.request.build_opener", return_value=MockOpener()):
        data, headers = provider_model_catalog.get_json("https://example.com", token="tok")
        assert data == {"data": []}
        assert headers == {"x-ratelimit-remaining": "100", "retry-after": "10"}


def test_poll():
    mock_payload = {
        "data": [
            {
                "id": "test/free-model",
                "name": "Test Free Model",
                "pricing": {"prompt": "0", "completion": "0"},
                "context_length": 4096,
                "max_output_tokens": 2048,
            },
            {
                "id": "ox-alpha",
                "name": "OX Alpha Live",
                "pricing": {"prompt": "0", "completion": "0"},
            }
        ]
    }
    with patch("scripts.provider_model_catalog.get_json", return_value=(mock_payload, {"x-ratelimit-limit": "1000"})):
        rows, headers = provider_model_catalog.poll("felo", "dummy_token")
        assert len(rows) == 2
        assert rows[0]["id"] == "test/free-model"
        assert rows[0]["pricing_classification"] == "free_zero_price"
        assert rows[0]["access_classification"] == "catalog_pricing_only"

        # Test trial model overrides and hoisting
        assert rows[1]["id"] == "ox-alpha"
        assert rows[1]["access_classification"] == "free_trial"
        assert rows[1]["cadence"] == "trial"
        assert headers == {"x-ratelimit-limit": "1000"}


def test_main(tmp_path):
    output_file = tmp_path / "catalog.json"
    mock_payload = {
        "data": [
            {
                "id": "openrouter/free",
                "pricing": {"prompt": "0", "completion": "0"},
            }
        ]
    }
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-test"}, clear=True), \
         patch("scripts.provider_model_catalog.get_json", return_value=(mock_payload, {})):
        ret = provider_model_catalog.main(["--providers", "openrouter", "--output", str(output_file)])
        # Verify exit code 0 when catalog rows are parsed
        assert ret == 0
        assert output_file.exists()

def test_native_provider_normalization_and_auth_headers():
    fixtures = {
        "groq": ({"data": [{"id":"g1", "context_window":8192,"max_completion_tokens":1024,"active":True}]}, "Authorization", "Bearer secret"),
        "mistral": ({"data": [{"id":"m1","max_context_length":32768,"capabilities":{"vision":True}}]}, "Authorization", "Bearer secret"),
        "gemini": ({"models": [{"name":"models/g1","inputTokenLimit":4096,"outputTokenLimit":512,"supportedGenerationMethods":["generateContent"]}]}, "x-goog-api-key", "secret"),
    }
    for provider,(payload,header,value) in fixtures.items():
        calls=[]
        def fake(url,token,header_name="Authorization",page_token=None):
            calls.append((url,token,header_name,page_token)); return payload,{}
        with patch.object(provider_model_catalog,"_request",side_effect=fake):
            rows,_=provider_model_catalog.poll(provider,"secret")
        assert rows[0]["id"]=="g1" if provider=="gemini" else rows[0]["id"] in ("g1","m1")
        assert calls[0][1:3]==("secret",header)
        if provider=="gemini":
            assert rows[0]["context_length"]==4096 and rows[0]["max_output_tokens"]==512
        if provider=="mistral": assert rows[0]["context_length"]==32768 and rows[0]["capabilities"]=={"vision":True}
        if provider=="groq": assert rows[0]["active"] is True

def test_gemini_pagination_and_repeat_token_rejection():
    pages=[({"models":[{"name":"models/a"}],"nextPageToken":"a b"},{}),({"models":[{"name":"models/b"}]},{})]
    with patch.object(provider_model_catalog,"_request",side_effect=pages) as request:
        rows,_=provider_model_catalog.poll("gemini","tok")
    assert [r["id"] for r in rows]==["a","b"]
    assert request.call_args_list[1].args[0] == provider_model_catalog.ENDPOINTS["gemini"]
    assert request.call_args_list[1].args[3] == "a b"
    with patch.object(provider_model_catalog,"_request",return_value=({"models":[],"nextPageToken":"x"},{})):
        with pytest.raises(ValueError): provider_model_catalog.poll("gemini","tok")

def test_strict_catalog_shapes_prices_and_provider_specific_free_suffix():
    for payload in ({}, {"data":{}}, {"data":[None]}, {"data":[{"id":7}]}):
        with patch.object(provider_model_catalog,"get_json",return_value=(payload,{})):
            with pytest.raises(ValueError): provider_model_catalog.poll("groq","t")
    for val in (True,float("nan"),float("inf"),"NaN"):
        assert provider_model_catalog.price_classification({"pricing":{"prompt":val,"completion":0}})=="unknown"
    item={"data":[{"id":"x:free","pricing":{"prompt":"0","completion":"0"}}]}
    with patch.object(provider_model_catalog,"get_json",return_value=(item,{})):
        groq,_=provider_model_catalog.poll("groq","t")
        openrouter,_=provider_model_catalog.poll("openrouter","t")
    assert not groq[0]["free_suffix"] and openrouter[0]["free_suffix"]

def test_secret_alias_and_legacy_default_providers():
    with patch.dict("os.environ",{"GOOGLE_API_KEY":"g"},clear=True):
        assert provider_model_catalog.resolve_secret("gemini")==("g","GOOGLE_API_KEY")
    assert set(("openrouter","felo","omni","huggingface")).issubset(provider_model_catalog.ENDPOINTS)


def test_legacy_felo_trial_and_documentation_when_missing_from_catalog():
    with patch.object(provider_model_catalog, "get_json", return_value=({"data": []}, {})):
        rows, _ = provider_model_catalog.poll("felo", "token")
    trial = next(row for row in rows if row["id"] == "ox-alpha")
    assert trial["raw_source"] == "felo:/v1/models + documented-model-page"
    assert trial["access_classification"] == "free_trial"
    assert any(row["id"] == "ox-alpha" for row in provider_model_catalog.DOCUMENTED_ENTITLEMENTS["felo"])


def test_gemini_wire_contract_uses_query_page_token_but_header_api_key():
    from urllib.parse import urlsplit, parse_qs
    from unittest.mock import MagicMock
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = b'{"models": []}'
    response.headers = {}
    opener = MagicMock()
    opener.open.return_value = response
    with patch.object(provider_model_catalog.urllib.request, 'build_opener', return_value=opener):
        provider_model_catalog._request(provider_model_catalog.ENDPOINTS['gemini'], 'never-in-url', 'x-goog-api-key', 'token +/?=')
    request = opener.open.call_args.args[0]
    assert parse_qs(urlsplit(request.full_url).query) == {'pageToken': ['token +/?=']}
    assert request.get_header('X-goog-api-key') == 'never-in-url'
    assert 'never-in-url' not in request.full_url
    assert not request.has_header('Authorization')
    assert not request.has_header('X-goog-page-token')
    response.read.assert_called_once_with(8 * 1024 * 1024 + 1)


def test_authenticated_transport_installs_redirect_rejecting_handler():
    import urllib.request
    from unittest.mock import MagicMock
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = b'{"data": []}'
    response.headers = {}
    opener = MagicMock()
    opener.open.return_value = response
    real_builder = urllib.request.build_opener
    handlers = []
    def capture(handler):
        handlers.append(handler())
        return opener
    with patch.object(provider_model_catalog.urllib.request, 'build_opener', side_effect=capture):
        provider_model_catalog.get_json(provider_model_catalog.ENDPOINTS['groq'], 'secret')
    assert isinstance(handlers[0], urllib.request.HTTPRedirectHandler)
    req = urllib.request.Request(provider_model_catalog.ENDPOINTS['groq'])
    assert handlers[0].redirect_request(req, None, 302, 'found', {}, 'https://elsewhere.invalid/') is None


def test_duplicate_catalog_models_are_stably_deduplicated():
    payload = {'data': [{'id': 'qualified/model', 'context_window': 128}, {'id': 'qualified/model', 'context_window': 256}]}
    with patch.object(provider_model_catalog, 'get_json', return_value=(payload, {})):
        rows, _ = provider_model_catalog.poll('groq', 'secret')
    assert len(rows) == 1
    assert rows[0]['context_length'] == 128


def test_authorized_hf_token_alias_retains_precedence():
    with patch.dict("os.environ", {"HF_TOKEN": "alias"}, clear=True):
        assert provider_model_catalog.resolve_secret("huggingface") == ("alias", "HF_TOKEN")
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "primary", "HF_TOKEN": "alias"}, clear=True):
        assert provider_model_catalog.resolve_secret("huggingface") == ("primary", "HUGGINGFACE_TOKEN")
    from pathlib import Path
    workflow = Path(".github/workflows/provider-batch.yml").read_text()
    assert "secrets.HF_API_TOKEN || secrets.HF_TOKEN" in workflow


def test_new_official_catalog_endpoints_are_pinned_and_exact():
    assert provider_model_catalog.ENDPOINTS["aion"] == "https://api.aionlabs.ai/v1/models"
    assert provider_model_catalog.ENDPOINTS["llm7"] == "https://api.llm7.io/v1/models"
    assert provider_model_catalog.ENDPOINTS["kilo"] == "https://ai-gateway.kilo.ai/api/v1/models"
    assert provider_model_catalog.SECRETS["zai"] == "ZAI_API_KEY"
    assert provider_model_catalog.SECRETS["modelscope"] == "MODELSCOPE_TOKEN"
    assert provider_model_catalog.SECRETS["siliconflow"] == "SILICONFLOW_API_KEY"
    payload = {"data": [{"id": "openai/gpt-oss-120b", "pricing": {"prompt": 0, "completion": 0}}]}
    from unittest.mock import patch
    with patch.object(provider_model_catalog, "get_json", return_value=(payload, {})):
        rows, _ = provider_model_catalog.poll("kilo", "token")
    assert rows[0]["id"] == "openai/gpt-oss-120b"
    assert rows[0]["pricing_classification"] == "free_zero_price"
