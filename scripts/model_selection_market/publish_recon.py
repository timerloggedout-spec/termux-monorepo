"""MSM-006: publish one deterministic research-only refresh PR through GitHub.

Only the generated snapshot path may change. No provider invocation, arbitrary
patches, force pushes, approval, merge, or routing mutation is supported.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

SNAPSHOT_PATH = "data/model-selection-market/provider-recon.json"
SCHEMA = "msm-provider-recon-v1"
REPO = "timerloggedout-spec/termux-monorepo"
GATES = ("repo-gate.yml", "termux-smoke.yml")


class GitHub:
    def __init__(self, token: str, repo: str = REPO):
        if repo != REPO:
            raise ValueError("publication is restricted to the development repository")
        self.token = token
        self.repo = repo

    def call(self, method: str, path: str, payload: Any = None) -> Any:
        body = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(
            f"https://api.github.com/repos/{self.repo}/{path}", data=body,
            method=method, headers={"Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json", "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "cue-q-provider-recon"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
                return json.loads(data) if data else None
        except urllib.error.HTTPError as exc:
            # Never print server bodies, request headers, or credentials.
            raise RuntimeError(f"GitHub {method} {path.split('?')[0]} returned HTTP {exc.code}") from None


def validate_snapshot(raw: bytes) -> dict:
    document = json.loads(raw)
    if not isinstance(document, dict) or document.get("schema_version") != SCHEMA:
        raise ValueError("unsupported research snapshot schema")
    # Every candidate stays research-only, including newly added upstream entries.
    models = document.get("model_candidates")
    if not isinstance(models, list) or not models:
        raise ValueError("snapshot must contain nonempty research candidates")
    for row in models:
        if not isinstance(row, dict) or row.get("runtime_eligible") is not False:
            raise ValueError("research data cannot authorize runtime eligibility")
        if row.get("quota_remaining") is not None:
            raise ValueError("directory claims cannot establish remaining quota")
    sources = document.get("sources")
    if not isinstance(sources, list) or len(sources) != 2:
        raise ValueError("both prioritized upstream sources are required")
    expected = {"mnfst/awesome-free-llm-apis", "tashfeenahmed/freellmapi"}
    if {source.get("repo") for source in sources if isinstance(source, dict)} != expected:
        raise ValueError("snapshot source repositories must match the fixed allowlist")
    for source in sources:
        sha = source.get("commit_sha", "")
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("source requires a full commit SHA")
        files = source.get("files")
        if not isinstance(files, dict) or not files:
            raise ValueError("source requires pinned file provenance")
        for path, metadata in files.items():
            expected_url = f"https://raw.githubusercontent.com/{source['repo']}/{sha}/{path}"
            if metadata.get("url") != expected_url or not re.fullmatch(r"[0-9a-f]{64}", metadata.get("sha256", "")):
                raise ValueError("source file lacks pinned URL/hash provenance")
    seen = set()
    for row in models:
        if row.get("source_repo") not in expected or row.get("evidence_class") != "THIRD_PARTY_CLAIM":
            raise ValueError("every candidate must be an attributed third-party claim")
        key = (row["source_repo"], row.get("provider_key"), row.get("model_key"))
        if not all(isinstance(value, str) and value for value in key) or key in seen:
            raise ValueError("candidate identity is invalid or duplicated")
        seen.add(key)
    return document


def publish(api: GitHub, raw: bytes, *, base: str = "master") -> dict:
    if base != "master":
        raise ValueError("refresh base must be master")
    validate_snapshot(raw)
    # Canonical bytes make formatting-only input changes idempotent.
    raw = (json.dumps(json.loads(raw), indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    digest = hashlib.sha256(raw).hexdigest()
    branch = "q/provider-recon-" + digest[:20]
    head = api.call("GET", "git/ref/heads/master")["object"]["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("invalid default-branch SHA")
    # Contents API returns 404 for first-run absent snapshot. The trees API avoids
    # treating an auth/transport failure as an absent file.
    base_tree = api.call("GET", "git/commits/" + head)["tree"]["sha"]
    tree = api.call("GET", f"git/trees/{base_tree}?recursive=1")
    if tree.get("truncated"):
        raise ValueError("cannot establish current snapshot from a truncated tree")
    entries = [entry for entry in tree["tree"] if entry["path"] == SNAPSHOT_PATH]
    if entries:
        blob = api.call("GET", "git/blobs/" + entries[0]["sha"])
        current = base64.b64decode(blob["content"])
        if current == raw:
            return {"status": "unchanged", "content_sha256": digest}
    quoted = urllib.parse.quote(f"timerloggedout-spec:{branch}", safe="")
    prs = api.call("GET", f"pulls?state=all&head={quoted}&per_page=100")
    if prs:
        pr = prs[0]
        # Re-dispatch known gates after an interrupted earlier publication.
        if pr["state"] == "open":
            for workflow in GATES:
                api.call("POST", f"actions/workflows/{workflow}/dispatches", {"ref": branch})
        return {"status": "existing", "url": pr["html_url"], "content_sha256": digest}
    refs = api.call("GET", "git/matching-refs/heads/" + branch)
    exact = [ref for ref in refs if ref["ref"] == "refs/heads/" + branch]
    if exact:
        # Never update an existing branch: recover only an identical snapshot.
        existing = api.call("GET", f"contents/{SNAPSHOT_PATH}?ref={branch}")
        if base64.b64decode(existing["content"]) != raw:
            raise ValueError("existing content-addressed branch differs; refusing overwrite")
    else:
        # Blob/tree/commit are unreachable until a single atomic ref creation;
        # failures cannot leave an empty branch that blocks retry recovery.
        blob = api.call("POST", "git/blobs", {"content": raw.decode(), "encoding": "utf-8"})
        new_tree = api.call("POST", "git/trees", {"base_tree": base_tree,
            "tree": [{"path": SNAPSHOT_PATH, "mode": "100644", "type": "blob", "sha": blob["sha"]}]})
        commit = api.call("POST", "git/commits", {
            "message": "chore(recon): refresh pinned provider research\n\nImplements: MSM-006",
            "tree": new_tree["sha"], "parents": [head]})
        api.call("POST", "git/refs", {"ref": "refs/heads/" + branch, "sha": commit["sha"]})
    pr = api.call("POST", "pulls", {"title": "chore(recon): refresh pinned free-provider research",
        "head": branch, "base": base,
        "body": "Implements: MSM-006\n\nGenerated research data only. Every candidate remains runtime-ineligible. "
            "No upstream code, inference, routing weights, credentials, workflows, or paid routes changed. "
            "Sources are commit-pinned with content hashes. Directory claims are not verified quotas.\n\n"
            "Promotion requires current-head dual gates and verified research-only outcome; "
            "this publisher cannot merge.\n\nSnapshot SHA256: `" + digest + "`"})
    # GITHUB_TOKEN-created PRs do not emit pull_request CI. Explicit dispatch
    # records the two required checks at this branch's actual head SHA.
    for workflow in GATES:
        api.call("POST", f"actions/workflows/{workflow}/dispatches", {"ref": branch})
    return {"status": "created", "url": pr["html_url"], "content_sha256": digest}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN")
    if not token:
        parser.error("GH_TOKEN is required; no credential is written to disk")
    print(json.dumps(publish(GitHub(token), args.snapshot.read_bytes()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
