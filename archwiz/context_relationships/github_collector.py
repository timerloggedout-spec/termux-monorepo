#!/usr/bin/env python3
"""Collect bounded GitHub relationship metadata without persisting discussion bodies.

The collector is intentionally independent from index publication.  It reads a
bounded GitHub API window, extracts only explicit internal references from text
in memory, and emits a compiler-compatible seed plus an audit report.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from .compiler import CompilationError, load_json, path_is_sensitive
except ImportError:  # Supports direct script use.
    from compiler import CompilationError, load_json, path_is_sensitive

COLLECTOR_ID = "archwiz.context_relationships.github_collector@1.0"
REFERENCE_RE = re.compile(
    r"(?:(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+))?#(?P<number>\d+)"
)
CLOSING_RE = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+))?#(?P<number>\d+)",
    re.IGNORECASE,
)
PERMALINK_RE = re.compile(
    r"https?://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)/"
    r"(?P<parent_kind>issues|pull)/(?P<number>\d+)#(?P<anchor>"
    r"issuecomment-(?P<issue_comment>\d+)|"
    r"pullrequestreview-(?P<review>\d+)|"
    r"discussion_r(?P<review_comment>\d+))",
    re.IGNORECASE,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_timestamp(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value:
        return value.replace("+00:00", "Z")
    return fallback


def issue_url(owner: str, repo: str, number: int) -> str:
    return f"https://github.com/{owner}/{repo}/issues/{number}"


def pull_url(owner: str, repo: str, number: int) -> str:
    return f"https://github.com/{owner}/{repo}/pull/{number}"


def permalink_targets(text: str | None, owner: str, repo: str) -> list[tuple[str, str, int, str]]:
    """Return exact local comment/review anchors as node refs and canonical URLs."""
    if not isinstance(text, str) or not text:
        return []
    targets: list[tuple[str, str, int, str]] = []
    for match in PERMALINK_RE.finditer(text):
        if match.group("owner") != owner or match.group("repo") != repo:
            continue
        number = int(match.group("number"))
        kind = next(
            kind
            for group, kind in (
                ("issue_comment", "issue_comment"),
                ("review", "review"),
                ("review_comment", "review_comment"),
            )
            if match.group(group)
        )
        external_id = match.group(kind)
        if external_id is None:
            continue
        targets.append((f"{kind}:{external_id}", match.group(0), number, match.group("parent_kind")))
    return sorted(set(targets), key=lambda item: (item[0], item[1]))


def reference_targets(
    text: str | None,
    owner: str,
    repo: str,
    number_to_ref: Mapping[int, str],
) -> list[tuple[str, str, int]]:
    """Return explicit internal references as (relation, node ref, number)."""
    if not isinstance(text, str) or not text:
        return []
    closing_numbers = {
        int(match.group("number"))
        for match in CLOSING_RE.finditer(text)
        if not match.group("owner") or (match.group("owner") == owner and match.group("repo") == repo)
    }
    targets: list[tuple[str, str, int]] = []
    for match in REFERENCE_RE.finditer(text):
        match_owner, match_repo = match.group("owner"), match.group("repo")
        if match_owner and (match_owner != owner or match_repo != repo):
            continue
        number = int(match.group("number"))
        target = number_to_ref.get(number)
        if target:
            targets.append(("CLOSES" if number in closing_numbers else "REFERENCES", target, number))
    return sorted(set(targets), key=lambda item: (item[0], item[1]))


class GitHubClient:
    def __init__(
        self,
        token: str,
        api_url: str = "https://api.github.com",
        max_retries: int = 3,
        sleep=time.sleep,
    ) -> None:
        self.token = token
        self.api_url = api_url.rstrip("/")
        self.max_retries = max_retries
        self.sleep = sleep
        self.request_count = 0
        self.retry_count = 0

    @staticmethod
    def retry_delay(error: HTTPError, attempt: int) -> float:
        retry_after = error.headers.get("Retry-After") if error.headers else None
        if retry_after and retry_after.isdigit():
            return min(float(retry_after), 60.0)
        reset = error.headers.get("X-RateLimit-Reset") if error.headers else None
        if reset and reset.isdigit():
            return min(max(float(reset) - time.time() + 1.0, 1.0), 60.0)
        return min(float(2**attempt), 30.0)

    def get_json(self, path: str, params: Mapping[str, Any] | None = None) -> tuple[Any, str | None]:
        query = f"?{urlencode(params, doseq=True)}" if params else ""
        request = Request(
            f"{self.api_url}{path}{query}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "termux-monorepo-context-relationships",
            },
        )
        for attempt in range(self.max_retries + 1):
            try:
                with urlopen(request, timeout=30) as response:  # nosec B310: controlled GitHub API base URL
                    self.request_count += 1
                    payload = json.loads(response.read().decode("utf-8"))
                    return payload, response.headers.get("Link")
            except HTTPError as error:
                retriable = error.code in {403, 429, 500, 502, 503, 504}
                if not retriable or attempt >= self.max_retries:
                    raise CompilationError(f"GitHub API request {path} failed with HTTP {error.code}") from error
                self.retry_count += 1
                self.sleep(self.retry_delay(error, attempt))
            except URLError as error:
                if attempt >= self.max_retries:
                    raise CompilationError(f"GitHub API request {path} failed: {error.reason}") from error
                self.retry_count += 1
                self.sleep(min(float(2**attempt), 30.0))
        raise CompilationError(f"GitHub API request {path} exhausted retries")

    def paginate(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        limit: int = 100,
        start_page: int = 1,
    ) -> Iterable[Mapping[str, Any]]:
        if start_page < 1:
            raise CompilationError("GitHub pagination start page must be positive")
        page = start_page
        emitted = 0
        while emitted < limit:
            page_params = dict(params or {})
            page_params.update({"per_page": min(100, limit - emitted), "page": page})
            payload, link = self.get_json(path, page_params)
            if not isinstance(payload, list):
                raise CompilationError(f"GitHub endpoint {path} did not return an array")
            for item in payload:
                if not isinstance(item, Mapping):
                    continue
                yield item
                emitted += 1
                if emitted >= limit:
                    return
            if not payload or not link or 'rel="next"' not in link:
                return
            page += 1


def node(kind: str, external_id: str, observed_at: str, attributes: Mapping[str, Any], url: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "kind": kind,
        "external_id": str(external_id),
        "observed_at": observed_at,
        "attributes": dict(attributes),
    }
    if url:
        result["url"] = url
    return result


def evidence(kind: str, source: str, details: Mapping[str, Any]) -> dict[str, Any]:
    return {"kind": kind, "source": source, "collector": COLLECTOR_ID, "details": dict(details)}


def edge(
    edge_type: str,
    source: str,
    target: str,
    observed_at: str,
    source_url: str,
    details: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "type": edge_type,
        "source": source,
        "target": target,
        "classification": "verified",
        "observed_at": observed_at,
        "evidence": [evidence("github_api" if edge_type not in {"REFERENCES", "CLOSES"} else "github_reference", source_url, details)],
    }


def candidate_edge(
    edge_type: str,
    source: str,
    target: str,
    score: float,
    observed_at: str,
    source_url: str,
    details: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "type": edge_type,
        "source": source,
        "target": target,
        "classification": "candidate",
        "score": score,
        "observed_at": observed_at,
        "evidence": [evidence("co_change", source_url, details)],
    }


def add_node(records: dict[str, dict[str, Any]], raw: dict[str, Any]) -> None:
    reference = f"{raw['kind']}:{raw['external_id']}"
    existing = records.get(reference)
    if existing is None:
        records[reference] = raw
        return
    existing_placeholder = bool((existing.get("attributes") or {}).get("referenced_only"))
    raw_placeholder = bool((raw.get("attributes") or {}).get("referenced_only"))
    if existing_placeholder and not raw_placeholder:
        records[reference] = raw
        return
    if raw_placeholder and not existing_placeholder:
        return
    # Metadata can change during an incremental run; retain the newest observation.
    if raw.get("observed_at", "") >= existing.get("observed_at", ""):
        records[reference] = raw


def load_scope_settings(scope_registry_path: Path) -> tuple[dict[str, list[str]], list[str]]:
    registry = load_json(scope_registry_path, "scope registry")
    exclusions = registry.get("exclusions", {})
    if not isinstance(exclusions, Mapping):
        raise CompilationError("scope registry exclusions must be an object")
    patterns = exclusions.get("path_globs", [])
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise CompilationError("scope registry exclusions.path_globs must be a string list")
    mappings: dict[str, list[str]] = {}
    for scope in registry.get("scopes", []):
        if not isinstance(scope, Mapping):
            continue
        scope_id = scope.get("id")
        labels = scope.get("labels", [])
        if isinstance(scope_id, str) and isinstance(labels, list):
            for label in labels:
                if isinstance(label, str):
                    mappings.setdefault(label.lower(), []).append(scope_id)
    return mappings, sorted(patterns)


def collect_github_seed(
    client: GitHubClient,
    owner: str,
    repo: str,
    ref: str,
    scope_registry_path: Path,
    since: str | None = None,
    max_items: int = 20,
    max_commits: int = 25,
    max_comments_per_item: int = 20,
    include_comments: bool = True,
    max_cochange_pairs_per_commit: int = 100,
    history_start_page: int = 1,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Collect a bounded GitHub metadata window into a compiler-compatible seed."""
    collected_at = utc_now()
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    report: Counter[str] = Counter()
    unresolved_references = 0
    cochange_evidence: dict[tuple[str, str], list[tuple[str, str, str]]] = {}
    label_scopes, exclusions = load_scope_settings(scope_registry_path)

    def accepted_file_path(value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        if path_is_sensitive(value, exclusions):
            report["excluded_history_paths"] += 1
            return None
        return value

    add_node(
        nodes,
        node(
            "repository",
            f"{owner}/{repo}",
            collected_at,
            {"ref": ref},
            f"https://github.com/{owner}/{repo}",
        ),
    )
    for scope_id in sorted({scope_id for values in label_scopes.values() for scope_id in values}):
        add_node(nodes, node("scope", scope_id, collected_at, {"source": "scope_registry"}))

    issue_params: dict[str, Any] = {"state": "all", "sort": "updated", "direction": "desc"}
    if since:
        issue_params["since"] = since
    raw_issues = list(
        client.paginate(
            f"/repos/{owner}/{repo}/issues", issue_params, max_items, start_page=history_start_page
        )
    )
    raw_pulls = list(
        client.paginate(
            f"/repos/{owner}/{repo}/pulls",
            {"state": "all", "sort": "updated", "direction": "desc"},
            max_items,
            start_page=history_start_page,
        )
    )
    if since:
        raw_pulls = [
            pull
            for pull in raw_pulls
            if safe_timestamp(pull.get("updated_at"), collected_at) >= since
        ]

    number_to_ref: dict[int, str] = {}
    issue_items: list[Mapping[str, Any]] = []
    pull_items: list[Mapping[str, Any]] = []
    for item in raw_issues:
        number = item.get("number")
        if not isinstance(number, int):
            continue
        if item.get("pull_request"):
            number_to_ref[number] = f"pull_request:{number}"
        else:
            number_to_ref[number] = f"issue:{number}"
            issue_items.append(item)
    for item in raw_pulls:
        number = item.get("number")
        if isinstance(number, int):
            number_to_ref[number] = f"pull_request:{number}"
            pull_items.append(item)

    def add_labels(parent_ref: str, item: Mapping[str, Any], observed_at: str, parent_url: str) -> None:
        for raw_label in item.get("labels", []):
            if not isinstance(raw_label, Mapping) or not isinstance(raw_label.get("name"), str):
                continue
            label_name = raw_label["name"]
            add_node(nodes, node("label", label_name, observed_at, {"name": label_name}))
            edges.append(edge("LABELED_AS", parent_ref, f"label:{label_name}", observed_at, parent_url, {"label": label_name}))
            report["labels"] += 1
            for scope_id in label_scopes.get(label_name.lower(), []):
                edges.append(
                    edge(
                        "IN_SCOPE",
                        f"label:{label_name}",
                        f"scope:{scope_id}",
                        observed_at,
                        scope_registry_path.as_posix(),
                        {"label": label_name, "scope": scope_id},
                    )
                )

    def add_explicit_references(parent_ref: str, text: str | None, observed_at: str, parent_url: str) -> None:
        nonlocal unresolved_references
        references = reference_targets(text, owner, repo, number_to_ref)
        referenced_numbers = {number for _, _, number in references}
        if isinstance(text, str):
            local_numbers = {
                int(match.group("number"))
                for match in REFERENCE_RE.finditer(text)
                if not match.group("owner") or (match.group("owner") == owner and match.group("repo") == repo)
            }
            unresolved_references += len(local_numbers - referenced_numbers)
        for relationship, target_ref, number in references:
            if target_ref == parent_ref:
                continue
            edges.append(
                edge(relationship, parent_ref, target_ref, observed_at, parent_url, {"reference": f"#{number}"})
            )
            report["explicit_references"] += 1
        for target_ref, target_url, target_number, parent_kind in permalink_targets(text, owner, repo):
            if target_ref == parent_ref:
                continue
            target_kind, target_id = target_ref.split(":", maxsplit=1)
            target_parent_ref = (
                f"pull_request:{target_number}"
                if parent_kind == "pull"
                else number_to_ref.get(target_number, f"issue:{target_number}")
            )
            target_parent_kind = target_parent_ref.split(":", maxsplit=1)[0]
            target_parent_url = (
                pull_url(owner, repo, target_number)
                if target_parent_kind == "pull_request"
                else issue_url(owner, repo, target_number)
            )
            add_node(
                nodes,
                node(
                    target_parent_kind,
                    str(target_number),
                    observed_at,
                    {"number": target_number, "referenced_only": True},
                    target_parent_url,
                ),
            )
            comment_attributes = {"referenced_only": True, "permalink": target_url}
            if target_parent_kind == "pull_request":
                comment_attributes["parent_pull_request"] = target_number
            else:
                comment_attributes["parent_issue"] = target_number
            add_node(nodes, node(target_kind, target_id, observed_at, comment_attributes, target_url))
            parent_relation = "REVIEWS" if target_kind == "review" else "COMMENTS_ON"
            edges.append(
                edge(
                    parent_relation,
                    target_ref,
                    target_parent_ref,
                    observed_at,
                    target_url,
                    {"parent": target_parent_ref, "permalink_target": True},
                )
            )
            edges.append(
                edge(
                    "REFERENCES",
                    parent_ref,
                    target_ref,
                    observed_at,
                    parent_url,
                    {"permalink": target_url, "target_kind": target_kind},
                )
            )
            report["permalink_references"] += 1

    def add_timeline_cross_references(parent_ref: str, number: int, parent_url: str, observed_at: str) -> None:
        for event_item in client.paginate(f"/repos/{owner}/{repo}/issues/{number}/timeline", {}, max_items):
            if event_item.get("event") != "cross-referenced":
                continue
            source_container = event_item.get("source")
            if not isinstance(source_container, Mapping):
                continue
            source = source_container.get("issue") or source_container.get("pull_request") or source_container
            if not isinstance(source, Mapping) or not isinstance(source.get("number"), int):
                continue
            source_number = int(source["number"])
            source_kind = (
                "pull_request"
                if source_container.get("type") == "pull_request" or source.get("pull_request")
                else "issue"
            )
            source_ref = f"{source_kind}:{source_number}"
            source_url = str(
                source.get("html_url")
                or (pull_url(owner, repo, source_number) if source_kind == "pull_request" else issue_url(owner, repo, source_number))
            )
            event_time = safe_timestamp(event_item.get("created_at"), observed_at)
            source_attributes = {
                "number": source_number,
                "state": source.get("state"),
                "title": source.get("title", ""),
                "referenced_only": source_number not in number_to_ref,
            }
            add_node(nodes, node(source_kind, str(source_number), event_time, source_attributes, source_url))
            number_to_ref.setdefault(source_number, source_ref)
            actor = (event_item.get("actor") or {}).get("login")
            edges.append(
                edge(
                    "MENTIONS",
                    source_ref,
                    parent_ref,
                    event_time,
                    parent_url,
                    {
                        "timeline_event": "cross-referenced",
                        "actor": actor if isinstance(actor, str) else None,
                        "source_url": source_url,
                    },
                )
            )
            report["timeline_cross_references"] += 1

    for item in sorted(issue_items, key=lambda item: int(item["number"])):
        number = int(item["number"])
        observed_at = safe_timestamp(item.get("updated_at"), collected_at)
        url = str(item.get("html_url") or issue_url(owner, repo, number))
        parent_ref = f"issue:{number}"
        add_node(
            nodes,
            node(
                "issue",
                str(number),
                observed_at,
                {
                    "number": number,
                    "state": item.get("state"),
                    "title": item.get("title", ""),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                },
                url,
            ),
        )
        report["issues"] += 1
        add_labels(parent_ref, item, observed_at, url)
        add_explicit_references(parent_ref, item.get("body"), observed_at, url)
        add_timeline_cross_references(parent_ref, number, url, observed_at)
        if include_comments:
            for comment in client.paginate(
                f"/repos/{owner}/{repo}/issues/{number}/comments", {}, max_comments_per_item
            ):
                comment_id = comment.get("id")
                if not isinstance(comment_id, int):
                    continue
                comment_time = safe_timestamp(comment.get("updated_at") or comment.get("created_at"), observed_at)
                comment_url = str(comment.get("html_url") or url)
                comment_ref = f"issue_comment:{comment_id}"
                add_node(
                    nodes,
                    node(
                        "issue_comment",
                        str(comment_id),
                        comment_time,
                        {"parent_issue": number, "created_at": comment.get("created_at"), "updated_at": comment.get("updated_at")},
                        comment_url,
                    ),
                )
                edges.append(edge("COMMENTS_ON", comment_ref, parent_ref, comment_time, comment_url, {"parent": parent_ref}))
                add_explicit_references(comment_ref, comment.get("body"), comment_time, comment_url)
                report["issue_comments"] += 1

    for item in sorted(pull_items, key=lambda item: int(item["number"])):
        number = int(item["number"])
        observed_at = safe_timestamp(item.get("updated_at"), collected_at)
        url = str(item.get("html_url") or pull_url(owner, repo, number))
        parent_ref = f"pull_request:{number}"
        add_node(
            nodes,
            node(
                "pull_request",
                str(number),
                observed_at,
                {
                    "number": number,
                    "state": item.get("state"),
                    "title": item.get("title", ""),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "merged_at": item.get("merged_at"),
                    "base_ref": (item.get("base") or {}).get("ref"),
                    "head_ref": (item.get("head") or {}).get("ref"),
                },
                url,
            ),
        )
        report["pull_requests"] += 1
        add_labels(parent_ref, item, observed_at, url)
        add_explicit_references(parent_ref, item.get("body"), observed_at, url)

        for changed_file in client.paginate(f"/repos/{owner}/{repo}/pulls/{number}/files", {}, max_items):
            filename = accepted_file_path(changed_file.get("filename"))
            if filename is None:
                continue
            file_url = f"https://github.com/{owner}/{repo}/blob/{ref}/{filename}"
            add_node(nodes, node("file", filename, observed_at, {"path": filename}, file_url))
            edges.append(edge("TOUCHES", parent_ref, f"file:{filename}", observed_at, url, {"status": changed_file.get("status")}))
            report["pull_request_files"] += 1

        for commit in client.paginate(f"/repos/{owner}/{repo}/pulls/{number}/commits", {}, max_commits):
            sha = commit.get("sha")
            if not isinstance(sha, str):
                continue
            commit_time = safe_timestamp(
                ((commit.get("commit") or {}).get("committer") or {}).get("date"), observed_at
            )
            commit_url = str(commit.get("html_url") or f"https://github.com/{owner}/{repo}/commit/{sha}")
            add_node(nodes, node("commit", sha, commit_time, {"sha": sha}, commit_url))
            edges.append(edge("HAS_COMMIT", parent_ref, f"commit:{sha}", commit_time, url, {"sha": sha}))
            report["pull_request_commits"] += 1

        if include_comments:
            for comment in client.paginate(
                f"/repos/{owner}/{repo}/issues/{number}/comments", {}, max_comments_per_item
            ):
                comment_id = comment.get("id")
                if not isinstance(comment_id, int):
                    continue
                comment_time = safe_timestamp(comment.get("updated_at") or comment.get("created_at"), observed_at)
                comment_url = str(comment.get("html_url") or url)
                comment_ref = f"issue_comment:{comment_id}"
                add_node(
                    nodes,
                    node(
                        "issue_comment",
                        str(comment_id),
                        comment_time,
                        {"parent_pull_request": number, "created_at": comment.get("created_at"), "updated_at": comment.get("updated_at")},
                        comment_url,
                    ),
                )
                edges.append(edge("COMMENTS_ON", comment_ref, parent_ref, comment_time, comment_url, {"parent": parent_ref}))
                add_explicit_references(comment_ref, comment.get("body"), comment_time, comment_url)
                report["pull_request_comments"] += 1
            for review in client.paginate(f"/repos/{owner}/{repo}/pulls/{number}/reviews", {}, max_comments_per_item):
                review_id = review.get("id")
                if not isinstance(review_id, int):
                    continue
                review_time = safe_timestamp(review.get("submitted_at") or review.get("updated_at"), observed_at)
                review_url = str(review.get("html_url") or url)
                review_ref = f"review:{review_id}"
                add_node(
                    nodes,
                    node(
                        "review",
                        str(review_id),
                        review_time,
                        {"parent_pull_request": number, "state": review.get("state")},
                        review_url,
                    ),
                )
                edges.append(edge("REVIEWS", review_ref, parent_ref, review_time, review_url, {"parent": parent_ref}))
                add_explicit_references(review_ref, review.get("body"), review_time, review_url)
                report["reviews"] += 1
            for comment in client.paginate(f"/repos/{owner}/{repo}/pulls/{number}/comments", {}, max_comments_per_item):
                comment_id = comment.get("id")
                if not isinstance(comment_id, int):
                    continue
                comment_time = safe_timestamp(comment.get("updated_at") or comment.get("created_at"), observed_at)
                comment_url = str(comment.get("html_url") or url)
                comment_ref = f"review_comment:{comment_id}"
                review_path = accepted_file_path(comment.get("path"))
                review_attributes = {"parent_pull_request": number, "line": comment.get("line")}
                if review_path is not None:
                    review_attributes["path"] = review_path
                add_node(
                    nodes,
                    node("review_comment", str(comment_id), comment_time, review_attributes, comment_url),
                )
                if review_path is not None:
                    add_node(nodes, node("file", review_path, comment_time, {"path": review_path}, f"https://github.com/{owner}/{repo}/blob/{ref}/{review_path}"))
                    edges.append(
                        edge(
                            "TOUCHES",
                            comment_ref,
                            f"file:{review_path}",
                            comment_time,
                            comment_url,
                            {"path": review_path, "line": comment.get("line"), "review_comment": True},
                        )
                    )
                edges.append(edge("COMMENTS_ON", comment_ref, parent_ref, comment_time, comment_url, {"parent": parent_ref}))
                add_explicit_references(comment_ref, comment.get("body"), comment_time, comment_url)
                report["review_comments"] += 1

    for commit in client.paginate(
        f"/repos/{owner}/{repo}/commits",
        {key: value for key, value in {"sha": ref, "since": since}.items() if value},
        max_commits,
    ):
        sha = commit.get("sha")
        if not isinstance(sha, str):
            continue
        commit_time = safe_timestamp(((commit.get("commit") or {}).get("committer") or {}).get("date"), collected_at)
        commit_url = str(commit.get("html_url") or f"https://github.com/{owner}/{repo}/commit/{sha}")
        add_node(nodes, node("commit", sha, commit_time, {"sha": sha}, commit_url))
        report["commits"] += 1
        full_commit, _ = client.get_json(f"/repos/{owner}/{repo}/commits/{sha}")
        if not isinstance(full_commit, Mapping):
            continue
        touched_files: list[str] = []
        for changed_file in full_commit.get("files", []):
            if not isinstance(changed_file, Mapping):
                continue
            filename = accepted_file_path(changed_file.get("filename"))
            if filename is None:
                continue
            touched_files.append(filename)
            file_url = f"https://github.com/{owner}/{repo}/blob/{ref}/{filename}"
            add_node(nodes, node("file", filename, commit_time, {"path": filename}, file_url))
            edges.append(edge("CHANGED_IN", f"file:{filename}", f"commit:{sha}", commit_time, commit_url, {"status": changed_file.get("status")}))
            report["commit_files"] += 1
        for source_path, target_path in list(combinations(sorted(set(touched_files)), 2))[:max_cochange_pairs_per_commit]:
            cochange_evidence.setdefault((source_path, target_path), []).append((sha, commit_time, commit_url))

    for (source_path, target_path), touches in sorted(cochange_evidence.items()):
        latest_time = max(item[1] for item in touches)
        latest_url = next(item[2] for item in sorted(touches, key=lambda item: item[1], reverse=True))
        score = min(0.95, round(0.35 + (0.15 * len(touches)), 2))
        edges.append(
            candidate_edge(
                "CO_CHANGED_WITH",
                f"file:{source_path}",
                f"file:{target_path}",
                score,
                latest_time,
                latest_url,
                {"commit_count": len(touches), "commits": [item[0] for item in sorted(touches)]},
            )
        )
        report["cochange_candidates"] += 1

    seed = {
        "schema_version": "1.0",
        "repository": {"owner": owner, "name": repo, "default_branch": ref},
        "nodes": [nodes[key] for key in sorted(nodes)],
        "edges": edges,
    }
    report_data = {
        "collector": COLLECTOR_ID,
        "collected_at": collected_at,
        "since": since,
        "max_items": max_items,
        "max_commits": max_commits,
        "max_comments_per_item": max_comments_per_item,
        "include_comments": include_comments,
        "history_window": {
            "start_page": history_start_page,
            "limit_per_family": max_items,
            "issue_count": len(raw_issues),
            "pull_request_count": len(raw_pulls),
            "issues_complete": len(raw_issues) < max_items,
            "pull_requests_complete": len(raw_pulls) < max_items,
            "next_start_page": (
                None
                if len(raw_issues) < max_items and len(raw_pulls) < max_items
                else history_start_page + ((max_items + 99) // 100)
            ),
        },
        "request_count": client.request_count,
        "unresolved_internal_reference_count": unresolved_references,
        "counts": dict(sorted(report.items())),
    }
    return seed, report_data


def load_checkpoint(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    checkpoint = load_json(path, "GitHub collection checkpoint")
    value = checkpoint.get("last_successful_at")
    if value is not None and not isinstance(value, str):
        raise CompilationError("GitHub collection checkpoint last_successful_at must be a string")
    return value


def write_checkpoint(path: Path, collected_at: str, owner: str, repo: str, ref: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "repository": f"{owner}/{repo}",
                "ref": ref,
                "last_successful_at": collected_at,
                "collector": COLLECTOR_ID,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--token-env", default="GITHUB_TOKEN", help="Environment variable containing a GitHub token")
    parser.add_argument("--api-url", default="https://api.github.com")
    parser.add_argument("--since", help="Optional ISO-8601 incremental high-water mark")
    parser.add_argument("--checkpoint", type=Path, help="Optional JSON high-water checkpoint; used when --since is omitted")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--max-items", type=int, default=20)
    parser.add_argument("--max-commits", type=int, default=25)
    parser.add_argument("--max-comments-per-item", type=int, default=20)
    parser.add_argument("--max-cochange-pairs-per-commit", type=int, default=100)
    parser.add_argument(
        "--history-start-page",
        type=int,
        default=1,
        help="GitHub history page to begin for an operator-controlled backfill window",
    )
    parser.add_argument("--without-comments", action="store_true")
    parser.add_argument(
        "--scope-registry",
        type=Path,
        default=Path("config/context_relationships/scope_registry.json"),
    )
    parser.add_argument("--output", type=Path, required=True, help="Path for the normalized GitHub seed")
    parser.add_argument("--report", type=Path, required=True, help="Path for collection summary")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    token = os.environ.get(args.token_env)
    if not token:
        print(f"GitHub collection failed: missing token in {args.token_env}", file=sys.stderr)
        return 2
    try:
        if any(
            value < 1
            for value in (
                args.max_items,
                args.max_commits,
                args.max_comments_per_item,
                args.max_cochange_pairs_per_commit,
                args.history_start_page,
            )
        ):
            raise CompilationError("collection limits must be positive integers")
        if args.max_retries < 0:
            raise CompilationError("max retries must be zero or greater")
        since = args.since or load_checkpoint(args.checkpoint)
        client = GitHubClient(token, args.api_url, args.max_retries)
        seed, report = collect_github_seed(
            client,
            args.owner,
            args.repo,
            args.ref,
            args.scope_registry,
            since,
            args.max_items,
            args.max_commits,
            args.max_comments_per_item,
            not args.without_comments,
            args.max_cochange_pairs_per_commit,
            args.history_start_page,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(seed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report["retry_count"] = client.retry_count
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.checkpoint is not None:
            write_checkpoint(args.checkpoint, report["collected_at"], args.owner, args.repo, args.ref)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except CompilationError as exc:
        print(f"GitHub collection failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
