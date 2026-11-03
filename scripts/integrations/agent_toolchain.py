"""Deterministic, offline normalizers for external agent-toolchain observations.

No network requests are made and provider content is never executed.
Callers pass already-retrieved provider records to these pure functions.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
from typing import Any
from urllib.parse import urlsplit, urlunsplit

SCHEMA_VERSION = "1.0.0"
ADAPTER_VERSION = "0.1.0"
MAX_HAPI_REMOTES = 25
MAX_CONTEXT7_EXCERPT = 20_000
MAX_CONTEXT_DEV_EXCERPT = 4_000
MAX_SOURCE_REFS = 20
_LIBRARY_ID = re.compile(r"^/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(?:/([A-Za-z0-9_.+-]+))?$")
_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:sk|rk)-[A-Za-z0-9_-]{24,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)


def _required_text(value: Any, field: str, limit: int = 500) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    value = value.strip()
    if len(value) > limit:
        raise ValueError(f"{field} exceeds {limit} characters")
    return value


def _optional_text(value: Any, field: str, limit: int = 1000) -> str | None:
    return None if value is None else _required_text(value, field, limit)


def _timestamp(value: str) -> str:
    value = _required_text(value, "captured_at", 64)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("captured_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("captured_at must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _safe_url(value: Any, field: str) -> tuple[str, bool]:
    raw = _required_text(value, field, 2048)
    try:
        parts = urlsplit(raw)
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid URL") from exc
    if any(pattern.search(raw) for pattern in _SECRET_PATTERNS):
        raise ValueError(f"{field} contains credential-shaped material")
    if parts.scheme.lower() != "https" or not parts.hostname:
        raise ValueError(f"{field} must be an absolute HTTPS URL")
    if parts.username is not None or parts.password is not None:
        raise ValueError(f"{field} must not contain URL credentials")
    host = parts.hostname.lower()
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    netloc = host if port in (None, 443) else f"{host}:{port}"
    canonical = urlunsplit(("https", netloc, parts.path or "/", "", ""))
    return canonical, bool(parts.query or parts.fragment)


def _redact_text(value: str) -> str:
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    return value


def _excerpt(payload: dict[str, Any], limit: int) -> tuple[str, bool]:
    value = next((payload.get(key) for key in ("excerpt", "snippet", "content", "markdown", "text") if payload.get(key) is not None), None)
    if value is None and isinstance(payload.get("snippets"), list):
        parts = []
        for item in payload["snippets"][:10]:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("content") or item.get("code") or item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        value = "\n\n".join(parts)
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValueError("provider excerpt must be text")
    value = _redact_text(value)
    return value[:limit], len(value) > limit


def _source_refs(items: Any) -> list[dict[str, str]]:
    if items is None:
        return []
    if not isinstance(items, list):
        raise ValueError("sources must be a list")
    refs = []
    for item in items[:MAX_SOURCE_REFS]:
        if isinstance(item, str):
            url, _ = _safe_url(item, "source URL")
            refs.append({"url": url})
        elif isinstance(item, dict):
            url, _ = _safe_url(item.get("url") or item.get("source_url"), "source URL")
            ref = {"url": url}
            title = item.get("title")
            if isinstance(title, str) and title.strip():
                ref["title"] = title.strip()[:300]
            refs.append(ref)
        else:
            raise ValueError("each source reference must be a URL or object")
    return refs


def _observation(integration_id, record_type, record_key, captured_at, provider,
                 capture_method, provider_request_id, identity, data, trust):
    captured = _timestamp(captured_at)
    request_id = _optional_text(provider_request_id, "provider_request_id", 256)
    digest = hashlib.sha256(
        "|".join((integration_id, record_key, captured, request_id or "")).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "integration_id": integration_id,
        "record_type": record_type,
        "record_key": record_key,
        "observation_id": f"{integration_id}:{digest}",
        "observed_at": captured,
        "source": {
            "provider": provider,
            "capture_method": capture_method,
            "provider_request_id": request_id,
            "attribution": "provider_reported",
        },
        "identity": identity,
        "data": data,
        "trust": trust,
        "privacy": {
            "classification": "public",
            "contains_raw_prompt": False,
            "contains_secret": False,
            "redaction_applied": True,
        },
    }


def normalize_hapi_server(record: dict[str, Any], captured_at: str,
                          provider_request_id: str | None = None) -> dict[str, Any]:
    """Normalize one HAPI registry server-version record; never admit or execute it."""
    if not isinstance(record, dict):
        raise ValueError("HAPI record must be an object")
    server = record.get("server", record)
    if not isinstance(server, dict):
        raise ValueError("HAPI record.server must be an object")
    name = _required_text(server.get("name"), "server.name", 300)
    version = _required_text(server.get("version"), "server.version", 100)
    remotes_value = server.get("remotes", [])
    if not isinstance(remotes_value, list):
        raise ValueError("server.remotes must be a list")
    if len(remotes_value) > MAX_HAPI_REMOTES:
        raise ValueError(f"server.remotes exceeds {MAX_HAPI_REMOTES} entries")
    remotes = []
    seen_remotes = set()
    for remote in remotes_value:
        if not isinstance(remote, dict):
            raise ValueError("each server remote must be an object")
        transport = _required_text(remote.get("type"), "remote.type", 80)
        endpoint, _ = _safe_url(remote.get("url"), "remote.url")
        remote_key = (transport, endpoint)
        if remote_key not in seen_remotes:
            seen_remotes.add(remote_key)
            remotes.append({"transport": transport, "endpoint": endpoint})
    capabilities_value = server.get("capabilities", [])
    if not isinstance(capabilities_value, list):
        raise ValueError("server.capabilities must be a list")
    capabilities = sorted({item.strip()[:100] for item in capabilities_value if isinstance(item, str) and item.strip()})
    known = {"$schema", "name", "title", "description", "version", "remotes", "capabilities", "packages", "icons", "repository", "websiteUrl"}
    metadata = record.get("_meta", {})
    official = metadata.get("io.modelcontextprotocol.registry/official", {}) if isinstance(metadata, dict) else {}
    if not isinstance(official, dict):
        official = {}
    registry_metadata = {
        key: official[key] for key in ("status", "statusChangedAt", "publishedAt", "updatedAt", "isLatest")
        if isinstance(official.get(key), (str, bool))
    }
    title = server.get("title", "")
    description = server.get("description", "")
    if not isinstance(title, str) or not isinstance(description, str):
        raise ValueError("server title and description must be text")
    data = {
        "title": _redact_text(title)[:300],
        "description": _redact_text(description)[:1000],
        "remotes": remotes,
        "capabilities": capabilities,
        "registry_metadata": registry_metadata,
        "unmapped_field_names": sorted(str(key) for key in server if key not in known)[:50],
    }
    return _observation(
        "hapi-mcp-registry", "mcp_server_version", f"{name}@{version}", captured_at,
        "HAPI MCP Registry", "registry_server_version_listing", provider_request_id,
        {"server_name": name, "version": version}, data,
        {"security_review_status": "not_reviewed", "admission_status": "not_admitted", "execution_allowed": False},
    )


def normalize_context7_document(payload: dict[str, Any], library_id: str,
                                version: str | None, captured_at: str,
                                provider_request_id: str | None = None) -> dict[str, Any]:
    """Normalize Context7 documentation with exact library and version identity."""
    if not isinstance(payload, dict):
        raise ValueError("Context7 payload must be an object")
    library_id = _required_text(library_id, "library_id", 300)
    match = _LIBRARY_ID.fullmatch(library_id)
    if not match:
        raise ValueError("library_id must use /org/project or /org/project/version format")
    embedded = match.group(3)
    explicit = _optional_text(version, "version", 100)
    if embedded and explicit and embedded != explicit:
        raise ValueError("explicit version conflicts with version embedded in library_id")
    resolved = embedded or explicit
    if not resolved:
        raise ValueError("Context7 documentation requires an explicit resolved version")
    excerpt, truncated = _excerpt(payload, MAX_CONTEXT7_EXCERPT)
    refs = _source_refs(payload.get("sources"))
    if not refs:
        source_url = payload.get("source_url") or payload.get("url")
        if source_url:
            refs = _source_refs([{"url": source_url, "title": payload.get("title", "")}])
    title = payload.get("title", "")
    if not isinstance(title, str):
        raise ValueError("Context7 title must be text")
    parts = library_id.split("/")
    return _observation(
        "context7", "versioned_documentation_reference", f"/{parts[1]}/{parts[2]}@{resolved}",
        captured_at, "Context7", "resolved_library_documentation", provider_request_id,
        {"library_id": library_id, "version": resolved},
        {"title": _redact_text(title)[:300], "excerpt": excerpt, "truncated": truncated, "source_refs": refs},
        {"content_untrusted": True, "implementation_authority": "advisory_only"},
    )


def normalize_context_dev_result(payload: dict[str, Any], captured_at: str,
                                 provider_request_id: str | None = None) -> dict[str, Any]:
    """Normalize one Context.dev result, removing query strings and fragments."""
    if not isinstance(payload, dict):
        raise ValueError("Context.dev payload must be an object")
    url_value = payload.get("url") or payload.get("canonical_url") or payload.get("link")
    canonical, redacted = _safe_url(url_value, "Context.dev result URL")
    excerpt, truncated = _excerpt(payload, MAX_CONTEXT_DEV_EXCERPT)
    title = payload.get("title", "")
    if not isinstance(title, str):
        raise ValueError("Context.dev title must be text")
    return _observation(
        "context-dev", "web_research_result", canonical, captured_at, "Context.dev",
        "web_search_or_scrape", provider_request_id, {"canonical_url": canonical},
        {"canonical_url": canonical, "title": _redact_text(title)[:300], "excerpt": excerpt,
         "truncated": truncated, "url_query_redacted": redacted},
        {"content_untrusted": True, "implementation_authority": "advisory_only"},
    )


def validate_observation(observation: dict[str, Any]) -> list[str]:
    """Return contract violations for a normalized provider observation."""
    errors = []
    if not isinstance(observation, dict):
        return ["observation must be an object"]
    required = {"schema_version", "integration_id", "record_type", "record_key", "observation_id",
                "observed_at", "source", "identity", "data", "trust", "privacy"}
    missing = sorted(required - set(observation))
    if missing:
        return [f"missing required fields: {', '.join(missing)}"]
    if observation["schema_version"] != SCHEMA_VERSION:
        errors.append("unsupported schema_version")
    if observation["integration_id"] not in {"hapi-mcp-registry", "context7", "context-dev"}:
        errors.append("unsupported integration_id")
    try:
        _timestamp(observation["observed_at"])
    except (TypeError, ValueError):
        errors.append("observed_at must be timezone-aware ISO-8601")
    for section in ("source", "identity", "data", "trust", "privacy"):
        if not isinstance(observation[section], dict):
            errors.append(f"{section} must be an object")
    privacy = observation.get("privacy", {})
    if isinstance(privacy, dict):
        if privacy.get("contains_raw_prompt") is not False or privacy.get("contains_secret") is not False:
            errors.append("privacy must assert no raw prompt and no secret")
    trust = observation.get("trust", {})
    if isinstance(trust, dict) and observation.get("integration_id") == "hapi-mcp-registry":
        if trust.get("execution_allowed") is not False:
            errors.append("HAPI execution must remain disabled")
        if trust.get("admission_status") != "not_admitted":
            errors.append("HAPI admission must remain not_admitted")
        if trust.get("security_review_status") != "not_reviewed":
            errors.append("HAPI security review must remain not_reviewed")
    serialized = json.dumps(observation, ensure_ascii=False, sort_keys=True)
    if any(pattern.search(serialized) for pattern in _SECRET_PATTERNS):
        errors.append("credential-shaped value detected")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("hapi", "context7", "context-dev"), required=True)
    parser.add_argument("--captured-at", required=True)
    parser.add_argument("--request-id")
    parser.add_argument("--library-id")
    parser.add_argument("--version")
    args = parser.parse_args(argv)
    try:
        payload = json.load(sys.stdin)
        if args.provider == "hapi":
            result = normalize_hapi_server(payload, args.captured_at, args.request_id)
        elif args.provider == "context7":
            if not args.library_id:
                raise ValueError("--library-id is required for Context7")
            result = normalize_context7_document(payload, args.library_id, args.version, args.captured_at, args.request_id)
        else:
            result = normalize_context_dev_result(payload, args.captured_at, args.request_id)
        errors = validate_observation(result)
        if errors:
            raise ValueError("; ".join(errors))
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"adapter error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
