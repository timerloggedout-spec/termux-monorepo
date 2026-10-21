#!/usr/bin/env python3
"""Check batch transport/key/catalog readiness; never run inference or change policy."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys
import urllib.error

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from llm_api_hub.server import provider_extensions, research_providers
from scripts import provider_model_catalog, provider_quota_managers


def check(*, catalogs=False):
    """Only allowlisted booleans, counts and fixed error classes leave this process."""
    admitted = research_providers.admitted_models()
    rows = []
    for provider, (_, aliases) in sorted(provider_extensions.ENDPOINTS.items()):
        configured = any(bool(os.environ.get(name)) for name in aliases)
        row = {
            "provider": provider,
            "transport_registered": provider in research_providers.ENDPOINTS,
            "credential_present": configured,
            "exact_model_admitted": any(model.startswith(provider + "/") for model in admitted),
            "catalog_implemented": provider in provider_model_catalog.ENDPOINTS,
            "catalog_status": "not_requested",
            "inference_attempted": False,
            "quota_manager": provider_quota_managers.catalog_quota_status(
                provider, {}, observed_at=dt.datetime.now(dt.timezone.utc).isoformat()),
        }
        if catalogs:
            if provider not in provider_model_catalog.ENDPOINTS:
                row["catalog_status"] = "not_documented"
            elif not configured and provider not in provider_model_catalog.PUBLIC_CATALOGS:
                row["catalog_status"] = "missing_credential"
            else:
                try:
                    token = next((os.environ.get(name) for name in aliases if os.environ.get(name)), "")
                    _, headers = provider_model_catalog.poll(provider, token)
                    row["quota_manager"] = provider_quota_managers.catalog_quota_status(
                        provider, headers, observed_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                        source=provider_model_catalog.ENDPOINTS[provider])
                    row["catalog_status"] = "ok"
                except urllib.error.HTTPError as exc:
                    row["catalog_status"] = f"http_{exc.code}" if 100 <= exc.code <= 599 else "unavailable"
                except Exception:
                    row["catalog_status"] = "unavailable"
        row["readiness"] = (
            "missing_credential" if not configured else
            "admission_required" if not row["exact_model_admitted"] else
            "admitted_not_execution_verified"
        )
        rows.append(row)
    return {
        "schema": "provider-operational-check/v1",
        "providers": rows,
        "summary": {
            "registered_transports": sum(row["transport_registered"] for row in rows),
            "configured_credentials": sum(row["credential_present"] for row in rows),
            "admitted_providers": sum(row["exact_model_admitted"] for row in rows),
            "catalogs_ok": sum(row["catalog_status"] == "ok" for row in rows),
            "completion_requests": 0,
            "paid_fallback_allowed": False,
            "production_admission_changed": False,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogs", action="store_true", help="Read fixed public/existing-key model catalogs only")
    args = parser.parse_args(argv)
    print(json.dumps(check(catalogs=args.catalogs), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
