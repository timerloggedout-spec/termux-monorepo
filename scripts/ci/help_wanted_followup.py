#!/usr/bin/env python3
"""Foreign PR follow-up with dynamic re-engagement.

Beyond one-shot CHANGES_REQUESTED:
  - All open foreign PRs we authored
  - Re-engage when maintainer comments/reviews AFTER our last marker (stale days)
  - CONTRIBUTING.md recon + URLs from thread
  - Cooldown prevents spam; evidence for every decision

Excludes timerloggedout-spec/termux-monorepo.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from scripts.ci.help_wanted_foreign_recon import (
        extract_urls,
        fetch_contributing,
        format_recon_block,
    )
except ImportError:
    # Actions checkout root
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.ci.help_wanted_foreign_recon import (  # type: ignore
        extract_urls,
        fetch_contributing,
        format_recon_block,
    )

try:
    from scripts.ci import tribute_system1
except ImportError:  # pragma: no cover - Actions checkout root
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.ci import tribute_system1  # type: ignore

API = "https://api.github.com"
AUTHOR = os.environ.get("HELP_WANTED_AUTHOR", "timerloggedout-spec")
EXCLUDE_REPOS = {"timerloggedout-spec/termux-monorepo"}
TOKEN = (
    os.environ.get("OPERATOR_GITHUB_TOKEN")
    or os.environ.get("OPERATOR_TOKEN")
    or os.environ.get("ARCHWIZ_GITHUB_TOKEN")
    or os.environ.get("GITHUB_TOKEN")
    or ""
)
MARKER = "### Help-wanted follow-up — termux-monorepo"
# Min age of our last marker before re-commenting after new external activity
REENGAGE_HOURS = float(os.environ.get("HELP_WANTED_REENGAGE_HOURS", "18"))
# Stake PRs idle this long get a gentle nudge + CONTRIBUTING recon once per cooldown
STALE_IDLE_HOURS = float(os.environ.get("HELP_WANTED_STALE_IDLE_HOURS", "72"))
# Closed foreign PRs updated within this window are routed for a lesson (never posted on).
LESSON_DAYS = int(os.environ.get("HELP_WANTED_LESSON_DAYS", "14"))
# Actions that post a timing-based public comment; Tribute System 1 must allow them.
GATED_ACTIONS = {"reengage", "stale_nudge"}


def api(method: str, path: str, body: dict | None = None):
    url = path if path.startswith("http") else f"{API}{path}"
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "termux-help-wanted-followup",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"HTTP {e.code} {path}: {err[:400]}", file=sys.stderr)
        return e.code, {}


def parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _search_foreign_prs(qualifier: str) -> list[dict]:
    q = f"author:{AUTHOR} is:pr {qualifier} -repo:timerloggedout-spec/termux-monorepo"
    status, data = api("GET", f"/search/issues?q={urllib.parse.quote(q)}&per_page=40")
    if status != 200:
        return []
    items = []
    for it in data.get("items") or []:
        repo_url = it.get("repository_url") or ""
        parts = repo_url.rstrip("/").split("/")
        full = f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 else ""
        if full in EXCLUDE_REPOS:
            continue
        items.append(it)
    return items


def search_open_foreign_prs() -> list[dict]:
    return _search_foreign_prs("is:open")


def search_closed_foreign_prs(now: datetime | None = None) -> list[dict]:
    """Closed foreign PRs (merged or not) so every close is routed for a lesson."""
    since = ((now or datetime.now(timezone.utc)) - timedelta(days=LESSON_DAYS)).strftime("%Y-%m-%d")
    return _search_foreign_prs(f"is:closed closed:>={since}")


def hydrate_thread(full: str, number: int) -> dict | None:
    """Read-only System 1 hydration; None on any failure (callers fail closed)."""
    try:
        return tribute_system1.hydrate(full, number)
    except Exception as e:  # noqa: BLE001 - any read failure means "do not post"
        print(f"system1 hydrate fail {full}#{number}: {e}", file=sys.stderr)
        return None


def system1_allows_post(thread: dict | None) -> bool:
    """Gate for reengage/stale_nudge: post only when System 1 sees no decline/claim/close."""
    if not thread:
        return False
    try:
        return bool(tribute_system1.reengage_allowed(thread))
    except Exception as e:  # noqa: BLE001
        print(f"system1 route fail: {e}", file=sys.stderr)
        return False


def lesson_row(thread: dict, html: str, now: datetime) -> dict:
    r = tribute_system1.route(thread)
    return {
        "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kind": "followup_lesson",
        "issue": html,
        "ok": True,
        "lane": "help-wanted-followup",
        "foreign": True,
        "action": "lesson",
        "primary": r.get("primary"),
        "s1_action": r.get("action"),
        "rung": r.get("rung"),
        "prefilter_rules": r.get("prefilter_rules"),
        "delphi_signal": r.get("delphi_signal"),
    }


def recorded_lessons() -> set[str]:
    seen: set[str] = set()
    for path in Path("docs/ops/generated/help-wanted-evidence").glob("*.jsonl"):
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if '"followup_lesson"' in line:
                    seen.add(json.loads(line).get("issue") or "")
        except (OSError, ValueError):
            continue
    return seen


def load_thread(owner: str, repo: str, number: int) -> tuple[list[dict], list[dict]]:
    _, comments = api("GET", f"/repos/{owner}/{repo}/issues/{number}/comments?per_page=100")
    _, reviews = api("GET", f"/repos/{owner}/{repo}/pulls/{number}/reviews")
    return (comments if isinstance(comments, list) else []), (
        reviews if isinstance(reviews, list) else []
    )


MAINTAINER_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}


def filter_maintainer_activity(
    comments: list[dict], reviews: list[dict]
) -> tuple[list[dict], list[dict]]:
    """Discard participant/bot activity unless GitHub identifies maintainer access.

    GitHub's author_association is the evidence source; unknown association is
    deliberately not promoted to maintainer feedback.
    """
    def is_maintainer(event: dict) -> bool:
        return str(event.get("author_association") or "").upper() in MAINTAINER_ASSOCIATIONS

    return (
        [event for event in comments if is_maintainer(event)],
        [event for event in reviews if is_maintainer(event)],
    )


def last_marker_ts(comments: list[dict]) -> datetime | None:
    last = None
    for c in comments:
        if MARKER not in (c.get("body") or ""):
            continue
        ts = parse_ts(c.get("created_at"))
        if ts and (last is None or ts > last):
            last = ts
    return last


def latest_changes_requested(reviews: list[dict]) -> tuple[str | None, datetime | None, str]:
    for r in reversed(reviews or []):
        if r.get("state") == "CHANGES_REQUESTED":
            body = (r.get("body") or "").strip()
            user = (r.get("user") or {}).get("login")
            ts = parse_ts(r.get("submitted_at"))
            excerpt = body[:1500] + ("…" if len(body) > 1500 else "")
            summary = f"Latest **CHANGES_REQUESTED** by @{user}:\n\n> " + excerpt.replace(
                "\n", "\n> "
            )
            return user, ts, summary
    return None, None, ""


def latest_approval_ts(reviews: list[dict]) -> datetime | None:
    """Return the latest trusted maintainer approval, including empty-body reviews."""
    timestamps = [
        parse_ts(review.get("submitted_at"))
        for review in reviews or []
        if review.get("state") == "APPROVED"
    ]
    valid = [timestamp for timestamp in timestamps if timestamp is not None]
    return max(valid) if valid else None


def latest_maintainer_signal(
    comments: list[dict], reviews: list[dict], owner: str
) -> tuple[datetime | None, str, list[str]]:
    """Newest non-us human/bot-owner signal with body + URLs."""
    events: list[tuple[datetime, str, str]] = []
    for c in comments:
        login = ((c.get("user") or {}).get("login") or "").lower()
        if login in {AUTHOR.lower(), "github-actions[bot]"}:
            continue
        if MARKER in (c.get("body") or ""):
            continue
        ts = parse_ts(c.get("created_at"))
        if not ts:
            continue
        body = (c.get("body") or "").strip()
        if len(body) < 20:
            continue
        events.append((ts, login, body))
    for r in reviews:
        login = ((r.get("user") or {}).get("login") or "").lower()
        if login == AUTHOR.lower():
            continue
        ts = parse_ts(r.get("submitted_at"))
        if not ts:
            continue
        body = (r.get("body") or "").strip()
        if len(body) < 40:
            continue
        # Approval is tracked separately: it suppresses stale nudges but is not
        # a request to re-engage. Only comments and change requests are signals.
        if r.get("state") in ("CHANGES_REQUESTED", "COMMENTED"):
            events.append((ts, login, body))
    if not events:
        return None, "", []
    events.sort(key=lambda x: x[0])
    ts, login, body = events[-1]
    excerpt = body[:1200] + ("…" if len(body) > 1200 else "")
    summary = f"Latest thread signal by @{login} ({ts.isoformat()}):\n\n> " + excerpt.replace(
        "\n", "\n> "
    )
    return ts, summary, extract_urls(body)


def decide_action(
    marker_ts: datetime | None,
    signal_ts: datetime | None,
    changes_ts: datetime | None,
    pr_updated: datetime | None,
    now: datetime,
    approval_ts: datetime | None = None,
) -> str:
    """Return action: changes | reengage | stale_nudge | skip."""
    reengage_delta = timedelta(hours=REENGAGE_HOURS)
    stale_delta = timedelta(hours=STALE_IDLE_HOURS)

    # Fresh CHANGES_REQUESTED after last marker → act
    if changes_ts and (marker_ts is None or changes_ts > marker_ts):
        if marker_ts is None or (now - marker_ts) >= timedelta(hours=1):
            return "changes"

    # Maintainer signal after our marker + cooldown
    if signal_ts and (marker_ts is None or signal_ts > marker_ts):
        if marker_ts is None or (now - marker_ts) >= reengage_delta:
            return "reengage"

    # A stale nudge is only appropriate when no substantive maintainer
    # feedback/review exists. If feedback exists but predates our marker, the
    # next action is ours: adapt/validate the patch, not ask the maintainer again.
    # New feedback after the marker is handled by the reengage branch above.
    if signal_ts is None and changes_ts is None and approval_ts is None:
        if pr_updated and (now - pr_updated) >= stale_delta:
            if marker_ts is None or (now - marker_ts) >= stale_delta:
                return "stale_nudge"

    return "skip"


def post_followup(owner: str, repo: str, number: int, body: str) -> str | None:
    status, data = api(
        "POST", f"/repos/{owner}/{repo}/issues/{number}/comments", {"body": body}
    )
    if status in (200, 201):
        return data.get("html_url")
    return None


def append_evidence(rows: list[dict]) -> None:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = Path(f"docs/ops/generated/help-wanted-evidence/{day}.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")


def main() -> int:
    if not TOKEN:
        print("No token", file=sys.stderr)
        return 1
    now = datetime.now(timezone.utc)
    items = search_open_foreign_prs()
    print(f"found {len(items)} FOREIGN open PRs")
    rows: list[dict] = []

    # Closed foreign PRs: route through System 1 for a lesson. Never posted on.
    already = recorded_lessons()
    for it in search_closed_foreign_prs(now):
        html = it.get("html_url") or ""
        if html in already:
            continue
        parts = (it.get("repository_url") or "").rstrip("/").split("/")
        thread = hydrate_thread(f"{parts[-2]}/{parts[-1]}", int(it["number"]))
        if thread is None:
            continue
        try:
            rows.append(lesson_row(thread, html, now))
            print(f"lesson {html}")
        except Exception as e:  # noqa: BLE001
            print(f"lesson fail {html}: {e}", file=sys.stderr)

    for it in items:
        repo_url = it.get("repository_url") or ""
        parts = repo_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        number = int(it["number"])
        html = it.get("html_url")
        pr_updated = parse_ts(it.get("updated_at"))

        comments, reviews = load_thread(owner, repo, number)
        marker_ts = last_marker_ts(comments)
        maintainer_comments, maintainer_reviews = filter_maintainer_activity(comments, reviews)
        ch_user, changes_ts, changes_summary = latest_changes_requested(maintainer_reviews)
        signal_ts, signal_summary, signal_urls = latest_maintainer_signal(
            maintainer_comments, maintainer_reviews, owner
        )
        approval_ts = latest_approval_ts(maintainer_reviews)
        action = decide_action(
            marker_ts, signal_ts, changes_ts, pr_updated, now, approval_ts=approval_ts
        )

        if action == "skip":
            print(f"skip {html} (no new signal / cooldown)")
            rows.append(
                {
                    "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "kind": "followup_skip_cooldown",
                    "issue": html,
                    "ok": True,
                    "lane": "help-wanted-followup",
                    "foreign": True,
                    "action": "skip",
                }
            )
            continue

        if action in GATED_ACTIONS:
            thread = hydrate_thread(f"{owner}/{repo}", number)
            if not system1_allows_post(thread):
                print(f"skip {html} ({action} blocked by Tribute System 1)")
                rows.append(
                    {
                        "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "kind": "followup_skip_system1",
                        "issue": html,
                        "ok": True,
                        "lane": "help-wanted-followup",
                        "foreign": True,
                        "action": action,
                        "hydrated": thread is not None,
                    }
                )
                continue

        contrib = None
        try:
            contrib = fetch_contributing(owner, repo)
        except Exception as e:
            print(f"contrib recon fail {owner}/{repo}: {e}", file=sys.stderr)

        urls = list(signal_urls)
        if contrib:
            urls = extract_urls(*(urls + (contrib.get("urls") or [])))
        recon = format_recon_block(contrib, urls)

        if action == "changes":
            head = changes_summary or signal_summary or "(CHANGES_REQUESTED detected)"
            next_line = "Next: revise the head branch to match the review, then re-request review."
        elif action == "reengage":
            head = signal_summary or changes_summary or "(maintainer signal after last follow-up)"
            next_line = (
                "Re-engaging: new maintainer feedback arrived after our last follow-up. "
                "We will adapt the branch to these notes (and foreign CONTRIBUTING)."
            )
        else:
            head = (
                f"Open tribute PR idle ≥{int(STALE_IDLE_HOURS)}h. "
                "Checking foreign requirements and linked notes."
            )
            next_line = (
                "Maintainer: any guidance (or CONTRIBUTING checklist items) welcome; "
                "we will keep this branch aligned with repo norms."
            )

        body = (
            f"{MARKER}\n\n"
            f"**Action:** `{action}`\n\n"
            f"{head}\n\n"
        )
        if recon:
            body += f"### Foreign-repo recon\n\n{recon}\n\n"
        body += (
            f"{next_line}\n\n"
            f"— `timerloggedout-spec/termux-monorepo` help-wanted-followup "
            f"(dynamic re-engage + CONTRIBUTING recon)\n"
        )

        url = post_followup(owner, repo, number, body)
        ok = bool(url)
        print(f"{'ok' if ok else 'fail'} {action} {html} -> {url}")
        rows.append(
            {
                "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "kind": f"followup_{action}",
                "issue": html,
                "ok": ok,
                "comment_url": url,
                "lane": "help-wanted-followup",
                "foreign": True,
                "action": action,
                "has_contributing": bool(contrib),
                "url_count": len(urls),
            }
        )

    if rows:
        append_evidence(rows)
    print(json.dumps({"processed": len(rows), "found": len(items)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
