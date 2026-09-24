#!/usr/bin/env python3
"""Lane-matrix recursive sweep — age + disposition inventory for open PRs.

Observer + artifact writer. Does NOT merge, close, rebase, or force-push.
Produces docs/ops/generated/lane-matrix-status.json (+ optional markdown).
#175 comments are opt-in only (--comment-175). The board is the artifact.

Agent-Identity: Grok (Administrator)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "lane-matrix-sweep/v1"
ISSUE_175 = 175
MARKER = "<!-- lane-matrix-sweep:v1 -->"
DEBOUNCE_HOURS = 11

ML_WHOLESALE = {432, 549, 601}
KEEP_ALIVE_ML = {682}
MINESWEEPER_HINT = re.compile(r"jules|dashboard|89.?file|minesweeper", re.I)
SECURITY_HINT = re.compile(r"sentinel|symlink|sec\(|security|chmod", re.I)
SESSION_HINT = re.compile(r"ops\(session\)|ops\(skills\)|session record|LANE-MATRIX|lane-matrix", re.I)
BOT_LOGINS = (
    "google-labs-jules",
    "github-actions",
    "dependabot",
    "renovate",
    "coderabbitai",
    "devin-ai",
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _days_open(created: str | None, now: datetime) -> float:
    ts = _parse_ts(created)
    if not ts:
        return -1.0
    return max(0.0, (now - ts).total_seconds() / 86400.0)


def _age_bucket(days: float) -> str:
    if days < 0:
        return "unknown"
    if days >= 40:
        return "ancient"
    if days >= 20:
        return "stale"
    if days >= 7:
        return "mid"
    return "fresh"


def _is_bot(login: str | None) -> bool:
    l = (login or "").lower()
    return any(b in l for b in BOT_LOGINS)


def classify_pr(pr: dict[str, Any], master_sha: str, now: datetime) -> dict[str, Any]:
    number = int(pr.get("number") or 0)
    title = pr.get("title") or ""
    user = (pr.get("user") or {}).get("login") or ""
    draft = bool(pr.get("draft"))
    base_ref = (pr.get("base") or {}).get("ref") or ""
    base_sha = (pr.get("base") or {}).get("sha") or ""
    head_ref = (pr.get("head") or {}).get("ref") or ""
    head_sha = (pr.get("head") or {}).get("sha") or ""
    mergeable_state = pr.get("mergeable_state") or "unknown"
    changed_files = pr.get("changed_files")
    if changed_files is None:
        changed_files = -1
    days = _days_open(pr.get("created_at"), now)
    bucket = _age_bucket(days)

    wrong_base = base_ref not in ("", "master")
    dirty = mergeable_state in ("dirty", "blocked") or pr.get("mergeable") is False
    mega = isinstance(changed_files, int) and changed_files >= 40
    bot = _is_bot(user)

    reasons: list[str] = []
    lane = "OBSERVE"

    if number in KEEP_ALIVE_ML:
        lane = "WAIT"
        reasons.append("ml-keep-alive-rebase-required")
    elif number in ML_WHOLESALE:
        lane = "EXTRACT"
        reasons.append("ml-wholesale-no-go")
    elif SESSION_HINT.search(title):
        lane = "SUPERSEDE"
        reasons.append("session-record-not-a-promote-object")
    elif wrong_base:
        lane = "HOLD"
        reasons.append(f"wrong-base:{base_ref}")
    elif draft:
        lane = "HOLD"
        reasons.append("draft")
    elif mega or (bot and dirty and isinstance(changed_files, int) and changed_files >= 20):
        lane = "EXTRACT"
        reasons.append("minesweeper-or-mega")
    elif SECURITY_HINT.search(title) and dirty:
        lane = "WAIT"
        reasons.append("security-extract-wait-dual-gate")
    elif dirty:
        lane = "HOLD"
        reasons.append(f"dirty:{mergeable_state}")
    elif bot:
        lane = "OBSERVE"
        reasons.append("bot-observe")
    elif days >= 40:
        lane = "OBSERVE"
        reasons.append("ancient-no-auto-promote")
    else:
        lane = "OBSERVE"
        reasons.append(f"state:{mergeable_state}")

    if MINESWEEPER_HINT.search(title) and lane == "OBSERVE":
        lane = "EXTRACT"
        reasons.append("minesweeper-title")

    return {
        "number": number,
        "title": title,
        "user": user,
        "bot": bot,
        "draft": draft,
        "base_ref": base_ref,
        "base_sha": base_sha[:12],
        "head_ref": head_ref,
        "head_sha": head_sha[:12],
        "mergeable_state": mergeable_state,
        "changed_files": changed_files,
        "created_at": pr.get("created_at"),
        "updated_at": pr.get("updated_at"),
        "days_open": round(days, 2),
        "age_bucket": bucket,
        "lane": lane,
        "reasons": reasons,
        "html_url": pr.get("html_url"),
    }


def gh_api(path: str, token: str, accept: str = "application/vnd.github+json") -> Any:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "termux-monorepo-lane-matrix-sweep",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def gh_paginate_prs(owner: str, repo: str, token: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    page = 1
    while page <= 10:
        data = gh_api(
            f"/repos/{owner}/{repo}/pulls?state=open&sort=created&direction=asc&per_page=100&page={page}",
            token,
        )
        if not isinstance(data, list) or not data:
            break
        out.extend(data)
        if len(data) < 100:
            break
        page += 1
    return out


def post_issue_comment(owner: str, repo: str, issue: int, body: str, token: str) -> None:
    payload = json.dumps({"body": body}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{issue}/comments",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "termux-monorepo-lane-matrix-sweep",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        resp.read()


def list_issue_comments(owner: str, repo: str, issue: int, token: str) -> list[dict[str, Any]]:
    data = gh_api(
        f"/repos/{owner}/{repo}/issues/{issue}/comments?per_page=50&sort=created&direction=desc",
        token,
    )
    return data if isinstance(data, list) else []


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Lane matrix status ({payload['observed_at']})",
        "",
        f"- Master: `{payload['master_sha']}`",
        f"- Open PRs: **{payload['counts']['open_prs']}**",
        f"- Oldest: #{payload['oldest']['number']} ({payload['oldest']['days_open']}d) — {payload['oldest']['title'][:80]}",
        "",
        "| Lane | Count |",
        "|------|------:|",
    ]
    for lane, count in sorted(payload["counts"]["by_lane"].items()):
        lines.append(f"| {lane} | {count} |")
    lines.extend(["", "| Age bucket | Count |", "|------------|------:|"])
    for bucket, count in sorted(payload["counts"]["by_age"].items()):
        lines.append(f"| {bucket} | {count} |")
    lines.extend(
        [
            "",
            "## Tip lanes (non-OBSERVE first)",
            "",
            "| PR | Days | Lane | Reasons | Title |",
            "|---:|-----:|------|---------|-------|",
        ]
    )
    prioritized = sorted(
        payload["prs"],
        key=lambda r: (
            0 if r["lane"] != "OBSERVE" else 1,
            -r["days_open"],
            r["number"],
        ),
    )
    for row in prioritized[:40]:
        reasons = ", ".join(row["reasons"][:3])
        title = (row["title"] or "").replace("|", "/")[:50]
        lines.append(
            f"| #{row['number']} | {row['days_open']} | {row['lane']} | {reasons} | {title} |"
        )
    lines.append("")
    lines.append(
        "Observer only: does not merge. Dual-gate remains promote authority. Age alone ≠ promote."
    )
    return "\n".join(lines) + "\n"


def build_pulse(payload: dict[str, Any]) -> str:
    by_lane = payload["counts"]["by_lane"]
    oldest = payload["oldest"]
    return "\n".join(
        [
            MARKER,
            f"## Lane-matrix sweep pulse — {payload['observed_at']}",
            "",
            f"**Master:** `{payload['master_sha']}` · **Open PRs:** {payload['counts']['open_prs']}",
            f"**Oldest open PR:** #{oldest['number']} — **{oldest['days_open']}d** — {oldest['title'][:70]}",
            "",
            "| Lane | n |",
            "|------|--:|",
            *[f"| {k} | {v} |" for k, v in sorted(by_lane.items())],
            "",
            "Artifact: `docs/ops/generated/lane-matrix-status.json`",
            "Rules: dual-gate only; age ≠ promote; session pulses SUPERSEDE; no #175 heartbeat.",
            "",
            "Agent-Identity: lane-matrix-sweep (GHA)",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lane-matrix recursive sweep")
    parser.add_argument("--owner", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "timerloggedout-spec"))
    parser.add_argument(
        "--repo",
        default=(os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo").split("/")[-1]),
    )
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "")
    parser.add_argument("--master-sha", default=os.environ.get("GITHUB_SHA", "unknown"))
    parser.add_argument("--json-out", default="docs/ops/generated/lane-matrix-status.json")
    parser.add_argument("--md-out", default="docs/ops/generated/lane-matrix-status.md")
    parser.add_argument("--comment-175", action="store_true", help="Opt-in pulse on #175 (off by default)")
    parser.add_argument("--force-comment", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not args.token and not args.dry_run:
        print("GITHUB_TOKEN required unless --dry-run", file=sys.stderr)
        return 2

    now = _now()
    if args.dry_run:
        prs_raw: list[dict[str, Any]] = []
    else:
        try:
            prs_raw = gh_paginate_prs(args.owner, args.repo, args.token)
        except urllib.error.HTTPError as exc:
            print(f"API error listing PRs: {exc}", file=sys.stderr)
            return 1

    rows = [classify_pr(pr, args.master_sha, now) for pr in prs_raw]
    by_lane: dict[str, int] = {}
    by_age: dict[str, int] = {}
    for row in rows:
        by_lane[row["lane"]] = by_lane.get(row["lane"], 0) + 1
        by_age[row["age_bucket"]] = by_age.get(row["age_bucket"], 0) + 1

    if rows:
        oldest = max(rows, key=lambda r: r["days_open"])
    else:
        oldest = {"number": 0, "days_open": 0, "title": "(none)", "lane": "OBSERVE"}

    payload = {
        "schema": SCHEMA,
        "observed_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository": f"{args.owner}/{args.repo}",
        "master_sha": args.master_sha,
        "counts": {"open_prs": len(rows), "by_lane": by_lane, "by_age": by_age},
        "oldest": {
            "number": oldest["number"],
            "days_open": oldest["days_open"],
            "title": oldest.get("title", ""),
            "lane": oldest.get("lane", "OBSERVE"),
        },
        "prs": rows,
        "rules": {
            "promote": "dual-gate only (hygiene+portability + termux_smoke)",
            "age_alone": False,
            "vercel_rate_limit": "non-gate",
            "session_pulses": "SUPERSEDE",
            "issue_175_comments": "opt-in only",
            "ml_wholesale": sorted(ML_WHOLESALE),
            "ml_keep_alive": sorted(KEEP_ALIVE_ML),
        },
    }

    json_path = Path(args.json_out)
    md_path = Path(args.md_out)
    if not args.dry_run:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        md_path.write_text(build_markdown(payload), encoding="utf-8")
        print(f"wrote {json_path} ({len(rows)} PRs)")
        print(f"wrote {md_path}")
    else:
        print(json.dumps({"dry_run": True, "counts": payload["counts"]}, indent=2))

    if args.comment_175 and not args.dry_run:
        try:
            comments = list_issue_comments(args.owner, args.repo, ISSUE_175, args.token)
            prior = next((c for c in comments if MARKER in (c.get("body") or "")), None)
            if prior and not args.force_comment:
                prior_ts = _parse_ts(prior.get("created_at"))
                if prior_ts and (now - prior_ts).total_seconds() < DEBOUNCE_HOURS * 3600:
                    print(f"#175 debounced ({DEBOUNCE_HOURS}h)")
                else:
                    post_issue_comment(args.owner, args.repo, ISSUE_175, build_pulse(payload), args.token)
                    print("posted #175 pulse")
            else:
                post_issue_comment(args.owner, args.repo, ISSUE_175, build_pulse(payload), args.token)
                print("posted #175 pulse")
        except urllib.error.HTTPError as exc:
            print(f"comment failed: {exc}", file=sys.stderr)
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
