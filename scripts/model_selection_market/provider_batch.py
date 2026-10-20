"""MSM-010: reconcile every research candidate with native catalog observations.

This report is not a routing policy. No endpoint is derived from research text,
no inference is performed and no account entitlement is inferred from a catalog.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .resource_index import _validate_provider

# Reviewed identity mappings, not fuzzy provider-name matching.
PROVIDER_MAP = {
    "openrouter": "openrouter",
    "hugging-face": "huggingface",
    "google-gemini": "gemini",
    "groq": "groq",
    "mistral-ai": "mistral",
}
NATIVE_CHAT_PROVIDERS = frozenset({"groq", "mistral", "gemini"})


def reconcile(snapshot: dict, catalog: dict) -> dict:
    candidates, _ = _validate_provider(snapshot)
    if not isinstance(catalog, dict) or catalog.get("schema") != "provider-model-catalog/v5":
        raise ValueError("catalog schema must be provider-model-catalog/v5")
    if not isinstance(catalog.get("models"), list) or not isinstance(catalog.get("provider_observations"), dict):
        raise ValueError("catalog requires models and provider_observations")
    live = {}
    for row in catalog["models"]:
        if not isinstance(row, dict):
            raise ValueError("catalog model must be an object")
        key = (row.get("provider"), row.get("id"))
        if any(not isinstance(value, str) or not value for value in key) or key in live:
            raise ValueError("invalid or duplicate catalog identity")
        live[key] = row
    results = []
    seen = set()
    for candidate in candidates:
        key = (candidate["source_repo"], candidate["provider_key"], candidate["model_key"])
        if key in seen:
            raise ValueError("duplicate research identity")
        seen.add(key)
        native = PROVIDER_MAP.get(candidate["provider_key"])
        model_id = candidate.get("model_id")
        if model_id is not None and not isinstance(model_id, str):
            raise ValueError("research model_id must be a string")
        observed = live.get((native, model_id))
        # An injected documented model-page row is not a successful list result.
        listed = observed is not None and observed.get("raw_source") == f"{native}:/v1/models"
        if not native:
            status = "adapter_not_implemented"
        elif not model_id or model_id.startswith("aggregate:"):
            status = "not_an_individual_model"
        elif native not in catalog["provider_observations"]:
            status = "catalog_unavailable"
        elif listed:
            status = "observed_in_catalog"
        else:
            status = "not_observed_in_catalog"
        results.append({
            "source_repo": candidate["source_repo"],
            "provider_key": candidate["provider_key"],
            "model_key": candidate["model_key"],
            "model_id": model_id,
            "native_provider": native,
            "native_chat_adapter": native in NATIVE_CHAT_PROVIDERS,
            "status": status,
            "pricing_classification": observed.get("pricing_classification", "unknown") if listed else "unknown",
            "runtime_eligible": False,
            "quota_remaining": None,
            "blocked_reasons": [*candidate["blocked_reasons"], "exact-model account admission required; catalog is not free entitlement"],
        })
    results.sort(key=lambda row: (row["source_repo"], row["provider_key"], row["model_key"]))
    return {
        "schema_version": "msm-provider-batch-v1",
        "research_sha256": hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "sources": snapshot["sources"],
        "catalog_observed_at": catalog.get("observed_at"),
        "summary": {"candidates": len(results), "by_status": dict(sorted(Counter(row["status"] for row in results).items())), "runtime_eligible": 0},
        "candidates": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", default="data/model-selection-market/provider-recon.json")
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    report = reconcile(json.loads(Path(args.research).read_text()), json.loads(Path(args.catalog).read_text()))
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent, delete=False) as handle:
            temp = handle.name
            json.dump(report, handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(temp, destination)
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
