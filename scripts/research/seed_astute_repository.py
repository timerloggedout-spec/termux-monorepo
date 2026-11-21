#!/usr/bin/env python3
"""Seed a newly created Research Astute repository through the GitHub Contents API.

The workflow owns repository creation and credential custody. This script performs
create-only file writes from the checked-out, reviewed platform and experiment tree.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = os.environ["TARGET_REPO"]
SOURCE = os.environ["GITHUB_REPOSITORY"]
FILES = [
    ROOT / "templates" / "research-astute" / "README.md",
    ROOT / "research" / "astute-platform",
    ROOT / "research" / "astute-computational-limits",
    ROOT / "scripts" / "research" / "validate_astute.py",
    ROOT / ".github" / "workflows" / "research-astute-validate.yml",
]


def gh(*args: str, data: str | None = None) -> tuple[int, str, str]:
    result = subprocess.run(
        ["gh", "api", *args],
        input=data,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def collect_files() -> dict[str, str]:
    files: dict[str, str] = {}
    for item in FILES:
        if item.is_file():
            files["README.md" if item.name == "README.md" else item.relative_to(ROOT).as_posix()] = item.read_text(encoding="utf-8")
        elif item.is_dir():
            for path in sorted(item.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    files[path.relative_to(ROOT).as_posix()] = path.read_text(encoding="utf-8")
    return files


def main() -> int:
    files = collect_files()
    workflow_path = ".github/workflows/research-astute-validate.yml"
    if workflow_path not in files:
        raise RuntimeError("standalone validation workflow is absent from the seed set")

    order = sorted(files, key=lambda path: (path == workflow_path, path))
    created, kept, failed = [], [], []
    for path in order:
        status, _, _ = gh(f"repos/{TARGET}/contents/{path}")
        if status == 0:
            kept.append(path)
            continue
        payload = {
            "message": f"research: seed {path} from {SOURCE}",
            "content": base64.b64encode(files[path].encode("utf-8")).decode("ascii"),
        }
        status, output, error = gh(
            "-X", "PUT", f"repos/{TARGET}/contents/{path}", "--input", "-",
            data=json.dumps(payload),
        )
        if status == 0:
            created.append(path)
        else:
            failed.append(path)
            print(f"::error title=research-seed::{path} refused: {(output + error).strip()[:240]}", file=sys.stderr)

    print(f"::notice title=research-seed::target={TARGET} created={len(created)} kept={len(kept)} failed={len(failed)}")
    if failed:
        return 1
    print(json.dumps({"target": TARGET, "created": created, "kept": kept}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
