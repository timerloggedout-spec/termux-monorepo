#!/usr/bin/env python3
"""Build deterministic, proposal-scoped Delphi trigger receipts.

This tool is intentionally offline: it never dispatches another workflow, invokes a
provider, or treats a proposal change as a vote/consensus. The Actions workflow runs
one matrix job per changed proposal identity and stores the resulting receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/proposals/registry.yaml"
PROPOSALS_ROOT = ROOT / "docs/proposals"
ELIGIBILITY_KEYS = ("delphi_trigger: true", "delphi-trigger: true", "participation_lane: delphic-anonymity-method")


def load_yaml(path: Path):
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required for proposal trigger receipts") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def changed_proposal_ids(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    ids = set()
    for name in result.stdout.splitlines():
        match = re.match(r"^docs/proposals/(?:active|closed)/([^/]+)/", name)
        if match:
            ids.add(match.group(1))
    return sorted(ids)


def registry_entries():
    data = load_yaml(REGISTRY)
    if not isinstance(data, dict) or not isinstance(data.get("proposals"), list):
        raise ValueError("registry must contain a proposals list")
    entries = {}
    for item in data["proposals"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("every proposal registry entry must have a string id")
        pid = item["id"]
        if pid in entries:
            raise ValueError(f"duplicate proposal id: {pid}")
        entries[pid] = item
    return entries


def build_receipt(proposal_id: str, source_sha: str, entries: dict) -> dict:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,99}", proposal_id):
        raise ValueError(f"invalid proposal id: {proposal_id!r}")
    item = entries.get(proposal_id)
    if item is None:
        return {
            "schema_version": "proposal-delphi-trigger-receipt.v1",
            "proposal_id": proposal_id,
            "source_sha": source_sha,
            "status": "not_triggered",
            "reason": "proposal_id_not_registered",
        }
    rel = str(item.get("path") or f"active/{proposal_id}/").rstrip("/")
    if rel.startswith("/") or ".." in Path(rel).parts or not rel.startswith(("active/", "closed/")):
        raise ValueError(f"{proposal_id}: unsafe proposal path {rel!r}")
    manifest = PROPOSALS_ROOT / rel / "MANIFEST.md"
    if not manifest.is_file():
        raise ValueError(f"{proposal_id}: manifest missing at {manifest.relative_to(ROOT)}")
    content = manifest.read_text(encoding="utf-8")
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    explicit_opt_in = any(key in content.lower() for key in ELIGIBILITY_KEYS)
    title = str(item.get("title", ""))
    marker = bool(re.search(r"delphic.?anonymity|contributor.?participation", proposal_id + " " + title, re.I))
    eligible = explicit_opt_in or marker
    return {
        "schema_version": "proposal-delphi-trigger-receipt.v1",
        "proposal_id": proposal_id,
        "proposal_path": f"docs/proposals/{rel}/",
        "source_sha": source_sha,
        "manifest_sha256": digest,
        "trigger": "proposal_change_or_manual_dispatch",
        "status": "triggered" if eligible else "not_triggered",
        "reason": "explicit_delphi_participation_opt_in" if eligible else "proposal_not_marked_for_delphi_participation",
        "registry_status": str(item.get("status", "unknown")),
        "receipt_scope": "deterministic_workflow_trigger_only",
        "does_not_assert": ["human_participation", "anonymity", "vote", "consensus", "experiment_success"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-changed", nargs=2, metavar=("BASE", "HEAD"))
    parser.add_argument("--proposal-id")
    parser.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA", "unknown"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.list_changed:
            print(json.dumps({"include": [{"proposal_id": pid} for pid in changed_proposal_ids(*args.list_changed)]}))
            return 0
        if not args.proposal_id:
            parser.error("--proposal-id is required unless --list-changed is used")
        receipt = build_receipt(args.proposal_id, args.source_sha, registry_entries())
        rendered = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
