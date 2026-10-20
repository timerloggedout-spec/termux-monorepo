#!/usr/bin/env python3
"""One explicitly requested zero-price smoke; never enables production routing."""
from __future__ import annotations

import argparse
import datetime as dt
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import tempfile
import urllib.error
import urllib.request

BASE = "https://openrouter.ai/api/v1"
# Reviewed exact identity from the production catalog; never select the first model.
MODEL = "liquid/lfm-2.5-2.6b:free"
MAX_BYTES = 2 * 1024 * 1024
TIMEOUT = 30


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(path, token, payload=None):
    if path not in {"/key", "/models", "/chat/completions"}:
        raise ValueError("invalid_endpoint")
    req = urllib.request.Request(
        BASE + path, data=None if payload is None else json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json",
                 "Content-Type": "application/json", "User-Agent": "provider-free-smoke/1"},
        method="GET" if payload is None else "POST")
    with urllib.request.build_opener(NoRedirect).open(req, timeout=TIMEOUT) as response:
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("response_too_large")
        if not 200 <= response.status < 300:
            raise ValueError("invalid_status")
    value = json.loads(body)
    if not isinstance(value, dict):
        raise ValueError("invalid_response")
    return value


def zero(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return False
    try:
        number = Decimal(str(value))
        return number.is_finite() and number == 0
    except InvalidOperation:
        return False


def free_model(row):
    if not isinstance(row, dict) or row.get("id") != MODEL:
        return False
    pricing = row.get("pricing")
    return (isinstance(pricing, dict) and {"prompt", "completion"} <= pricing.keys()
            and all(zero(price) for price in pricing.values()))


def observe(token, execute=False):
    report = {"schema": "provider-free-smoke/v1", "provider": "openrouter",
              "credential_environment": "OPENROUTER_API_KEY", "credential_present": bool(token),
              "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "model": MODEL, "free_account_verified": False, "zero_price_verified": False,
              "inference_attempted": False, "inference_ok": False,
              "completion_requests": 0, "paid_fallback_allowed": False,
              "production_admission_changed": False, "reason": "explicit_smoke_not_requested"}
    if not execute:
        return report
    if not token:
        report["reason"] = "missing_secret"
        return report
    stage = "account"
    try:
        account = request("/key", token).get("data")
        if not isinstance(account, dict) or account.get("is_free_tier") is not True:
            report["reason"] = "free_account_unverified"
            return report
        report["free_account_verified"] = True
        # Do not persist labels, balances, quotas, identifiers, or account responses.
        stage = "catalog"
        models = request("/models", token).get("data")
        matches = [row for row in models if isinstance(row, dict) and row.get("id") == MODEL] if isinstance(models, list) else []
        if len(matches) != 1 or not free_model(matches[0]):
            report["reason"] = "exact_zero_price_model_unverified"
            return report
        report["zero_price_verified"] = True
        payload = {"model": MODEL, "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
                   "max_tokens": 16, "stream": False,
                   "provider": {"allow_fallbacks": False, "require_parameters": True,
                                "max_price": {"prompt": 0, "completion": 0, "request": 0, "image": 0}}}
        stage = "inference"
        report.update(inference_attempted=True, completion_requests=1)
        value = request("/chat/completions", token, payload)
        # Never persist a response body or any provider-supplied identifiers.
        choices = value.get("choices")
        content = choices[0].get("message", {}).get("content") if isinstance(choices, list) and choices and isinstance(choices[0], dict) and isinstance(choices[0].get("message"), dict) else None
        usage = value.get("usage")
        if value.get("error") or value.get("model") not in {MODEL, MODEL.removesuffix(":free")} or not isinstance(content, str) or content.strip() != "OK":
            report["reason"] = "inference_response_unverified"
            return report
        if not isinstance(usage, dict) or not zero(usage.get("cost")):
            report["reason"] = "inference_zero_cost_receipt_unverified"
            return report
        report.update(inference_ok=True, reason="verified_zero_cost_smoke", observed_cost_zero=True)
    except urllib.error.HTTPError as exc:
        report["reason"] = f"{stage}_http_{exc.code}"
    except (OSError, ValueError, TypeError, KeyError, IndexError):
        report["reason"] = f"{stage}_transport_or_response_failure"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    report = observe(os.environ.get("OPENROUTER_API_KEY"), execute=args.execute)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(report, handle, sort_keys=True, indent=2)
        handle.write("\n")
        temporary = handle.name
    os.replace(temporary, path)
    print(json.dumps({"reason": report["reason"], "inference_ok": report["inference_ok"],
                      "completion_requests": report["completion_requests"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
