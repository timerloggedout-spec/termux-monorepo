import datetime as dt
import json
from unittest.mock import patch

from scripts import provider_availability_probe as probe


CREDENTIAL_KEYS = (
    "GEMINI_API_KEY",
    "OPENROUTER_API_KEY",
    "FELO_AI_API",
    "HUGGINGFACE_TOKEN",
    "HF_TOKEN",
    "GOOGLE_API_KEY", "OMNI_API_KEY", "GROQ_API_KEY", "MISTRAL_API_KEY",
    "CEREBRAS_API_KEY", "NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY", "AION_API_KEY",
    "LLM7_API_TOKEN", "ZAI_API_KEY", "MODELSCOPE_TOKEN", "SILICONFLOW_API_KEY",
    "KILO_API_KEY", "OVHCLOUD_API_KEY", "SAMBANOVA_API_KEY", "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID", "COHERE_API_KEY", "OLLAMA_API_KEY",
    "HUGGING_FACE_HUB_TOKEN", "HF_API_TOKEN",
)


def test_result_row_schema_defaults():
    row = probe.result("openrouter")
    assert row["provider"] == "openrouter"
    assert row["credential_present"] is False
    assert row["catalog_ok"] is False
    assert row["inference_ok"] is False
    assert row["model"] is None
    assert row["error_class"] is None
    assert row["observed_at"].endswith("Z")


def test_now_is_utc_z_suffixed():
    stamp = probe.now()
    assert stamp.endswith("Z")
    # Must be parseable as a tz-aware timestamp.
    parsed = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() == dt.timedelta(0)


def test_probe_catalog_missing_secret_is_credential_safe():
    row = probe.result("openrouter")
    with patch.dict("os.environ", {k: "" for k in CREDENTIAL_KEYS}, clear=False):
        probe.probe_catalog("openrouter", "https://example.invalid/models", "", row)
    assert row["credential_present"] is False
    assert row["catalog_ok"] is False
    assert row["inference_ok"] is False
    assert row["error_class"] == "missing_secret"
    # No token-derived fields should leak into the evidence row.
    assert row["model"] is None


def test_gemini_probe_missing_secret_is_credential_safe():
    row = probe.result("gemini")
    probe.gemini_probe(row, "")
    assert row["credential_present"] is False
    assert row["catalog_ok"] is False
    assert row["inference_ok"] is False
    assert row["error_class"] == "missing_secret"
    assert row["model"] is None


def test_openrouter_inference_noop_without_credentials():
    row = probe.result("openrouter")
    # No token, no model, catalog not ok -> must remain a no-op.
    probe.openrouter_inference(row, "")
    assert row["inference_ok"] is False
    assert row["error_class"] is None


def test_openrouter_inference_noop_when_catalog_failed():
    row = probe.result("openrouter")
    row["model"] = "some/model:free"
    row["catalog_ok"] = False
    probe.openrouter_inference(row, "dummy-token")
    assert row["inference_ok"] is False
    assert row["error_class"] is None


def test_main_writes_document_without_leaking_secrets(tmp_path):
    out = tmp_path / "availability.json"
    env = {k: "" for k in CREDENTIAL_KEYS}
    env["OUTPUT"] = str(out)
    from scripts import provider_model_catalog

    # Public catalogs are still observed, but the test must never use the network.
    with patch.dict("os.environ", env, clear=True), patch.object(
        provider_model_catalog, "poll",
        side_effect=lambda provider, token: ([{"id": f"fixture-{provider}", "free_suffix": False}], {}),
    ):
        probe.main()
    assert out.exists()
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["schema"] == "provider-availability/v1"
    assert doc["observed_at"].endswith("Z")
    providers = {row["provider"] for row in doc["providers"]}
    assert {"gemini", "openrouter", "felo", "huggingface", "aion", "llm7",
            "zai", "modelscope", "siliconflow", "kilo", "ovhcloud",
            "sambanova", "cloudflare", "cohere", "ollama"}.issubset(providers)
    public = {"llm7", "modelscope", "ovhcloud"}
    for row in doc["providers"]:
        assert row["credential_present"] is False
        assert row["inference_ok"] is False
        if row["provider"] in public:
            assert row["auth_mode"] == "public"
            assert row["catalog_probe_required"] is True
            assert row["catalog_ok"] is True
        else:
            assert row["auth_mode"] == "unconfigured"
            assert row["catalog_probe_required"] is False
            assert row["catalog_ok"] is False
    # Credentials must never be serialized into the evidence document.
    body = out.read_text(encoding="utf-8")
    for key in CREDENTIAL_KEYS:
        assert key not in body


def test_huggingface_alias_precedence_matches_catalog():
    env = {
        "HUGGINGFACE_TOKEN": "first",
        "HUGGING_FACE_HUB_TOKEN": "second",
        "HF_API_TOKEN": "third",
        "HF_TOKEN": "fourth",
    }
    assert probe.resolve_huggingface_token(env) == "first"
    for alias in probe.HF_TOKEN_ALIASES:
        env = {name: "" for name in probe.HF_TOKEN_ALIASES}
        env[alias] = alias
        assert probe.resolve_huggingface_token(env) == alias


def test_gemini_auth_uses_header_never_url_token():
    calls = []

    def fake_request(url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith("/models"):
            return 200, {"models": [{"name": "models/gemini-flash", "supportedGenerationMethods": ["generateContent"]}]}
        return 200, {}

    row = probe.result("gemini")
    with patch.object(probe, "request", side_effect=fake_request):
        probe.gemini_probe(row, "secret-value")
    assert row["catalog_ok"] and row["inference_ok"]
    assert len(calls) == 2
    for url, kwargs in calls:
        assert "secret-value" not in url
        assert "key=" not in url
        assert kwargs["auth_header"] == "x-goog-api-key"
        assert kwargs["token"] == "secret-value"


def test_probe_errors_do_not_expose_error_body_or_token():
    row = probe.result("gemini")
    secret = "private-key-value"
    with patch.object(probe, "request", side_effect=OSError(f"request failed {secret}")):
        probe.gemini_probe(row, secret)
    assert row["error_class"] == "OSError"
    assert secret not in json.dumps(row)


def test_request_rejects_redirects_and_bounds_response():
    from unittest.mock import Mock
    import urllib.error

    redirect = urllib.error.HTTPError("https://example.test", 302, "Found", {}, None)
    with patch.object(probe._OPENER, "open", side_effect=redirect):
        try:
            probe.request("https://example.test", token="secret")
        except urllib.error.HTTPError as exc:
            assert exc.code == 302
        else:
            raise AssertionError("redirect must not be followed")
    response = Mock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.read.return_value = b"x" * (probe.MAX_RESPONSE_BYTES + 1)
    with patch.object(probe._OPENER, "open", return_value=response):
        try:
            probe.request("https://example.test")
        except ValueError as exc:
            assert str(exc) == "response_too_large"
        else:
            raise AssertionError("oversized response must be rejected")


def test_request_places_gemini_key_in_header_not_url():
    from unittest.mock import Mock

    response = Mock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.status = 200
    response.read.return_value = b"{}"
    captured = {}

    def open_request(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = request.headers
        return response

    with patch.object(probe._OPENER, "open", side_effect=open_request):
        probe.request("https://example.test/models", token="private-key", auth_header="x-goog-api-key")
    assert "private-key" not in captured["url"]
    assert "key=" not in captured["url"]
    assert captured["headers"]["X-goog-api-key"] == "private-key"



def test_public_catalog_probe_does_not_require_credentials_or_inference():
    from scripts import provider_model_catalog

    row = probe.result("ovhcloud")
    with patch.dict("os.environ", {}, clear=True), patch.object(
        provider_model_catalog, "poll", return_value=([{"id": "public-model"}], {})
    ) as poll:
        probe.catalog_provider_probe("ovhcloud", row, provider_model_catalog)
    poll.assert_called_once_with("ovhcloud", None)
    assert row["auth_mode"] == "public"
    assert row["catalog_probe_required"] is True
    assert row["catalog_ok"] is True
    assert row["model_count"] == 1
    assert row["inference_ok"] is False


def test_unconfigured_expanded_provider_never_calls_network():
    from scripts import provider_model_catalog

    row = probe.result("sambanova")
    with patch.dict("os.environ", {}, clear=True), patch.object(
        provider_model_catalog, "poll"
    ) as poll:
        probe.catalog_provider_probe("sambanova", row, provider_model_catalog)
    poll.assert_not_called()
    assert row["auth_mode"] == "unconfigured"
    assert row["catalog_probe_required"] is False
    assert row["error_class"] == "missing_secret"


def test_expanded_catalog_probe_never_runs_inference():
    from scripts import provider_model_catalog

    row = probe.result("sambanova")
    with patch.dict("os.environ", {"SAMBANOVA_API_KEY": "fixture-secret"}, clear=True), patch.object(
        provider_model_catalog, "poll", return_value=([{"id": "fixture-model"}], {})
    ) as poll:
        probe.catalog_provider_probe("sambanova", row, provider_model_catalog)
    poll.assert_called_once_with("sambanova", "fixture-secret")
    assert row["catalog_ok"] is True
    assert row["inference_ok"] is False
    assert "fixture-secret" not in json.dumps(row)
