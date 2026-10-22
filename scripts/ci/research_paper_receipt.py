#!/usr/bin/env python3
"""Emit attributable offline validation metadata; never infer task completion."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def receipt(root: Path, artifacts: list[Path]) -> dict:
    def git(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()

    patterns = (
        "integrations/swarms/", "src/advanced_research", "src/swarms_", "src/telemetry.py",
        "llm_api_hub/", "scripts/model_selection_market/", "scripts/ci/research_paper_receipt.py",
        "tests/test_advanced_research", "tests/test_research_", "tests/test_paper_accounting",
        ".github/workflows/research-paper-validation.yml", ".github/workflows/swarms-validation.yml",
        "scripts/telemetry/research_evidence.py", "scripts/provider_quota_managers.py",
        "ops/quota/provider-managers.json", "tests/hub_quota_fixture.py", "tests/test_swarms",
        "tests/test_llm_api_hub_server.py", "tests/test_msm_paper_wallet.py",
        "scripts/ci/repo_gate.py", "scripts/ci/termux_smoke.py",
    )
    tracked = git("ls-files").splitlines()
    sources = {}
    for name in tracked:
        path = root / name
        if name.startswith(patterns) and path.is_file() and not path.is_symlink():
            sources[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    evidence = {}
    for path in artifacts:
        if not path.is_file() or path.is_symlink():
            raise ValueError("evidence artifact must be an existing regular file")
        evidence[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "schema": "research-paper-validation/v1",
        "candidate_sha": git("rev-parse", "HEAD"),
        "workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF"),
        "workflow_sha": os.environ.get("GITHUB_WORKFLOW_SHA"),
        "actions_run_id": os.environ.get("GITHUB_RUN_ID"),
        "actions_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "execution_environment": "Linux; not native Android evidence",
        "inference": "deterministic fake only",
        "task_outcome": "UNKNOWN",
        "merged_or_deployed": False,
        "dirty_tracked_files": bool(git("diff", "HEAD", "--name-only")),
        "source_sha256": dict(sorted(sources.items())),
        "artifact_sha256": dict(sorted(evidence.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = receipt(ROOT, args.artifact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
