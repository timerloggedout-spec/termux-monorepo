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
    with patch.dict("os.environ", env, clear=False):
        probe.main()
    assert out.exists()
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["schema"] == "provider-availability/v1"
    assert doc["observed_at"].endswith("Z")
    providers = {row["provider"] for row in doc["providers"]}
    assert {"gemini", "openrouter", "felo", "huggingface"}.issubset(providers)
    for row in doc["providers"]:
        # With no credentials configured, every provider must be inert.
        assert row["credential_present"] is False
        assert row["catalog_ok"] is False
        assert row["inference_ok"] is False
    # Credentials must never be serialized into the evidence document.
    body = out.read_text(encoding="utf-8")
    for key in CREDENTIAL_KEYS:
        assert key not in body
