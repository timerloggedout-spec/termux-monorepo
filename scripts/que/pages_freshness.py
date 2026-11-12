#!/usr/bin/env python3
"""Page-freshness audit for the tracking pages (served SHA vs master, stamp age, HTTP).

  pages_freshness.py --config ops/challenge/qdesk-pages.json --out audit.json --alarms alarms.json
Needs GITHUB_REPOSITORY (+ GITHUB_TOKEN for commit dates). Stdlib only; reads public URLs.
"""
from __future__ import annotations

import argparse, json, os, re, sys, urllib.error, urllib.request
from datetime import datetime, timezone


def get(url: str, token: str | None = None, timeout: int = 20):
    h = {"User-Agent": "qdesk-pages-audit", "Cache-Control": "no-cache"}
    if token and "api.github.com" in url:
        h.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() or b""
    except Exception as e:  # network/transient
        return 0, str(e).encode()


def dig(obj, dotted: str):
    for part in dotted.split("."):
        obj = obj.get(part) if isinstance(obj, dict) else None
    return obj


def ts(s: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def audit(cfg: dict, repo: str, token: str | None, now: datetime) -> list[dict]:
    api = f"https://api.github.com/repos/{repo}"
    _, b = get(f"{api}/commits/master", token)
    head = json.loads(b or b"{}")
    head_sha, head_at = head.get("sha", ""), ts((head.get("commit") or {}).get("committer", {}).get("date", ""))
    cache: dict = {}

    def commit_at(sha):
        if sha not in cache:
            _, cb = get(f"{api}/commits/{sha}", token)
            cache[sha] = ts((json.loads(cb or b"{}").get("commit") or {}).get("committer", {}).get("date", ""))
        return cache[sha]

    out = []
    for p in cfg["pages"]:
        code, body = get(p["url"])
        row = {"name": p["name"], "url": p["url"], "http": code, "state": "ok", "served_sha": None, "detail": ""}
        expect = p.get("expect", [200])
        if code not in expect:
            row.update(state="broken", detail=f"HTTP {code}")
        elif p["kind"] == "http":
            row["detail"] = p.get("note", "")
            if code != 200:
                row["state"] = "retired"
        elif p["kind"] in ("sha", "ghpages_branch"):
            sha = None
            if p["kind"] == "sha":
                try:
                    sha = dig(json.loads(body), p["field"])
                except ValueError:
                    row.update(state="broken", detail="unparseable JSON")
            else:
                _, bb = get(f"{api}/commits/{p['branch']}", token)
                msg = (json.loads(bb or b"{}").get("commit") or {}).get("message", "")
                m = re.search(r"\b[0-9a-f]{40}\b", msg)
                sha = m.group(0) if m else None
            row["served_sha"] = sha
            if sha and head_sha and sha != head_sha:
                at = commit_at(sha)
                lag = (head_at - at).total_seconds() / 3600 if at and head_at else None
                age = (now - at).total_seconds() / 3600 if at else None
                row["lag_hours"] = round(lag, 1) if lag is not None else None
                row["detail"] = f"serves {sha[:7]} ({age:.0f}h old), master {head_sha[:7]}" if age is not None else f"serves {sha[:7]}"
                if lag is not None and lag > p.get("max_lag_hours", 36):
                    row["state"] = "stale"
            elif not sha and row["state"] == "ok":
                row.update(state="broken", detail="no served SHA stamp")
            else:
                row["detail"] = "serves master head"
        elif p["kind"] == "stamp":
            try:
                g = ts(dig(json.loads(body), p["field"]) or "")
            except ValueError:
                g = None
            if not g:
                row.update(state="broken", detail="no generated_at stamp")
            else:
                age = (now - g).total_seconds() / 3600
                row["detail"] = f"generated {age:.0f}h ago"
                if age > p.get("max_age_hours", 48):
                    row["state"] = "stale"
        if p.get("fix"):
            row["fix"] = p["fix"]
        out.append(row)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ops/challenge/qdesk-pages.json")
    ap.add_argument("--out")
    ap.add_argument("--alarms")
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    rows = audit(json.load(open(a.config)), os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo"),
                 os.environ.get("GITHUB_TOKEN"), now)
    bad = [r for r in rows if r["state"] in ("stale", "broken")]
    for r in rows:
        level = "warning" if r in bad else "notice"
        print(f"::{level} title=page {r['state']}::{r['name']} HTTP {r['http']} {r['detail']}"[:480])
    if a.out:
        json.dump({"schema": "qdesk.pages-audit.v1", "generated_at": now.isoformat(), "pages": rows}, open(a.out, "w"), indent=1)
    if a.alarms:
        day = now.strftime("%Y-%m-%d")
        json.dump([{"key": "qdesk-page:" + re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-") + ":" + day,
                    "title": f"Tracking page {r['state']}: {r['name']}", "priority": "P1",
                    "why": f"{r['url']} HTTP {r['http']} {r['detail']} {r.get('fix', '')}".strip()} for r in bad],
                  open(a.alarms, "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
