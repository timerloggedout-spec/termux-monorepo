"""MSM-011: normalize GitHub pull-request review evidence offline."""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "msm-review-evidence-v1"
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
FORMAL_REVIEW_STATES = {"PENDING", "APPROVED", "CHANGES_REQUESTED", "COMMENTED", "DISMISSED"}


class EvidenceError(ValueError):
    """Malformed or inconsistent review evidence."""


def _fail(message: str) -> None:
    raise EvidenceError(message)


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be a non-empty string")
    return value


def _pages(data: Any, label: str) -> list[dict]:
    """Accept flat arrays and gh api --paginate --slurp page arrays."""
    if not isinstance(data, list):
        _fail(f"{label} must be an array or array of pages")
    rows = []
    for i, item in enumerate(data):
        if isinstance(item, list):
            for row in item:
                if not isinstance(row, dict):
                    _fail(f"{label} page records must be objects")
                rows.append(row)
        elif isinstance(item, dict):
            rows.append(item)
        else:
            _fail(f"{label}[{i}] must be an object or page array")
    return rows


def _check_urls(row: dict, label: str, repo: str, pr: int) -> None:
    allowed = {
        "pull_request_url": f"https://api.github.com/repos/{repo}/pulls/{pr}",
        "issue_url": f"https://api.github.com/repos/{repo}/issues/{pr}",
        "repository_url": f"https://api.github.com/repos/{repo}",
    }
    if "html_url" in row:
        url = row["html_url"]
        prefixes = (
            f"https://github.com/{repo}/pull/{pr}",
            f"https://github.com/{repo}/issues/{pr}",
            f"https://github.com/{repo}/commit/",
        )
        valid = isinstance(url, str) and any(
            url == prefix or url.startswith(prefix + "#") or
            (prefix.endswith("/") and bool(SHA_RE.fullmatch(url[len(prefix):])))
            for prefix in prefixes
        )
        if not valid:
            _fail(f"{label}.html_url does not match requested repository/PR")
    for key, expected in allowed.items():
        if key in row and row[key] != expected:
            _fail(f"{label}.{key} does not match requested repository/PR")


def _actor(row: dict, label: str) -> tuple[str | None, str | None]:
    user = row.get("user")
    if user is None:
        return None, None
    if not isinstance(user, dict):
        _fail(f"{label}.user must be an object or null")
    login = user.get("login")
    if login is not None and (not isinstance(login, str) or not login.strip()):
        _fail(f"{label}.user.login must be null or non-empty string")
    typ = user.get("type")
    if typ is not None and typ not in ("User", "Bot", "Organization", "Mannequin"):
        _fail(f"{label}.user.type is invalid")
    return login, typ


def _count_by(rows: list[dict], identity) -> dict:
    result: dict[str, int] = {}
    for row in rows:
        value = identity(row)
        if value is not None:
            result[value] = result.get(value, 0) + 1
    return dict(sorted(result.items()))


def normalize(
    reviews: Any,
    comments: Any,
    inline_comments: Any,
    commits: Any,
    *,
    repo: str,
    pr: int,
    head_sha: str,
) -> dict:
    _nonempty(repo, "repo")
    if len(repo.split("/")) != 2 or any(not part for part in repo.split("/")):
        _fail("repo must be owner/name")
    if isinstance(pr, bool) or not isinstance(pr, int) or pr <= 0:
        _fail("pr must be a positive integer")
    if not isinstance(head_sha, str) or not SHA_RE.fullmatch(head_sha):
        _fail("head_sha must be a full 40-character hex SHA")

    groups = {
        "reviews": _pages(reviews, "reviews"),
        "conversation_comments": _pages(comments, "comments"),
        "inline_comments": _pages(inline_comments, "inline_comments"),
        "commits": _pages(commits, "commits"),
    }
    for name, rows in groups.items():
        seen = set()
        for i, row in enumerate(rows):
            label = f"{name}[{i}]"
            ident = row.get("sha") if name == "commits" else row.get("id")
            if isinstance(ident, bool) or not isinstance(ident, (str, int)) or not str(ident):
                _fail(f"{label}.{'sha' if name == 'commits' else 'id'} must be a string or integer")
            if str(ident) in seen:
                _fail(f"duplicate {name} record id {ident}")
            seen.add(str(ident))
            _check_urls(row, label, repo, pr)

    formal, pending = [], []
    states: dict[str, int] = {}
    for i, row in enumerate(groups["reviews"]):
        label = f"reviews[{i}]"
        state = _nonempty(row.get("state"), f"{label}.state").upper()
        if state not in FORMAL_REVIEW_STATES:
            _fail(f"{label}.state is not a recognized GitHub review state")
        submitted = row.get("submitted_at")
        if submitted is not None and (not isinstance(submitted, str) or not submitted.strip()):
            _fail(f"{label}.submitted_at must be null or non-empty string")
        login, typ = _actor(row, label)
        is_formal = state != "PENDING" and submitted is not None
        entry = {
            "id": str(row["id"]), "state": state, "submitted_at": submitted,
            "actor_login": login, "actor_type": typ,
        }
        if is_formal:
            formal.append(entry)
            states[state] = states.get(state, 0) + 1
        else:
            pending.append(entry)

    def normalize_discussion(name):
        output = []
        for i, row in enumerate(groups[name]):
            login, typ = _actor(row, f"{name}[{i}]")
            output.append({"id": str(row["id"]), "actor_login": login, "actor_type": typ})
        return output

    discussion = normalize_discussion("conversation_comments")
    inline = normalize_discussion("inline_comments")
    commit_rows = []
    for i, row in enumerate(groups["commits"]):
        commit = row.get("commit")
        if not isinstance(commit, dict):
            _fail(f"commits[{i}].commit must be an object")
        sha = _nonempty(row.get("sha"), f"commits[{i}].sha")
        if not SHA_RE.fullmatch(sha):
            _fail(f"commits[{i}].sha must be a full 40-character hex SHA")
        authors = []
        for field in ("author", "committer"):
            user = row.get(field)
            if user is not None and not isinstance(user, dict):
                _fail(f"commits[{i}].{field} must be object or null")
            login = user.get("login") if user else None
            if login is not None and (not isinstance(login, str) or not login.strip()):
                _fail(f"commits[{i}].{field}.login must be null or non-empty string")
            authors.append(login)
        commit_rows.append({
            "id": sha, "sha": sha,
            "author_login": authors[0], "committer_login": authors[1],
        })

    def actor_breakdown(rows):
        # Missing actor type remains unknown, rather than being misclassified as a user.
        users = [row for row in rows if row["actor_type"] == "User"]
        bots = [row for row in rows if row["actor_type"] == "Bot"]
        return {
            "users": _count_by(users, lambda row: row["actor_login"]),
            "bots": _count_by(bots, lambda row: row["actor_login"]),
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "repository": repo,
        "pull_request": pr,
        "bound_head_sha": head_sha.lower(),
        "counts": {
            "formal_submitted_reviews": len(formal),
            "pending_reviews": len(pending),
            "conversation_comments": len(discussion),
            "inline_comments": len(inline),
            "commits": len(commit_rows),
            "formal_review_states": dict(sorted(states.items())),
        },
        "actors": {
            "formal_reviews": actor_breakdown(formal),
            "pending_reviews": actor_breakdown(pending),
            "conversation_comments": actor_breakdown(discussion),
            "inline_comments": actor_breakdown(inline),
            "commit_authors": _count_by(commit_rows, lambda row: row["author_login"]),
            "commit_committers": _count_by(commit_rows, lambda row: row["committer_login"]),
        },
        "provenance": {
            "source_urls": {
                "reviews": f"https://api.github.com/repos/{repo}/pulls/{pr}/reviews",
                "conversation_comments": f"https://api.github.com/repos/{repo}/issues/{pr}/comments",
                "inline_comments": f"https://api.github.com/repos/{repo}/pulls/{pr}/comments",
                "commits": f"https://api.github.com/repos/{repo}/pulls/{pr}/commits",
            },
            "head_sha": head_sha.lower(),
            "review_ids": sorted(row["id"] for row in formal + pending),
            "conversation_comment_ids": sorted(row["id"] for row in discussion),
            "inline_comment_ids": sorted(row["id"] for row in inline),
            "commit_ids": sorted(row["id"] for row in commit_rows),
            "commit_shas": sorted(row["sha"] for row in commit_rows),
        },
        "formal_reviews": sorted(formal, key=lambda row: row["id"]),
        "pending_reviews": sorted(pending, key=lambda row: row["id"]),
    }


def write_output(path: str, value: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent,
            prefix=f".{target.name}.", delete=False,
        ) as output:
            name = output.name
            json.dump(value, output, sort_keys=True, indent=2, ensure_ascii=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, target)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("reviews", "comments", "inline-comments", "commits", "output", "repo", "pr", "head-sha"):
        parser.add_argument("--" + arg, required=True)
    args = parser.parse_args(argv)
    try:
        def load(path):
            with open(path, encoding="utf-8") as source:
                return json.load(source)

        result = normalize(
            load(args.reviews), load(args.comments), load(args.inline_comments),
            load(args.commits), repo=args.repo, pr=int(args.pr), head_sha=args.head_sha,
        )
        write_output(args.output, result)
    except (EvidenceError, OSError, json.JSONDecodeError, ValueError) as exc:
        parser.exit(2, f"review evidence failed; output not written: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
