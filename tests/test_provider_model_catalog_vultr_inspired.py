from scripts.provider_model_catalog_vultr_inspired import (
    OUTPUT_SCHEMA,
    normalize_incumbent,
)


def _incumbent(models):
    return {
        "schema": "provider-model-catalog/v5",
        "observed_at": "2026-11-21T00:00:00Z",
        "providers": ["fixture"],
        "provider_observations": {"fixture": {"status": "observed"}},
        "cadence_classes": ["daily", "unknown"],
        "errors": [{"provider": "fixture", "error": "timeout"}],
        "models": models,
    }


def test_vultr_inspired_projection_preserves_exact_prices_and_evidence():
    result = normalize_incumbent(_incumbent([{
        "provider": "fixture",
        "id": "model-a",
        "name": "Model A",
        "pricing": {"prompt": "0.00000017", "completion": "0"},
        "pricing_classification": "paid",
        "context_length": 128000,
        "max_output_tokens": 8192,
        "input_modalities": ["text", "image"],
        "output_modalities": ["text"],
        "active": True,
        "future_field": {"preserve": True},
    }]))

    assert result["schema"] == OUTPUT_SCHEMA
    assert result["catalogue"] == "VultrInspired"
    model = result["models"][0]
    assert model["pricing"]["exact_decimal_strings"] == {
        "prompt": "0.00000017",
        "completion": "0",
    }
    assert model["limits"] == {"context_tokens": 128000, "output_tokens": 8192}
    assert model["modalities"]["input"] == ["text", "image"]
    assert model["lifecycle"]["catalogue_active"] is True
    assert model["extensions"]["future_field"] == {"preserve": True}
    assert model["incumbent_record"]["provider"] == "fixture"
    assert result["provider_observations"]["fixture"]["status"] == "observed"
    assert result["cadence_classes"] == ["daily", "unknown"]
    assert result["source_errors"] == [{"provider": "fixture", "error": "timeout"}]
    assert result["incumbent_document"]["schema"] == "provider-model-catalog/v5"


def test_vultr_inspired_projection_isolates_invalid_rows_and_marks_float_prices():
    result = normalize_incumbent(_incumbent([
        None,
        {"provider": "fixture", "id": "model-b", "pricing": {"prompt": 0.1}},
        {"provider": "fixture", "id": "model-c", "pricing": {"prompt": "0.2"}},
    ]))

    assert [row["id"] for row in result["models"]] == ["model-b", "model-c"]
    assert result["models"][0]["pricing"]["exact_decimal_strings"] == {}
    assert result["models"][1]["pricing"]["exact_decimal_strings"] == {"prompt": "0.2"}
    assert {issue["code"] for issue in result["issues"]} == {
        "invalid_model_record",
        "pricing_value_not_exact_decimal",
    }


def test_vultr_inspired_projection_declares_offline_execution_boundary():
    result = normalize_incumbent(_incumbent([]))
    assert result["execution"] == {
        "mode": "offline_projection",
        "network_requests": 0,
        "credentials_required": False,
        "inference_calls": 0,
    }


def test_vultr_inspired_projection_requires_incumbent_schema():
    import pytest

    with pytest.raises(ValueError, match="unsupported_incumbent_schema"):
        normalize_incumbent({"schema": "unknown"})


def test_vultr_inspired_cli_writes_local_projection(tmp_path):
    import json
    from scripts import provider_model_catalog_vultr_inspired as adapter

    source = tmp_path / "incumbent.json"
    target = tmp_path / "vultr-inspired.json"
    source.write_text(json.dumps(_incumbent([
        {"provider": "fixture", "id": "model-cli", "pricing": {"prompt": "0.0001"}}
    ])), encoding="utf-8")

    assert adapter.main(["--input", str(source), "--output", str(target)]) == 0
    output = json.loads(target.read_text(encoding="utf-8"))
    assert output["catalogue"] == "VultrInspired"
    assert output["models"][0]["id"] == "model-cli"
