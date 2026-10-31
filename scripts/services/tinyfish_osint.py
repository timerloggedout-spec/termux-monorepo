#!/usr/bin/env python3
"""TinyFish Search/Fetch OSINT collector (public pages only).

[MUSEai]@{role:{scraping-tools}} — routes tinyfish-search ∘ tinyfish-fetch
from the data-ingestion set (primary-verified 2026-10-30):
  search: GET  https://api.search.tinyfish.ai?query=...   free 30/min, 500/hr
  fetch:  POST https://api.fetch.tinyfish.ai {"urls": []} free 150/min, 1000/day
Auth: X-API-Key header, key from env TINYFISH_API_KEY (Actions secret of the
same name; provisioned via the vault route, names-only everywhere else).
Public pages only — no login/session use (hosted login = session export).
Quota slice of record: github:scraping-tools (claim 6520959920).
While the secret is absent the collector prints DEFER and exits 0 with
--defer-ok, writing nothing (x-observatory pattern).
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

SEARCH_ENDPOINT = "https://api.search.tinyfish.ai"
FETCH_ENDPOINT = "https://api.fetch.tinyfish.ai"
SCHEMA = "tinyfish-osint/v1"
TIMEOUT_SECONDS = 60
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
FETCH_CHUNK = 50
# Free-tier caps (tinyfish.ai/pricing, verified 2026-10-30). A single run
# never plans past them; cadence-level pacing is the caller's job.
FETCH_DAILY_CAP = 1000
SEARCH_HOURLY_CAP = 500


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_public_url(url: str) -> str:
    """Return url if it is a public http(s) URL, else raise ValueError."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"unsupported scheme: {parsed.scheme!r}")
    host = parsed.hostname or ""
    if not host or host == "localhost":
        raise ValueError(f"non-public host: {host!r}")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None and not ip.is_global:
        raise ValueError(f"non-public IP host: {host!r}")
    return url


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _request(req: Request) -> dict:
    opener = build_opener(_NoRedirect)
    with opener.open(req, timeout=TIMEOUT_SECONDS) as resp:
        raw = resp.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("response exceeds size cap")
    return json.loads(raw.decode("utf-8"))


def run_search(api_key: str, query: str, include_domains: list[str]) -> dict:
    params = {"query": query}
    if include_domains:
        params["include_domains"] = ",".join(include_domains)
    req = Request(
        f"{SEARCH_ENDPOINT}?{urlencode(params)}",
        headers={"X-API-Key": api_key, "Accept": "application/json"},
        method="GET",
    )
    return _request(req)


def run_fetch(api_key: str, urls: list[str]) -> list[dict]:
    results = []
    for chunk in chunked(urls, FETCH_CHUNK):
        req = Request(
            FETCH_ENDPOINT,
            data=json.dumps({"urls": chunk}).encode("utf-8"),
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        results.append(_request(req))
    return results


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


def _envelope(mode: str, status: str, reason: str, request_info: dict,
              results=None) -> dict:
    envelope = {
        "schema": SCHEMA,
        "tool": "tinyfish",
        "mode": mode,
        "status": status,
        "reason": reason,
        "observed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "request": request_info,
        "quota_slice": "github:scraping-tools",
    }
    if results is not None:
        envelope["results"] = results
    return envelope


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["search", "fetch"], required=True)
    parser.add_argument("--query", help="search mode: query text")
    parser.add_argument("--include-domains", default="",
                        help="search mode: comma-separated domain allowlist")
    parser.add_argument("--url", action="append", default=[],
                        help="fetch mode: public URL (repeatable)")
    parser.add_argument("--output", required=True, help="envelope JSON output path")
    parser.add_argument("--defer-ok", action="store_true",
                        help="absent API key -> print DEFER, exit 0, write nothing")
    args = parser.parse_args(argv)

    api_key = os.environ.get("TINYFISH_API_KEY", "").strip()
    if not api_key:
        if args.defer_ok:
            print("DEFER: TINYFISH_API_KEY not provisioned; nothing written.")
            return 0
        print("ERROR: TINYFISH_API_KEY not set", file=sys.stderr)
        return 2

    if args.mode == "search":
        if not args.query:
            print("ERROR: --query required for search mode", file=sys.stderr)
            return 2
        request_info = {"query": args.query,
                        "include_domains": [d for d in args.include_domains.split(",") if d]}
        try:
            results = run_search(api_key, args.query, request_info["include_domains"])
        except (HTTPError, URLError, ValueError) as exc:
            _atomic_json(Path(args.output),
                         _envelope("search", "error", f"{type(exc).__name__}: {exc}", request_info))
            return 1
        _atomic_json(Path(args.output),
                     _envelope("search", "ok", "search completed", request_info, results))
        return 0

    # fetch mode
    if not args.url:
        print("ERROR: at least one --url required for fetch mode", file=sys.stderr)
        return 2
    if len(args.url) > FETCH_DAILY_CAP:
        print(f"ERROR: {len(args.url)} urls exceeds free daily cap {FETCH_DAILY_CAP}",
              file=sys.stderr)
        return 2
    try:
        urls = [validate_public_url(u) for u in args.url]
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    request_info = {"urls": urls, "chunks": len(list(chunked(urls, FETCH_CHUNK)))}
    try:
        results = run_fetch(api_key, urls)
    except (HTTPError, URLError, ValueError) as exc:
        _atomic_json(Path(args.output),
                     _envelope("fetch", "error", f"{type(exc).__name__}: {exc}", request_info))
        return 1
    _atomic_json(Path(args.output),
                 _envelope("fetch", "ok", "fetch completed", request_info, results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
