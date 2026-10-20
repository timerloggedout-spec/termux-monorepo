#!/usr/bin/env python3
"""One-shot, keyless public-source Markdown research via Firecrawl."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler

ENDPOINT = "https://api.firecrawl.dev/v2/scrape"
SOURCES = {
    "awesome-free-llm-apis": "https://github.com/mnfst/awesome-free-llm-apis",
    "freellmapi": "https://github.com/tashfeenahmed/freellmapi",
}
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
TIMEOUT_SECONDS = 60
SCHEMA = "public-research-service/v1"


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _envelope(source: str, status: str, reason: str, markdown=None) -> dict:
    result = {
        "schema": SCHEMA,
        "endpoint": ENDPOINT,
        "source_url": SOURCES[source],
        "authentication": "none",
        "status": status,
        "reason": reason,
        "observed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if markdown is not None:
        result["markdown"] = markdown
    return result


def _read_capped(response) -> bytes:
    data = response.read(MAX_RESPONSE_BYTES + 1)
    if len(data) > MAX_RESPONSE_BYTES:
        raise ValueError("response_too_large")
    return data


def scrape(source: str) -> dict:
    """Fetch exactly one fixed public source; never reads credentials from environment."""
    source_url = SOURCES[source]
    body = json.dumps({"url": source_url, "formats": ["markdown"], "onlyMainContent": True}).encode("utf-8")
    request = Request(ENDPOINT, data=body, headers={"Content-Type": "application/json"}, method="POST")
    opener = build_opener(_NoRedirect)
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            raw = _read_capped(response)
    except HTTPError as exc:
        code = exc.code
        try:
            exc.close()
        except Exception:
            pass
        reason = "upstream_http_" + str(code) if 400 <= code <= 599 else "redirect_blocked"
        return _envelope(source, "unavailable", reason)
    except (URLError, TimeoutError, OSError):
        return _envelope(source, "unavailable", "network_error")
    except ValueError:
        return _envelope(source, "unavailable", "response_too_large")

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _envelope(source, "unavailable", "invalid_json")
    if not isinstance(payload, dict):
        return _envelope(source, "unavailable", "invalid_response_shape")
    if payload.get("success") is not True:
        return _envelope(source, "unavailable", "upstream_unsuccessful")
    data = payload.get("data")
    if not isinstance(data, dict):
        return _envelope(source, "unavailable", "invalid_response_shape")
    metadata = data.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        return _envelope(source, "unavailable", "invalid_response_shape")
    if isinstance(metadata, dict):
        code = metadata.get("statusCode")
        if isinstance(code, bool) or (code is not None and not isinstance(code, int)):
            return _envelope(source, "unavailable", "invalid_response_shape")
        if code is not None and code >= 400:
            return _envelope(source, "unavailable", "source_http_error")
    markdown = data.get("markdown")
    if not isinstance(markdown, str):
        return _envelope(source, "unavailable", "invalid_response_shape")
    if not markdown.strip():
        return _envelope(source, "unavailable", "empty_markdown")
    return _envelope(source, "observed", "ok", markdown)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, choices=tuple(SOURCES))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    result = scrape(args.source)
    _atomic_json(args.output, result)
    return 0 if result["status"] == "observed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
