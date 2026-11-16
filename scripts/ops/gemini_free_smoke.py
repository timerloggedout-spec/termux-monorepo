#!/usr/bin/env python3
"""One explicit synthetic Gemini smoke, only on a live verified unbilled project.

No credential creation, secret export, routing admission, retry or paid fallback.
Official sources: https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-flash-lite
https://ai.google.dev/gemini-api/docs/billing
https://cloud.google.com/api-keys/docs/reference/rest/v2/projects.locations.keys/getKeyString
https://cloud.google.com/billing/docs/reference/rest/v1/projects/getBillingInfo

A Gemini API key alone cannot establish its project's billing tier. An existing
Google OAuth token with read permissions and the existing API key resource name
are needed for live verification; absence is a blocker, not an attestation flag.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hmac
import http.client
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

MODEL = "gemini-3.1-flash-lite"
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}"
CHAT_URL = MODEL_URL + ":generateContent"
# Reviewed official Standard Free-tier input/output price, not a paid-tier credit.
# Expiry prevents an old reviewed price from silently authorizing later requests.
PRICE_VERIFIED_AT = datetime(2026, 10, 21, 13, 6, tzinfo=timezone.utc)
PRICE_MAX_AGE = timedelta(hours=24)
MAX_BYTES = 65536
TIMEOUT = 10
KEY_RESOURCE = re.compile(r"projects/([1-9][0-9]*)/locations/global/keys/([A-Za-z0-9_-]{1,128})")
PROJECT_ID = re.compile(r"[a-z][a-z0-9-]{4,61}[a-z0-9]")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class SmokeError(ValueError):
    """Fixed reason codes only; never include upstream text or credentials."""


def _valid_secret(value):
    return isinstance(value, str) and 0 < len(value) <= 16384 and all(32 < ord(c) < 127 for c in value)


def _url_allowed(url):
    return (url in {MODEL_URL, CHAT_URL}
            or re.fullmatch(r"https://apikeys\.googleapis\.com/v2/" + KEY_RESOURCE.pattern + r"/keyString", url) is not None
            or re.fullmatch(r"https://cloudresourcemanager\.googleapis\.com/v3/projects/[1-9][0-9]*", url) is not None
            or re.fullmatch(r"https://cloudbilling\.googleapis\.com/v1/projects/" + PROJECT_ID.pattern + r"/billingInfo", url) is not None)


def request(url, credential, payload=None):
    """Fixed HTTPS destinations; API keys only in headers, never URLs or output."""
    if not isinstance(url, str) or not _url_allowed(url) or not _valid_secret(credential):
        raise SmokeError("invalid_request")
    is_gemini = url in {MODEL_URL, CHAT_URL}
    if (payload is not None) != (url == CHAT_URL):
        raise SmokeError("invalid_request")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    headers["x-goog-api-key" if is_gemini else "Authorization"] = credential if is_gemini else "Bearer " + credential
    req = urllib.request.Request(url, headers=headers, method="POST" if payload is not None else "GET",
                                 data=json.dumps(payload).encode() if payload is not None else None)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=TIMEOUT) as response:
            if response.status != 200:
                raise SmokeError("http_error")
            raw = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as error:
        raise SmokeError("http_" + str(error.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
        raise SmokeError("transport_unavailable") from None
    if len(raw) > MAX_BYTES:
        raise SmokeError("response_too_large")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise SmokeError("invalid_response") from None
    if not isinstance(value, dict):
        raise SmokeError("invalid_response")
    return value


def verify_project(key, oauth, resource):
    """Bind the actual in-process key to an active project with no billing link."""
    match = KEY_RESOURCE.fullmatch(resource) if isinstance(resource, str) else None
    if match is None:
        raise SmokeError("api_key_resource_missing_or_invalid")
    if not _valid_secret(oauth):
        raise SmokeError("project_read_authorization_missing")
    number = match.group(1)
    observed = request(f"https://apikeys.googleapis.com/v2/{resource}/keyString", oauth)
    actual = observed.get("keyString")
    if not _valid_secret(actual) or not hmac.compare_digest(actual, key):
        raise SmokeError("api_key_project_binding_unverified")
    del actual, observed
    project = request(f"https://cloudresourcemanager.googleapis.com/v3/projects/{number}", oauth)
    project_id = project.get("projectId")
    if (project.get("name") != "projects/" + number or project.get("state") != "ACTIVE"
            or not isinstance(project_id, str) or PROJECT_ID.fullmatch(project_id) is None):
        raise SmokeError("active_project_unverified")
    billing = request(f"https://cloudbilling.googleapis.com/v1/projects/{project_id}/billingInfo", oauth)
    # billingEnabled=false alone also describes a linked closed/suspended account.
    # Require an explicit absence of the billing account link, never a zero balance.
    if (billing.get("projectId") != project_id or billing.get("billingEnabled") is not False
            or billing.get("billingAccountName") != ""):
        raise SmokeError("unbilled_project_unverified")


def observe(key=None, *, oauth=None, resource=None, execute=False, now=None):
    report = {"schema": "gemini-free-smoke/v1", "provider": "gemini", "model": MODEL,
              "credential_present": bool(key), "free_project_verified": False,
              "official_zero_price_verified": False, "exact_model_available": False,
              "inference_attempted": False, "inference_ok": False, "completion_requests": 0,
              "production_admission_changed": False, "paid_fallback_allowed": False,
              "reason": "explicit_smoke_not_requested"}
    if not execute:
        return report
    if not _valid_secret(key):
        report["reason"] = "missing_or_invalid_secret"
        return report
    now = now if now is not None else datetime.now(timezone.utc)
    if (not isinstance(now, datetime) or now.tzinfo is None
            or not PRICE_VERIFIED_AT <= now <= PRICE_VERIFIED_AT + PRICE_MAX_AGE):
        report["reason"] = "official_zero_price_evidence_expired"
        return report
    report["official_zero_price_verified"] = True
    stage = "project"
    try:
        verify_project(key, oauth, resource)
        report["free_project_verified"] = True
        stage = "model"
        model = request(MODEL_URL, key)
        methods = model.get("supportedGenerationMethods")
        if (model.get("name") != "models/" + MODEL or not isinstance(methods, list)
                or "generateContent" not in methods):
            raise SmokeError("exact_model_unavailable")
        report["exact_model_available"] = True
        # Re-check immediately before inference; do not rely on a cached attestation.
        stage = "project_recheck"
        report["free_project_verified"] = False
        verify_project(key, oauth, resource)
        report["free_project_verified"] = True
        stage = "inference"
        report.update(inference_attempted=True, completion_requests=1)
        value = request(CHAT_URL, key, {
            "contents": [{"role": "user", "parts": [{"text": "Reply with exactly: OK"}]}],
            "generationConfig": {"maxOutputTokens": 16, "temperature": 0},
        })
        candidates = value.get("candidates")
        parts = candidates[0].get("content", {}).get("parts") if isinstance(candidates, list) and len(candidates) == 1 and isinstance(candidates[0], dict) and isinstance(candidates[0].get("content"), dict) else None
        valid_parts = isinstance(parts, list) and len(parts) == 1 and isinstance(parts[0], dict)
        text = parts[0].get("text") if valid_parts else None
        report["inference_ok"] = bool(isinstance(text, str) and text.strip() == "OK"
                                      and candidates[0].get("finishReason") == "STOP"
                                      and value.get("modelVersion") == MODEL)
        report["reason"] = "verified_free_smoke_succeeded" if report["inference_ok"] else "unexpected_completion"
    except SmokeError as error:
        # Only our fixed codes are permitted; raw upstream bodies are discarded.
        report["reason"] = stage + "_" + str(error)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    report = observe(os.environ.get("GEMINI_API_KEY"),
                     oauth=os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN"),
                     resource=os.environ.get("GEMINI_API_KEY_RESOURCE"), execute=args.execute)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if not args.execute or report["inference_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
