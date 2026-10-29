#!/usr/bin/env python3
"""X (Twitter) signal harvest — the Social Observatory collector.

Programmatic only: X API v2, OAuth 2.0 *user context* (app-only bearer is
rejected by both endpoints: liked_tweets needs like.read, bookmarks needs
bookmark.read; scopes tweet.read + users.read + offline.access for refresh).

Signals are the account owner's own Likes and Bookmarks, treated as
research signals (never adoption orders), classified into planes:

- ``marketing`` — carries a fleet/project signal (termux-monorepo,
  ``t3mpu``/tempux monorepo marketing, 4n0n, help-wanted, the owner handle)
- ``personal``  — no marketing signal (deterministic inference, recorded
  in ``plane_basis``; owner overrides win, see load_overrides)

Privacy rule: Bookmarks are private on X. Bookmark records are
METADATA-ONLY (id, author, url, timestamps, metrics, a one-way text hash
for change detection) — never the tweet text. Likes are public on X, so
like records may carry a short text excerpt.

No token -> DEFER: with ``--defer-ok`` the collector prints a DEFER
receipt and exits 0 without writing anything (workflow stays green,
index untouched). The token is an owner provisioning item; the secret
name is X_OAUTH2_USER_TOKEN and it is NOT provisioned yet.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

API = "https://api.x.com/2"
UA = "termux-monorepo-x-observatory/1.0"
SCHEMA_VERSION = "x-index/v1"
MAX_PAGES = 20  # bookmarks endpoint caps at the 800 most recent
RETRIES = 3

MARKETING_TERMS = (
    "termux", "monorepo", "timerloggedout", "4n0n", "t3mpu", "t3πmu",
    "tempux", "help-wanted", "help wanted", "monorep0",
)


class XHttpError(RuntimeError):
    def __init__(self, code: int, path: str):
        super().__init__(f"HTTP {code} for {path}")
        self.code = code
        self.path = path


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_json(path: str, token: str, params: dict[str, Any] | None = None) -> Any:
    query = "?" + urllib.parse.urlencode(params or {}) if params else ""
    req = urllib.request.Request(API + path + query, headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": UA,
    })
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:  # nosec B310: fixed API host
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt != RETRIES - 1:
                retry_after = exc.headers.get("Retry-After")
                delay = min(int(retry_after), 60) if retry_after and retry_after.isdigit() else 2 ** attempt
                time.sleep(delay)
                continue
            raise XHttpError(exc.code, path) from exc
        except (urllib.error.URLError, TimeoutError):
            if attempt == RETRIES - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"X API request failed: {path}")


def classify_plane(text: str, author_handle: str, own_handle: str | None,
                   overrides: dict[str, str], tweet_id: str) -> tuple[str, str]:
    """Deterministic plane classification; the basis is recorded so the
    inference is auditable. Owner overrides always win."""
    if tweet_id in overrides:
        return overrides[tweet_id], "owner_override"
    hay = f"{text} @{author_handle}".lower()
    for term in MARKETING_TERMS:
        if term in hay:
            return "marketing", f"term:{term}"
    if own_handle and author_handle.lower() == own_handle.lower():
        return "marketing", "author_is_account_owner"
    return "personal", "default_no_marketing_signal"


def normalize(tweet: dict[str, Any], users: dict[str, dict[str, Any]], signal: str,
              own_handle: str | None, overrides: dict[str, str], captured_at: str) -> dict[str, Any]:
    tid = str(tweet.get("id"))
    author = users.get(str(tweet.get("author_id")), {})
    handle = author.get("username") or ""
    text = tweet.get("text") or ""
    plane, basis = classify_plane(text, handle, own_handle, overrides, tid)
    metrics = tweet.get("public_metrics") or {}
    return {
        "id": f"x:tweet:{tid}",
        "tweet_id": tid,
        "url": f"https://x.com/{handle}/status/{tid}" if handle else f"https://x.com/i/status/{tid}",
        "author_handle": handle,
        "author_name": author.get("name"),
        "signals": [signal],
        "tweet_created_at": tweet.get("created_at"),
        "first_captured_at": captured_at,
        "plane": plane,
        "plane_basis": basis,
        # Bookmarks are private on X: metadata only, never the text.
        "text_excerpt": (text[:280] if signal == "like" else None),
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None,
        "metrics": {"like_count": metrics.get("like_count", 0),
                    "retweet_count": metrics.get("retweet_count", 0)},
    }


def merge_records(fetched: list[dict[str, Any]], previous: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for rec in previous:
        merged[rec["tweet_id"]] = dict(rec)
    for rec in fetched:
        tid = rec["tweet_id"]
        if tid in merged:
            old = merged[tid]
            rec = dict(rec)
            rec["signals"] = sorted(set(old.get("signals") or []) | set(rec["signals"]))
            rec["first_captured_at"] = old.get("first_captured_at") or rec["first_captured_at"]
            # A record that has ever been a like keeps its excerpt rule from
            # the like fetch; bookmark-only stays metadata-only.
            if "like" not in rec["signals"]:
                rec["text_excerpt"] = None
            elif old.get("text_excerpt"):
                rec["text_excerpt"] = old["text_excerpt"]
            merged[tid] = rec
        else:
            merged[tid] = rec
    return sorted(merged.values(), key=lambda r: (r["author_handle"].lower(), r["tweet_id"]))


def compute_delta(previous: list[dict[str, Any]] | None, records: list[dict[str, Any]]) -> dict[str, Any]:
    if previous is None:
        return {"available": False, "added": [], "removed": [], "signal_changed": []}
    prev = {r["tweet_id"]: r for r in previous}
    cur = {r["tweet_id"]: r for r in records}
    changed = []
    for tid in sorted(set(prev) & set(cur)):
        before = sorted(prev[tid].get("signals") or [])
        after = sorted(cur[tid].get("signals") or [])
        if before != after:
            changed.append({"tweet_id": tid, "from": before, "to": after})
    return {"available": True, "added": sorted(set(cur) - set(prev)),
            "removed": sorted(set(prev) - set(cur)), "signal_changed": changed}


def snapshot_hash(records: list[dict[str, Any]]) -> str:
    stable = [{k: v for k, v in r.items() if k not in ("metrics", "first_captured_at")} for r in records]
    canonical = json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_payload(account: dict[str, Any] | None, records: list[dict[str, Any]], observed_at: str,
                  delta: dict[str, Any] | None = None, status: str = "ok") -> dict[str, Any]:
    counts = {"likes": 0, "bookmarks": 0, "both": 0, "marketing": 0, "personal": 0, "total": len(records)}
    for r in records:
        sig = set(r.get("signals") or [])
        if "like" in sig:
            counts["likes"] += 1
        if "bookmark" in sig:
            counts["bookmarks"] += 1
        if len(sig) > 1:
            counts["both"] += 1
        counts[r["plane"]] = counts.get(r["plane"], 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "builder": "termux-monorepo.x_observatory@1.0",
        "observed_at": observed_at,
        "status": status,
        "account": account,
        "snapshot_hash": snapshot_hash(records),
        "counts": counts,
        "delta": delta if delta is not None else {"available": False, "added": [], "removed": [], "signal_changed": []},
        "records": records,
    }


def markdown(payload: dict[str, Any]) -> str:
    lines = ["# X (Twitter) Observatory — projection", "",
             "> Canonical data lives in `workspace/llm_map/social/x-index.json`; this file is a navigation projection. "
             "Signals are research signals, never adoption orders. Bookmark records are metadata-only (bookmarks are private on X).", "",
             f"Observed: `{payload['observed_at']}` · Status: `{payload['status']}`", ""]
    acct = payload.get("account") or {}
    if acct:
        lines.extend([f"Account: `@{acct.get('username')}` (id `{acct.get('id')}`)", ""])
    lines.extend(["## Counts", ""])
    for key, value in payload["counts"].items():
        lines.append(f"- **{key}:** {value}")
    delta = payload.get("delta") or {}
    lines.extend(["", "## Changes since previous snapshot", ""])
    if not delta.get("available"):
        lines.append("_No previous snapshot available for comparison._")
    else:
        lines.append(f"- **Added ({len(delta.get('added') or [])}):** {', '.join(delta.get('added') or []) or '—'}")
        lines.append(f"- **Removed ({len(delta.get('removed') or [])}):** {', '.join(delta.get('removed') or []) or '—'}")
        lines.append(f"- **Signal changed ({len(delta.get('signal_changed') or [])})**")
    for plane in ("marketing", "personal"):
        rows = [r for r in payload["records"] if r["plane"] == plane]
        lines.extend(["", f"## {plane.capitalize()} plane ({len(rows)})", "",
                      "| Tweet | Author | Signals | Captured |", "|---|---|---|---|"])
        for r in rows:
            lines.append(f"| [{r['tweet_id']}]({r['url']}) | @{r['author_handle']} | {', '.join(r['signals'])} | {r['first_captured_at']} |")
    lines.append("")
    return "\n".join(lines)


def load_overrides(path: Path | None) -> dict[str, str]:
    if path and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {str(k): str(v) for k, v in (data.get("overrides") or {}).items()}
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def harvest(fetch: Callable[..., Any], token: str, overrides: dict[str, str],
            captured_at: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    me = fetch("/users/me", token, {"user.fields": "username,name"})
    account = (me or {}).get("data") or {}
    uid = account.get("id")
    if not uid:
        raise RuntimeError("could not resolve the authenticated X user")
    own_handle = account.get("username")
    params = {"max_results": 100, "tweet.fields": "created_at,author_id,public_metrics",
              "expansions": "author_id", "user.fields": "username,name"}
    fetched: list[dict[str, Any]] = []
    for signal, sub in (("like", "liked_tweets"), ("bookmark", "bookmarks")):
        next_token: str | None = None
        for _ in range(MAX_PAGES):
            page_params = dict(params)
            if next_token:
                page_params["pagination_token"] = next_token
            payload = fetch(f"/users/{uid}/{sub}", token, page_params)
            includes = payload.get("includes") or {}
            users = {str(u.get("id")): u for u in includes.get("users") or []}
            for tweet in payload.get("data") or []:
                fetched.append(normalize(tweet, users, signal, own_handle, overrides, captured_at))
            next_token = (payload.get("meta") or {}).get("next_token")
            if not next_token:
                break
    return {"id": str(uid), "username": own_handle, "name": account.get("name")}, fetched


def main(argv: list[str] | None = None, fetch: Callable[..., Any] = get_json) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--overrides", type=Path)
    parser.add_argument("--token-env", default="X_OAUTH2_USER_TOKEN")
    parser.add_argument("--defer-ok", action="store_true",
                        help="missing token or auth failure -> DEFER receipt, exit 0, write nothing")
    args = parser.parse_args(argv)
    token = os.environ.get(args.token_env)
    if not token:
        print(f"DEFER: {args.token_env} not provisioned; X harvest skipped (owner provisioning item)")
        return 0 if args.defer_ok else 2
    overrides = load_overrides(args.overrides)
    try:
        account, fetched = harvest(fetch, token, overrides, now())
    except XHttpError as exc:
        print(f"DEFER: X API auth/read failed ({exc}); harvest skipped")
        return 0 if args.defer_ok else 1
    previous: dict[str, Any] = {}
    if args.output.exists():
        try:
            previous = json.loads(args.output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
    records = merge_records(fetched, previous.get("records") or [])
    digest = snapshot_hash(records)
    observed_at = previous.get("observed_at") if previous.get("snapshot_hash") == digest else now()
    delta = compute_delta(previous.get("records"), records)
    payload = build_payload(account, records, observed_at, delta=delta, status="ok")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(payload), encoding="utf-8")
    print(json.dumps(payload["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
