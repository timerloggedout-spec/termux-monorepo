#!/usr/bin/env python3
"""archw1z — Manus full session exporter for ML pipeline (web-only, not Open API v2)."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

BASE = "https://api.manus.im"
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)
DEFAULT_HEADERS = {
    "accept": "application/json",
    "user-agent": UA,
    "referer": "https://manus.im/",
    "origin": "https://manus.im",
    "x-client-type": "web",
    "x-client-locale": "en",
    "x-client-timezone": "UTC",
    "x-client-timezone-offset": "0",
}


def _http_get(url: str, headers: dict, cookies: dict | None) -> Any:
    try:
        from curl_cffi import requests as creq

        r = creq.get(
            url,
            headers=headers,
            cookies=cookies or {},
            impersonate="chrome131",
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    except ImportError:
        import urllib.request

        req = urllib.request.Request(url, headers=headers)
        if cookies:
            req.add_header("cookie", "; ".join(f"{k}={v}" for k, v in cookies.items()))
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())


def parse_session_id(raw: str) -> str:
    if raw.startswith("http"):
        path = urlparse(raw).path
        m = re.search(r"/(?:share|app)/([A-Za-z0-9_-]+)", path)
        if not m:
            raise SystemExit(f"cannot parse sessionId from URL: {raw}")
        return m.group(1)
    return raw.strip()


def load_cookies(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    p = Path(path).expanduser()
    if not p.exists():
        print(f"warn: cookie file missing {p}", file=sys.stderr)
        return {}
    data = json.loads(p.read_text())
    items = data.get("cookies", data) if isinstance(data, dict) else data
    out: dict[str, str] = {}
    if isinstance(items, list):
        for c in items:
            name, val = c.get("name"), c.get("value")
            if name and val is not None:
                out[name] = val
    elif isinstance(items, dict):
        out = {str(k): str(v) for k, v in items.items()}
    return out


def fetch_session(session_id: str, stype: str, headers: dict, cookies: dict) -> dict:
    url = f"{BASE}/api/chat/getSessionV2?sessionId={session_id}&type={stype}&getFirstSegment=true"
    return _http_get(url, headers, cookies)


def fetch_files(session_id: str, stype: str, headers: dict, cookies: dict) -> dict:
    url = f"{BASE}/api/chat/getSessionFilesV2?sessionId={session_id}&type={stype}"
    return _http_get(url, headers, cookies)


def fetch_cascade(session_id: str, stype: str, headers: dict, cookies: dict) -> dict:
    url = f"{BASE}/api/chat/listCascadeJobs?sessionId={session_id}&type={stype}&includeActive=true"
    try:
        return _http_get(url, headers, cookies)
    except Exception as e:
        print(f"warn: cascade fetch failed: {e}", file=sys.stderr)
        return {}


def ts_iso(ms: int | float | None) -> str | None:
    if ms is None:
        return None
    try:
        return datetime.fromtimestamp(float(ms) / 1000.0, tz=timezone.utc).isoformat()
    except (OSError, ValueError, TypeError):
        return None


def flatten_events(session: dict, session_id: str) -> list[dict]:
    data = session.get("data") or session
    rows: list[dict] = []
    for seg_i, seg in enumerate(data.get("segments") or []):
        for ev in seg.get("events") or []:
            ts = ev.get("timestamp")
            rows.append({
                "schema_version": 1,
                "source": "manus.im/web",
                "session_id": session_id,
                "segment_index": seg_i,
                "event_id": ev.get("id"),
                "event_type": ev.get("type"),
                "timestamp_ms": ts,
                "timestamp_iso": ts_iso(ts),
                "payload": ev,
            })
    meta_keys = ("id", "title", "createdAt", "updatedAt", "isShared", "agentTaskMode", "userStatus")
    if any(k in data for k in meta_keys):
        meta = {k: data.get(k) for k in meta_keys if k in data}
        created = data.get("createdAt")
        rows.insert(0, {
            "schema_version": 1,
            "source": "manus.im/web",
            "session_id": session_id,
            "segment_index": -1,
            "event_id": f"meta:{session_id}",
            "event_type": "session_meta",
            "timestamp_ms": created,
            "timestamp_iso": ts_iso(created),
            "payload": meta,
        })
    rows.sort(key=lambda r: (r.get("timestamp_ms") is None, r.get("timestamp_ms") or 0))
    return rows


def files_as_events(files_body: dict, session_id: str) -> list[dict]:
    data = files_body.get("data") or files_body
    items = data if isinstance(data, list) else data.get("files") or data.get("items") or []
    rows: list[dict] = []
    if not isinstance(items, list):
        return rows
    for f in items:
        ts = f.get("lastUpdatedAt") or f.get("timestamp")
        if ts is None and isinstance(f.get("raw"), list) and f["raw"]:
            ts = f["raw"][0].get("timestamp")
        rows.append({
            "schema_version": 1,
            "source": "manus.im/web",
            "session_id": session_id,
            "segment_index": None,
            "event_id": f.get("id"),
            "event_type": "sandbox_file",
            "timestamp_ms": ts,
            "timestamp_iso": ts_iso(ts),
            "payload": f,
        })
    return rows


def cascade_as_events(cascade_body: dict, session_id: str) -> list[dict]:
    data = cascade_body.get("data") or cascade_body
    jobs = data if isinstance(data, list) else data.get("jobs") or data.get("items") or []
    rows: list[dict] = []
    if not isinstance(jobs, list):
        return rows
    for j in jobs:
        ts = j.get("createdAt") or j.get("timestamp") or j.get("updatedAt")
        rows.append({
            "schema_version": 1,
            "source": "manus.im/web",
            "session_id": session_id,
            "segment_index": None,
            "event_id": j.get("id") or j.get("jobId"),
            "event_type": "cascade_job",
            "timestamp_ms": ts,
            "timestamp_iso": ts_iso(ts),
            "payload": j,
        })
    return rows


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Manus Computer + chat timeline → JSONL")
    ap.add_argument("--session", help="sessionId")
    ap.add_argument("--url", help="manus.im/share/... or /app/... URL")
    ap.add_argument("--type", default="shared")
    ap.add_argument("--cookies", default=os.environ.get("MANUS_COOKIES"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--raw-dir", default=None)
    ap.add_argument("--client-id", default=None)
    args = ap.parse_args()
    raw = args.session or args.url
    if not raw:
        ap.error("need --session or --url")
    session_id = parse_session_id(raw)
    headers = dict(DEFAULT_HEADERS)
    if args.client_id:
        headers["x-client-id"] = args.client_id
    cookies = load_cookies(args.cookies)
    print(f"[manus] session={session_id} type={args.type}", file=sys.stderr)
    session = fetch_session(session_id, args.type, headers, cookies)
    files = fetch_files(session_id, args.type, headers, cookies)
    cascade = fetch_cascade(session_id, args.type, headers, cookies)
    if args.raw_dir:
        rd = Path(args.raw_dir)
        rd.mkdir(parents=True, exist_ok=True)
        (rd / f"{session_id}_session.json").write_text(json.dumps(session, indent=2), encoding="utf-8")
        (rd / f"{session_id}_files.json").write_text(json.dumps(files, indent=2), encoding="utf-8")
        (rd / f"{session_id}_cascade.json").write_text(json.dumps(cascade, indent=2), encoding="utf-8")
    rows = flatten_events(session, session_id)
    rows.extend(files_as_events(files, session_id))
    rows.extend(cascade_as_events(cascade, session_id))
    rows.sort(key=lambda r: (r.get("timestamp_ms") is None, r.get("timestamp_ms") or 0))
    out = Path(args.out) if args.out else Path("manus_export") / f"{session_id}.jsonl"
    write_jsonl(rows, out)
    hist = Counter(r["event_type"] for r in rows)
    print(f"[manus] wrote {len(rows)} events → {out}", file=sys.stderr)
    print(f"[manus] types: {dict(hist)}", file=sys.stderr)


if __name__ == "__main__":
    main()
