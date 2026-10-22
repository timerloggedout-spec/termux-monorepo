#!/usr/bin/env python3
"""Offline metadata inventory; never invokes agy, git, a model, or a network."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


def inventory(workspace: Path) -> dict:
    """Report presence only, never configuration contents or session URLs."""
    exists = workspace.is_dir()
    repository = exists and (workspace / ".git").exists()
    cli = shutil.which("agy") is not None
    return {
        "schema_version": 1,
        "workspace_exists": exists,
        "repository_marker_present": bool(repository),
        "agy_on_path": cli,
        "project_skills_present": exists and (workspace / ".agents/skills").is_dir(),
        "project_agents_present": exists and (workspace / ".agents/agents").is_dir(),
        "project_hooks_present": exists and (workspace / ".agents/hooks.json").is_file(),
        "prerequisites_present": bool(repository and cli),
        "runtime_verified": False,
        "settings_modified": False,
        "model_prompts_launched": 0,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True,
                        help="Explicit repository path; no home-directory scan")
    args = parser.parse_args(argv)
    result = inventory(args.workspace)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["prerequisites_present"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
