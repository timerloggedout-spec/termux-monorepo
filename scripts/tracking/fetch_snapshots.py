#!/usr/bin/env python3
"""Refresh the tracking observation snapshots (workflow-side, network).

Writes (stamped API reads — the surface-feeds observation pattern):
  scripts/tracking/pr_feed_snapshot.json
    {schema, read_at, merged[<=150 recent], open[<=200]} from the GitHub
    PR API using GH_TOKEN/GITHUB_TOKEN (in Actions: the workflow token).
  scripts/tracking/lane_events_snapshot.json
    {schema, read_at, status, count, events[<=200 latest]} from Neon
    lane_events via SQL-over-HTTP (Neon serverless endpoint derived from
    LANE_EVENTS_DATABASE_URL host). No secret set -> status=not_configured
    (a named gap in the feed, never a failure). Values are never printed.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "scripts" / "tracking"
REPO = os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gh(path: str, token: str):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "repo-tracking-collect"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def _slim(pr: dict, merged: bool) -> dict:
    return {
        "number": pr.get("number"), "title": pr.get("title"),
        "merged_at": pr.get("merged_at"), "updated_at": pr.get("updated_at"),
        "created_at": pr.get("created_at"),
        "merge_commit_sha": pr.get("merge_commit_sha"),
        "head_ref": (pr.get("head") or {}).get("ref"),
        "author": (pr.get("user") or {}).get("login"),
        "labels": [l.get("name") for l in pr.get("labels", []) if isinstance(l, dict)],
        "html_url": pr.get("html_url"), "merged": merged,
    }


def fetch_prs(token: str) -> dict:
    merged, page = [], 1
    while len(merged) < 150 and page <= 3:
        batch = _gh(f"/repos/{REPO}/pulls?state=closed&sort=updated&direction=desc"
                    f"&per_page=100&page={page}", token)
        for pr in batch:
            if pr.get("merged_at"):
                merged.append(_slim(pr, True))
        if len(batch) < 100:
            break
        page += 1
    open_prs, page = [], 1
    while len(open_prs) < 200 and page <= 2:
        batch = _gh(f"/repos/{REPO}/pulls?state=open&sort=updated&direction=desc"
                    f"&per_page=100&page={page}", token)
        open_prs += [_slim(pr, False) for pr in batch]
        if len(batch) < 100:
            break
        page += 1
    return {"schema": "tracking-pr-feed-snapshot/v1", "read_at": _now(),
            "repo": REPO, "merged": merged[:150], "open": open_prs[:200]}


def fetch_lane_events() -> dict:
    url = os.environ.get("LANE_EVENTS_DATABASE_URL", "").strip()
    base = {"schema": "tracking-lane-events-snapshot/v1", "read_at": _now(),
            "status": "not_configured", "count": None, "events": []}
    if not url:
        return base
    try:
        host = urllib.parse.urlparse(url).hostname
        if not host:
            base["status"] = "bad_url"
            return base
        query = ("SELECT lane, workflow, event_type, conclusion, subject_url, head_sha, "
                 "occurred_at::text AS occurred_at FROM lane_events "
                 "ORDER BY occurred_at DESC LIMIT 200")
        count_q = "SELECT count(*)::int AS n FROM lane_events"
        def _sql(q):
            req = urllib.request.Request(
                f"https://{host}/sql",
                data=json.dumps({"query": q, "params": []}).encode(), method="POST",
                headers={"Neon-Connection-String": url, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        rows = _sql(query).get("rows", [])
        cnt = _sql(count_q).get("rows", [{}])
        base.update({"status": "ok", "count": cnt[0].get("n") if cnt else None,
                     "events": rows})
        return base
    except Exception as e:  # never fail the collect; record the class only
        base["status"] = f"error:{type(e).__name__}"
        return base


def fetch_backup(token: str) -> dict:
    """Metadata-only extract of the private backup repo (owner order:
    the dashboard records the backups). Reads EXPORT.json (counts and
    gates only — never the manifest, never file paths), reports/*.json
    drill verdicts, and the export/drill commit subjects. On error the
    status records the class and the caller preserves last-good data."""
    repo = os.environ.get("BACKUP_REPO", "timerloggedout-spec/muse-vm-workspace-backup")
    base = {"schema": "tracking-backup-snapshot/v1", "read_at": _now(),
            "status": "ok", "repo": repo, "export": None, "drills": [], "commits": []}
    ex = _gh(f"/repos/{repo}/contents/EXPORT.json", token)
    import base64 as _b64
    ex_doc = json.loads(_b64.b64decode(ex["content"]))
    base["export"] = {"export_id": ex_doc.get("export_id"),
                      "exported_at": ex_doc.get("exported_at"),
                      "counts": ex_doc.get("counts"), "gates": ex_doc.get("gates")}
    try:
        listing = _gh(f"/repos/{repo}/contents/reports", token)
        for item in listing if isinstance(listing, list) else []:
            if item.get("type") == "file" and str(item.get("name", "")).endswith(".json"):
                doc = json.loads(_b64.b64decode(
                    _gh(f"/repos/{repo}/contents/{item['path']}", token)["content"]))
                doc["report"] = f"reports/{item['name']}"
                base["drills"].append(doc)
    except Exception:
        pass  # drills are enrichment; the export record stands without them
    for c in _gh(f"/repos/{repo}/commits?per_page=30", token):
        msg = (c.get("commit") or {}).get("message", "")
        if msg.startswith(("export ", "drill ", "init:")):
            base["commits"].append({"sha": c.get("sha"), "message": msg.splitlines()[0],
                                    "at": (c.get("commit") or {}).get("committer", {}).get("date")})
    return base


def main() -> int:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    OUT.mkdir(parents=True, exist_ok=True)
    if token:
        try:
            snap = fetch_prs(token)
            snap["status"] = "ok"
        except Exception as e:  # fail-soft, recorded (DEFER class: e.g.
            # GITHUB_TOKEN bucket exhausted by the merge-triggered workflow
            # storm). The generator names this as a gap; next run retries.
            msg = f"{type(e).__name__}: {str(e)[:160]}"
            print(f"::warning::pr feed fetch failed ({msg}); degraded snapshot written")
            snap = {"schema": "tracking-pr-feed-snapshot/v1", "read_at": _now(),
                    "repo": REPO, "status": f"error:{msg}", "merged": [], "open": []}
        (OUT / "pr_feed_snapshot.json").write_text(json.dumps(snap, indent=1) + "\n")
        print("pr_feed_snapshot refreshed")
    else:
        print("::warning::no GH token; pr snapshot untouched")
    (OUT / "lane_events_snapshot.json").write_text(json.dumps(fetch_lane_events(), indent=1) + "\n")
    print("lane_events_snapshot refreshed")
    bpath = OUT / "backup_snapshot.json"
    if token:
        try:
            bsnap = fetch_backup(token)
        except Exception as e:  # fail-soft: keep last-good data, stamp status
            prev = {}
            try:
                prev = json.loads(bpath.read_text())
            except Exception:
                pass
            bsnap = {"schema": "tracking-backup-snapshot/v1", "read_at": _now(),
                     "status": f"error:{type(e).__name__}: {str(e)[:120]}",
                     "repo": prev.get("repo"),
                     "export": prev.get("export"), "drills": prev.get("drills", []),
                     "commits": prev.get("commits", [])}
            print(f"::warning::backup fetch failed ({bsnap['status']}); last-good preserved")
        bpath.write_text(json.dumps(bsnap, indent=1) + "\n")
        print("backup_snapshot refreshed")
    else:
        print("::warning::no GH token; backup snapshot untouched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
