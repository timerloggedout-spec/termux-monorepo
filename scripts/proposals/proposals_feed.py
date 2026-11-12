#!/usr/bin/env python3
"""Proposals index feed collector — schema proposals-feed/v2.

Reads the proposal registry of record (docs/proposals/registry.yaml)
and the Oracle Method pass records (docs/proposals/passes/*/pass.json)
and emits the feed the dashboard's proposals page renders: every
registered proposal pack with its status, priority, author and related
issues/PRs, linked to its tree on GitHub, plus the pass records.

Each related PR is stamped at collection time with the state the
GitHub API reports for it — `open`, `merged` or `closed-unmerged`,
plus `merged_at` when merged (schema v2; v1 carried the bare number).
PR state comes from the API at collection, never from the registry
and never hand-entered; a ref the API cannot resolve is stamped
`unknown` and named in `gaps`, never guessed.

Honesty rules (contract: docs/ops/PROPOSALS-FEED.md): registry values
are carried verbatim — statuses, priorities and author strings are
never normalized, merged or inferred; a field the registry omits
renders as an empty list, never a guessed one; a pass record whose
pass.json cannot be read is named in `gaps`, never silently dropped.

Usage: proposals_feed.py --registry docs/proposals/registry.yaml \
         --proposals-root docs/proposals --out FEED.json

The registry is YAML. PyYAML is used when importable; otherwise a
subset parser for this registry's regular shape runs instead (scalar
fields, inline or block integer lists for the related fields). The
two parsers are differential-tested against each other.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "proposals-feed/v2"
TREE = "https://github.com/timerloggedout-spec/termux-monorepo/tree/master/docs/proposals/"
REPO = "timerloggedout-spec/termux-monorepo"
API = "https://api.github.com"
ITEM_KEYS = ("id", "title", "author", "status", "priority", "path", "proposal_type")
INT_LIST_KEYS = ("related_issues", "related_prs")
PR_STATES = ("open", "merged", "closed-unmerged", "unknown")
PROPOSAL_TYPES = frozenset({
    "architecture", "research", "scientific_experiment",
    "scientific_experiment_system", "behavioral_experiment",
    "measurement_validation", "integration", "operations", "product",
    "governance", "security", "evaluation",
})


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return json.loads(value)
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def _int_list(value: str) -> list[int]:
    value = value.strip()
    if value in ("", "[]"):
        return []
    assert value.startswith("[") and value.endswith("]"), f"not a flow list: {value!r}"
    return [int(x.strip()) for x in value[1:-1].split(",") if x.strip()]


def parse_registry_subset(text: str) -> dict:
    """Parse the registry without PyYAML (its regular shape only).

    Two list shapes occur in the wild and both parse: the house style
    (items indented 2 under `proposals:`, keys at 4) and PyYAML's
    indentless style (items at 0, keys at 2). The item indent is
    learned from the first item; key and block-list indents follow.
    """
    registry: dict = {"proposals": []}
    current: dict | None = None
    pending_list_key: str | None = None
    in_proposals = False
    key_indent: int | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0 and not line.startswith("- "):
            in_proposals = line.startswith("proposals:")
            if not in_proposals and ":" in line:
                key, _, value = line.partition(":")
                registry[key.strip()] = _unquote(value)
            current = None
            pending_list_key = None
            key_indent = None
            continue
        if not in_proposals:
            continue
        if line.startswith("- ") and (key_indent is None or indent == key_indent - 2):
            current = {}
            registry["proposals"].append(current)
            pending_list_key = None
            key_indent = indent + 2
            line = line[2:]
            indent = key_indent
            if not line:
                continue
        if current is None or key_indent is None:
            continue
        if indent == key_indent and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            pending_list_key = None
            if key in ITEM_KEYS:
                current[key] = _unquote(value)
            elif key in INT_LIST_KEYS:
                if value:
                    current[key] = _int_list(value)
                else:
                    current[key] = []
                    pending_list_key = key
            continue
        if indent == key_indent + 2 and line.startswith("- ") and pending_list_key:
            current[pending_list_key].append(int(line[2:].strip()))
            continue
        # anything deeper belongs to a skipped nested block (reviewers,
        # related_branches, gates_required, ...) — not feed fields.
    return registry


BALLOT_CLASS_PRECEDENCE = ("LOCAL_BASELINE", "HUMAN_COLLABORATOR", "MODEL_PROVIDER")


def _pass_outcome(ballot: dict) -> dict | None:
    """The pass's round-1 outcome, verbatim from its ballot record.

    Scores come from the ballot class that actually voted (count > 0);
    when several classes voted, the class with the most ballots wins
    and ties resolve by BALLOT_CLASS_PRECEDENCE. Scores are carried
    exactly as recorded — equal scores stay equal (a tie is data;
    the feed never ranks). Returns None when no class voted.
    """
    by_class = ballot.get("ballots_by_class") or {}
    per_class = ballot.get("per_class") or {}
    eligible = []
    for cls in BALLOT_CLASS_PRECEDENCE:
        count = by_class.get(cls, 0)
        scores = (per_class.get(cls) or {}).get("scores")
        if isinstance(count, int) and count > 0 and isinstance(scores, dict) and scores:
            eligible.append((cls, count))
    if not eligible:
        return None
    cls, _count = max(eligible, key=lambda kv: kv[1])
    return {
        "scores": per_class[cls]["scores"],
        "ballots": sum(int(v) for v in by_class.values() if isinstance(v, int)),
        "class": cls,
        "source": "cycle/BALLOT-round1.json",
    }


def load_registry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return parse_registry_subset(text)


def fetch_pr(number: int, token: str) -> dict:
    """One PR's state record from the GitHub API.

    `state` is `open`, `merged` (closed with a merge — merged_at is
    carried verbatim from the API) or `closed-unmerged`. Any failure
    (HTTP error, network, malformed body) yields `unknown`: the feed
    never guesses a state it could not read.
    """
    req = urllib.request.Request(
        f"{API}/repos/{REPO}/pulls/{number}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "proposals-feed-collector",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {"number": number, "state": "unknown", "merged_at": None}
    if data.get("state") == "open":
        return {"number": number, "state": "open", "merged_at": None}
    if data.get("merged_at"):
        return {"number": number, "state": "merged",
                "merged_at": data["merged_at"]}
    if data.get("state") == "closed":
        return {"number": number, "state": "closed-unmerged",
                "merged_at": None}
    return {"number": number, "state": "unknown", "merged_at": None}


def resolve_pr_states(numbers, token: str, fetch=fetch_pr) -> dict:
    """Resolve each unique PR number once; returns {number: record}."""
    return {n: fetch(n, token) for n in sorted(set(numbers))}


def collection_token() -> str | None:
    """The API token for collection, from the job environment."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def build_feed(registry: dict, proposals_root: Path, now: str,
               pr_states: dict | None = None) -> dict:
    def pr_record(number: int) -> dict:
        if pr_states is not None and number in pr_states:
            return pr_states[number]
        return {"number": number, "state": "unknown", "merged_at": None}

    proposals = []
    gaps: list[str] = []
    for entry in registry.get("proposals", []):
        path = str(entry.get("path", "")).strip()
        proposal_type = entry.get("proposal_type")
        if proposal_type is not None and proposal_type not in PROPOSAL_TYPES:
            gaps.append(f"proposal {entry.get('id')}: unknown proposal_type {proposal_type!r} (preserved verbatim)")
        proposals.append({
            "id": entry.get("id"),
            "title": entry.get("title"),
            "author": entry.get("author"),
            "status": entry.get("status"),
            "priority": entry.get("priority"),
            "proposal_type": proposal_type,
            "path": path,
            "url": TREE + path.lstrip("/"),
            "issues": [int(x) for x in entry.get("related_issues") or []],
            "prs": [pr_record(int(x)) for x in entry.get("related_prs") or []],
        })

    passes = []
    passes_dir = proposals_root / "passes"
    if passes_dir.is_dir():
        for pass_dir in sorted(p for p in passes_dir.iterdir() if p.is_dir()):
            record = {"id": pass_dir.name, "pass_id": None, "schema": None,
                      "status": None, "candidates": None, "outcome": None,
                      "path": f"passes/{pass_dir.name}/",
                      "url": TREE + f"passes/{pass_dir.name}"}
            try:
                data = json.loads((pass_dir / "pass.json").read_text(encoding="utf-8"))
                record["pass_id"] = data.get("pass_id")
                record["schema"] = data.get("schema")
                # the pass's own status, verbatim from its record —
                # never inferred from the registry or the pass's age
                record["status"] = data.get("status")
                if record["status"] is None:
                    gaps.append(f"pass {pass_dir.name}: no status field in pass.json (not inferred)")
                if isinstance(data.get("candidates"), list):
                    record["candidates"] = len(data["candidates"])
            except Exception as exc:  # named, never silently dropped
                gaps.append(f"pass {pass_dir.name}: pass.json unreadable ({type(exc).__name__})")
            ballot_path = pass_dir / "cycle" / "BALLOT-round1.json"
            if ballot_path.is_file():
                try:
                    ballot = json.loads(ballot_path.read_text(encoding="utf-8"))
                    outcome = _pass_outcome(ballot)
                    if outcome is not None:
                        record["outcome"] = outcome
                    else:
                        gaps.append(f"pass {pass_dir.name}: BALLOT-round1.json records no ballots (outcome not emitted)")
                except Exception as exc:  # named, never silently dropped
                    gaps.append(f"pass {pass_dir.name}: BALLOT-round1.json unreadable ({type(exc).__name__}); outcome not emitted")
            passes.append(record)
    else:
        gaps.append("docs/proposals/passes/ not found")

    def tally(key: str) -> dict:
        counts: dict[str, int] = {}
        for p in proposals:
            value = p.get(key)
            if value is None:
                continue
            counts[value] = counts.get(value, 0) + 1
        return counts

    return {
        "schema": SCHEMA,
        "generated_at": now,
        "source": "docs/proposals/registry.yaml",
        "registry_updated_at": registry.get("updated_at"),
        "registry_updated_by": registry.get("updated_by"),
        "counts": {
            "total": len(proposals),
            "by_status": tally("status"),
            "by_priority": tally("priority"),
            "by_author": tally("author"),
            "by_type": tally("proposal_type"),
            "passes": len(passes),
        },
        "proposals": proposals,
        "passes": passes,
        "gaps": gaps,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="docs/proposals/registry.yaml")
    ap.add_argument("--proposals-root", default="docs/proposals")
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-pr-states", action="store_true",
                    help="do not call the API; stamp every PR unknown")
    args = ap.parse_args()
    registry = load_registry(Path(args.registry))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pr_states = None
    resolution_gaps: list[str] = []
    if not args.skip_pr_states:
        numbers = [int(x) for entry in registry.get("proposals", [])
                   for x in entry.get("related_prs") or []]
        token = collection_token()
        if token and numbers:
            pr_states = resolve_pr_states(numbers, token)
            for n in sorted(pr_states):
                if pr_states[n]["state"] == "unknown":
                    resolution_gaps.append(
                        f"pr #{n}: state unresolvable at collection "
                        "(stamped unknown, never guessed)")
        elif numbers:
            resolution_gaps.append(
                "PR states not resolved at collection (no API token in "
                "the collection environment); all PR refs stamped "
                "unknown, never guessed")
    feed = build_feed(registry, Path(args.proposals_root), now,
                      pr_states=pr_states)
    feed["gaps"].extend(resolution_gaps)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(feed, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}: {feed['counts']['total']} proposals, "
          f"{feed['counts']['passes']} passes, {len(feed['gaps'])} gaps")


if __name__ == "__main__":
    main()
