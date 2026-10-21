#!/usr/bin/env python3
"""Opt-in private quota-service observation; never imported by automatic collectors.

Ollama balance and OpenRouter key observations are explicit opt-in only. USD pools
and legacy percentages are not request counts, account identity, entitlement, or admission.
"""
from __future__ import annotations

import argparse
import datetime as dt
import http.client
import json
import os
from pathlib import Path
import re
import ssl
import stat
import sys
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.provider_quota_transport import (
    MAX_RESPONSE_BYTES, MAX_TIMEOUT_SECONDS, OLLAMA_BALANCE_URL,
    OPENROUTER_KEY_URL, observe_ollama_balance, observe_openrouter_key,
)

SERVICES = {
    "ollama.balance": {
        "provider_family": "ollama",
        "source": OLLAMA_BALANCE_URL,
        "credential_env": "OLLAMA_API_KEY",
        "scope": "credential-selected user or shared Team; identity not returned by source",
        "activation": "explicit_private_observation_only",
    },
    "openrouter.key": {
        "provider_family": "openrouter",
        "source": OPENROUTER_KEY_URL,
        "credential_env": "OPENROUTER_API_KEY",
        "scope": "credential-selected key; account identity unverified",
        "activation": "explicit_private_observation_only",
    },
}
SCOPE_STATUS = "credential_selected_user_or_team_identity_unverified"
FRESHNESS_SECONDS = 60


def _utc(now: dt.datetime) -> dt.datetime:
    if not isinstance(now, dt.datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("timezone-aware observation time required")
    return now.astimezone(dt.timezone.utc)


def _iso(now: dt.datetime) -> str:
    return _utc(now).isoformat().replace("+00:00", "Z")


def _time(value: str) -> dt.datetime:
    return _utc(dt.datetime.fromisoformat(value.replace("Z", "+00:00")))


def _context(service_id: str, scope: str) -> None:
    if not isinstance(service_id, str) or service_id not in SERVICES:
        raise ValueError("unsupported quota service")
    if not isinstance(scope, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", scope):
        raise ValueError("explicit bounded private scope alias required")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("nonfinite JSON value")


def https_request(*, method, url, headers, timeout, allow_redirects, max_response_bytes):
    """Single verified-TLS request; no proxies, redirects, retries or URL overrides.

    Socket operations time out after the bounded timeout; this is not a whole-job
    deadline. Only a bounded body is read, including for chunked responses.
    """
    if (method != "GET" or url not in (OLLAMA_BALANCE_URL, OPENROUTER_KEY_URL) or allow_redirects is not False
            or isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not 0 < timeout <= MAX_TIMEOUT_SECONDS
            or type(max_response_bytes) is not int or max_response_bytes != MAX_RESPONSE_BYTES
            or not isinstance(headers, dict) or set(headers) != {"Authorization"}):
        raise ValueError("invalid fixed-source transport contract")
    host, path = {OLLAMA_BALANCE_URL: ("ollama.com", "/api/balance"),
                  OPENROUTER_KEY_URL: ("openrouter.ai", "/api/v1/key")}[url]
    conn = http.client.HTTPSConnection(host, timeout=timeout, context=ssl.create_default_context())
    try:
        conn.request("GET", path, headers={**headers, "Accept": "application/json"})
        response = conn.getresponse()
        if response.status != 200:
            # Neither the error body nor Retry-After is interpreted as quota.
            return SimpleNamespace(status_code=response.status)
        length = response.getheader("Content-Length")
        if length is not None and (not length.isdecimal() or int(length) > max_response_bytes):
            raise ValueError("invalid or oversized response")
        body = response.read(max_response_bytes + 1)
        if len(body) > max_response_bytes:
            raise ValueError("oversized response")
        payload = json.loads(body.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_reject_constant)
        return SimpleNamespace(status_code=200, json=lambda: payload)
    finally:
        conn.close()


def observe_service(service_id: str, api_key: str, *, scope: str,
                    now: dt.datetime | None = None, request=None) -> dict[str, Any]:
    """Observe one credential-selected balance scope, in PRIVATE memory.

    Authenticated transport binds the response to the supplied credential, not to
    an independently verified account/Team identifier (the API returns none).
    Alias and values must remain private. Freshness expires at the earlier of
    sixty seconds or the next source-supplied reset. No reservation is performed.
    """
    _context(service_id, scope)
    now = _utc(dt.datetime.now(dt.timezone.utc) if now is None else now)
    result = {
        "schema": "provider-quota-service-observation/v1",
        "service_id": service_id, "provider_family": SERVICES[service_id]["provider_family"],
        "source": SERVICES[service_id]["source"], "observed_at": _iso(now),
        "scope": scope, "scope_status": ("credential_selected_key_account_identity_unverified"
                                          if service_id == "openrouter.key" else SCOPE_STATUS),
        "status": "unknown", "reason": "source_unavailable_or_invalid",
        "signals": {}, "valid_until": None, "runtime_admission": "unchanged",
        "request_quota": "unknown", "entitlement": "unknown",
    }
    adapter = observe_ollama_balance if service_id == "ollama.balance" else observe_openrouter_key
    observation = adapter(
        api_key, https_request if request is None else request,
        observed_at=_iso(now), scope=scope,
    )
    if observation["status"] != "observed":
        return result
    signals = observation["signals"]
    if service_id == "openrouter.key":
        counters = {"free_model_daily_used", "free_model_daily_limit", "free_model_daily_remaining"}
        result.update(status="observed", reason="sanitized_key_observation", signals=signals)
        if counters <= signals.keys():
            result["request_quota"] = "observed"
        reset = signals.get("openrouter_effective_budget_resets_at")
        if reset and _time(reset) <= now:
            result.update(status="unknown", reason="source_reset_due_refresh_required", signals={},
                          request_quota="unknown")
            return result
        validity = now + dt.timedelta(seconds=FRESHNESS_SECONDS)
        if reset:
            validity = min(validity, _time(reset))
        result["valid_until"] = _iso(validity)
        return result
    if "ollama_included_period_until" in signals:
        start = _time(signals["ollama_included_period_from"])
        end = _time(signals["ollama_included_period_until"])
        if not start <= now < end:
            result["reason"] = "source_period_not_current"
            return result
        kind = "remaining_usd_balance"
        resets = [end]
    else:
        resets = [_time(signals[f"ollama_{window}_resets_at"]) for window in ("session", "weekly")]
        if any(reset <= now for reset in resets):
            result["reason"] = "source_reset_due_refresh_required"
            return result
        kind = "remaining_legacy_percent_and_purchased_usd"
    result.update(status="observed", reason="current_source_balance", signals=signals,
                  balance_kind=kind, valid_until=_iso(min(now + dt.timedelta(seconds=FRESHNESS_SECONDS), *resets)))
    return result


def public_status(observation: dict[str, Any]) -> dict[str, Any]:
    """Status-only allowlist. Never publish scopes, values, resets or private hashes."""
    sid = observation.get("service_id")
    if sid == "gemini.project_model":
        # No trusted live Gemini collector exists; never publish caller claims
        # as verified project/account quota, tier, entitlement or billing state.
        public = {"service_id": sid, "provider_family": "gemini",
                  "status": "unknown", "request_quota": "unknown"}
        try:
            public["observed_at"] = _iso(_time(observation.get("observed_at")))
        except (TypeError, ValueError, AttributeError, OverflowError):
            public["observed_at"] = None
        return public
    if not isinstance(sid, str) or sid not in SERVICES:
        raise ValueError("unsupported quota service")
    public = {"service_id": sid, "provider_family": SERVICES[sid]["provider_family"],
              "status": "observed" if observation.get("status") == "observed" else "unknown",
              "observed_at": _iso(_time(observation["observed_at"]))}
    if sid == "openrouter.key":
        public["request_quota"] = (observation.get("request_quota")
                                   if observation.get("request_quota") in ("observed", "unknown")
                                   else "unknown")
    return public


def observe_gemini_quota(metadata=None, *, scope: str,
                         now: dt.datetime | None = None) -> dict[str, Any]:
    """Normalize PRIVATE caller-supplied Gemini evidence, without any API call.

    This is not a Google response schema or authenticated collector. No endpoint
    exposing actual project/model quotas is implemented, so supplied evidence
    cannot verify the active credential's project or grant runtime admission.
    No credentials, billing state, account observations or counts are logged.
    """
    from scripts.provider_quota_gemini import normalize_gemini_evidence

    unknown = {
        "schema": "provider-quota-service-observation/v1",
        "service_id": "gemini.project_model", "provider_family": "gemini",
        "source": "https://ai.google.dev/gemini-api/docs/rate-limits",
        "observed_at": None, "status": "unknown",
        "reason": "project_binding_and_current_quota_unverified",
        "request_quota": "unknown", "entitlement": "unknown",
        "tier": "unknown", "signals": {}, "valid_until": None,
        "runtime_admission": "unchanged",
    }
    try:
        now = _utc(dt.datetime.now(dt.timezone.utc) if now is None else now)
        unknown["observed_at"] = _iso(now)
        observation = normalize_gemini_evidence(
            {} if metadata is None else metadata, observed_at=_iso(now), scope=scope)
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
        return unknown
    return {**observation, "service_id": "gemini.project_model",
            "reason": "project_binding_and_current_quota_unverified",
            "request_quota": "unknown", "valid_until": None,
            "runtime_admission": "unchanged"}


def _open_private(path):
    target = Path(path)
    parent = target.parent.resolve(strict=True)
    info = parent.stat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o700):
        raise ValueError("private output requires an owned mode-0700 directory")
    if any((ancestor / ".git").exists() for ancestor in (parent, *parent.parents)):
        raise ValueError("private observations must remain outside repository worktrees")
    return os.open(parent / target.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)


def _write_fd(fd, observation):
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(observation, stream, allow_nan=False, sort_keys=True)
        stream.write("\n")


def write_private(path, observation):
    """Create a new private observation; never overwrite or follow a file symlink."""
    _write_fd(_open_private(path), observation)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service", choices=sorted(SERVICES), required=True)
    parser.add_argument("--scope", required=True, help="private alias for this credential-selected user/Team")
    parser.add_argument("--private-out", required=True, help="new file in an owned 0700 directory outside Git")
    parser.add_argument("--observe", action="store_true", required=True, help="explicitly authorize one balance GET")
    args = parser.parse_args(argv)
    try:
        _context(args.service, args.scope)
        # Reserve safe output BEFORE reading credentials or making a request.
        fd = _open_private(args.private_out)
    except (OSError, ValueError):
        parser.error("invalid context or private output destination")
    observation = observe_service(args.service, os.environ.get(SERVICES[args.service]["credential_env"], ""), scope=args.scope)
    _write_fd(fd, observation)
    print(json.dumps(public_status(observation), sort_keys=True))
    return 0 if observation["status"] == "observed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
