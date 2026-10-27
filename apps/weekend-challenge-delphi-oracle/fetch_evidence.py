"""fetch_evidence — the one new tool for the Weekend Challenge entry.

Given a decision request naming an artifact (a pull request, a file, a
workflow run), retrieve the artifact's *current* state read-only and
assemble a material evidence set: every item carries provenance (where it
came from, when it was observed) and a freshness stamp (fresh_until).
The Delphi oracle then grades fetched evidence instead of asserted
evidence — the fleet's "evidence over claims" rule, as a tool.

Transport is injected: any callable ``transport(method, path) -> dict``.
Only GET is ever issued; a non-GET raises. The default transport reads
the public GitHub API with urllib (optional GITHUB_TOKEN env for rate
limits). No credentials are stored or logged here.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

SCHEMA = "delphi-evidence-set/v1"
TTL_SECONDS = 900  # an evidence set is fresh for 15 minutes from assembly
REPO = "timerloggedout-spec/termux-monorepo"


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _item(claim: str, value, path: str, observed_at: datetime) -> dict:
    payload = json.dumps({"claim": claim, "value": value, "path": path},
                         sort_keys=True).encode()
    return {
        "claim": claim,
        "value": value,
        "provenance": {"source": "github-api", "path": path,
                       "observed_at": _iso(observed_at)},
        "fresh_until": _iso(observed_at + timedelta(seconds=TTL_SECONDS)),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def github_transport(method: str, path: str) -> dict:
    """Default read-only transport against api.github.com."""
    if method != "GET":
        raise ValueError("fetch_evidence is read-only: GET only")
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "delphi-fetch-evidence/1.0"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


class CountingTransport:
    """Wraps a transport and counts calls, so receipts stay honest."""

    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def __call__(self, method: str, path: str) -> dict:
        if method != "GET":
            raise ValueError("fetch_evidence is read-only: GET only")
        self.calls += 1
        return self.inner(method, path)


def fetch_evidence(artifact: dict, transport=None, now: datetime | None = None,
                   repo: str = REPO) -> dict:
    """Assemble a provenance/freshness-stamped evidence set for an artifact.

    artifact: {"kind": "pull_request" | "file" | "workflow_run",
               "ref": <number | path | run id>}
    """
    transport = transport or github_transport
    now = now or datetime.now(timezone.utc)
    kind, ref = artifact["kind"], artifact["ref"]
    items: list[dict] = []

    if kind == "pull_request":
        base = f"/repos/{repo}/pulls/{ref}"
        pr = transport("GET", base)
        items.append(_item("pr.state", pr.get("state"), base, now))
        items.append(_item("pr.merged", bool(pr.get("merged_at")), base, now))
        items.append(_item("pr.head_sha", (pr.get("head") or {}).get("sha"),
                           base, now))
        checks_path = f"/repos/{repo}/commits/{pr['head']['sha']}/check-runs?per_page=100"
        checks = transport("GET", checks_path)
        for run in checks.get("check_runs", []):
            items.append(_item(f"check:{run['name']}", run.get("conclusion"),
                               checks_path, now))
    elif kind == "file":
        path = f"/repos/{repo}/contents/{ref}?ref=master"
        meta = transport("GET", path)
        items.append(_item("file.exists", True, path, now))
        items.append(_item("file.blob_sha", meta.get("sha"), path, now))
        items.append(_item("file.size_bytes", meta.get("size"), path, now))
    elif kind == "workflow_run":
        path = f"/repos/{repo}/actions/runs/{ref}"
        run = transport("GET", path)
        items.append(_item("run.conclusion", run.get("conclusion"), path, now))
        items.append(_item("run.event", run.get("event"), path, now))
    else:
        raise ValueError(f"unsupported artifact kind: {kind}")

    material = len(items) >= 2 and all(
        it["provenance"]["path"] and it["sha256"] for it in items)
    return {
        "schema": SCHEMA,
        "artifact": {"kind": kind, "ref": ref, "repo": repo},
        "assembled_at": _iso(now),
        "fresh_until": _iso(now + timedelta(seconds=TTL_SECONDS)),
        "items": items,
        "material": material,
    }
