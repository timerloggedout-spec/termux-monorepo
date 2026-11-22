"""Native Vultr-inspired projection over the incumbent provider catalog.

This module projects local JSON through a standard-library-only offline adapter.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "provider-model-catalog/v5"
OUTPUT_SCHEMA = "provider-model-catalog/vultr-inspired/v1"
KNOWN_FIELDS = {
    "provider", "id", "name", "description", "pricing",
    "pricing_classification", "access_classification", "access_source",
    "access_source_observed", "entitlement_verification", "cadence",
    "free_suffix", "context_length", "max_output_tokens", "capabilities",
    "active", "raw_source", "input_modalities", "output_modalities",
    "inputs", "outputs", "created_at", "deprecated_at", "supported_parameters",
    "tools", "structured_output", "streaming", "reasoning",
}


def _decimal_string(value: Any) -> str | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        candidate = value
    elif isinstance(value, int):
        candidate = str(value)
    else:
        return None
    try:
        parsed = Decimal(candidate)
    except InvalidOperation:
        return None
    return candidate if parsed.is_finite() and parsed >= 0 else None


def _modalities(row: dict[str, Any], key: str) -> list[str]:
    value = row.get(key)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    return []


def normalize_incumbent(document: dict[str, Any]) -> dict[str, Any]:
    """Project incumbent v5 rows into a loss-aware, versioned local contract."""
    if not isinstance(document, dict) or document.get("schema") != INPUT_SCHEMA:
        raise ValueError("unsupported_incumbent_schema")
    source_models = document.get("models")
    if not isinstance(source_models, list):
        raise ValueError("invalid_models_collection")

    models: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for index, row in enumerate(source_models):
        if not isinstance(row, dict):
            issues.append({"index": index, "code": "invalid_model_record"})
            continue
        provider, model_id = row.get("provider"), row.get("id")
        if not isinstance(provider, str) or not provider or not isinstance(model_id, str) or not model_id:
            issues.append({"index": index, "code": "missing_model_identity"})
            continue

        pricing = row.get("pricing") if isinstance(row.get("pricing"), dict) else {}
        exact_pricing: dict[str, str] = {}
        for price_key, price_value in pricing.items():
            exact = _decimal_string(price_value)
            if exact is not None:
                exact_pricing[str(price_key)] = exact
            elif price_value is not None:
                issues.append({
                    "index": index,
                    "model_id": model_id,
                    "code": "pricing_value_not_exact_decimal",
                    "field": str(price_key),
                })

        readiness = row.get("active") if isinstance(row.get("active"), bool) else None
        models.append({
            "provider": provider,
            "id": model_id,
            "name": row.get("name"),
            "description": row.get("description"),
            "limits": {
                "context_tokens": row.get("context_length"),
                "output_tokens": row.get("max_output_tokens"),
            },
            "modalities": {
                "input": _modalities(row, "input_modalities"),
                "output": _modalities(row, "output_modalities"),
                "inputs": row.get("inputs") if isinstance(row.get("inputs"), list) else [],
                "outputs": row.get("outputs") if isinstance(row.get("outputs"), list) else [],
            },
            "pricing": {
                "source_values": dict(pricing),
                "exact_decimal_strings": exact_pricing,
                "classification": row.get("pricing_classification", "unknown"),
            },
            "capabilities": {
                "provider": row.get("capabilities"),
                "tools": row.get("tools"),
                "structured_output": row.get("structured_output"),
                "streaming": row.get("streaming"),
                "reasoning": row.get("reasoning"),
                "supported_parameters": row.get("supported_parameters"),
            },
            "lifecycle": {
                "readiness": readiness,
                "created_at": row.get("created_at"),
                "deprecated_at": row.get("deprecated_at"),
            },
            "access_evidence": {
                "classification": row.get("access_classification", "unknown"),
                "source": row.get("access_source"),
                "source_observed_at": row.get("access_source_observed"),
                "entitlement_verification": row.get("entitlement_verification", "unknown"),
                "cadence": row.get("cadence", "unknown"),
                "free_suffix": row.get("free_suffix", False),
            },
            "provenance": {
                "source": row.get("raw_source"),
                "observed_at": document.get("observed_at"),
                "source_schema": INPUT_SCHEMA,
            },
            "extensions": {key: value for key, value in row.items() if key not in KNOWN_FIELDS},
            "incumbent_record": dict(row),
        })

    return {
        "schema": OUTPUT_SCHEMA,
        "catalogue": "VultrInspired",
        "version": "1.0.0",
        "source_catalogue": "Incumbent",
        "source_version": INPUT_SCHEMA,
        "observed_at": document.get("observed_at"),
        "providers": list(document.get("providers", [])) if isinstance(document.get("providers"), list) else [],
        "provider_observations": dict(document.get("provider_observations", {}))
        if isinstance(document.get("provider_observations"), dict) else {},
        "cadence_classes": list(document.get("cadence_classes", []))
        if isinstance(document.get("cadence_classes"), list) else [],
        "source_errors": list(document.get("errors", []))
        if isinstance(document.get("errors"), list) else [],
        "source_extensions": {
            key: value for key, value in document.items()
            if key not in {"schema", "observed_at", "providers", "provider_observations", "cadence_classes", "models", "errors"}
        },
        "incumbent_document": dict(document),
        "models": models,
        "issues": issues,
        "execution": {
            "mode": "offline_projection",
            "network_requests": 0,
            "credentials_required": False,
            "inference_calls": 0,
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Transform a supplied incumbent snapshot into a local VultrInspired file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Incumbent v5 JSON document")
    parser.add_argument("--output", required=True, type=Path, help="VultrInspired v1 output path")
    args = parser.parse_args(argv)

    with args.input.open("r", encoding="utf-8") as source_file:
        incumbent = json.load(source_file)
    projection = normalize_incumbent(incumbent)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix=".vultr-inspired-", suffix=".tmp", dir=args.output.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output_file:
            json.dump(projection, output_file, indent=2, sort_keys=True)
            output_file.write("\n")
            output_file.flush()
            os.fsync(output_file.fileno())
        os.replace(temporary_path, args.output)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)

    print(f"catalogue={projection['catalogue']} version={projection['version']} models={len(projection['models'])} issues={len(projection['issues'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
