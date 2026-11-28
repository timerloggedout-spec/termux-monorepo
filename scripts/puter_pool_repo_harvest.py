#!/usr/bin/env python3
"""Harvest a safe source manifest from a local Puter Pool repository checkout.

The manifest records allowlisted source paths, byte counts, SHA-256 digests,
and route/schema capability names. It excludes environment files, databases,
account tokens, browser storage, request bodies, and runtime history.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SOURCE_REPOSITORY = "timerloggedout-spec/puter-pool_fork"
ALLOWLIST = (
    "README.md", "package.json", "src/index.ts", "src/config/index.ts",
    "src/api/openai.ts", "src/api/anthropic.ts", "src/api/routes.ts",
    "src/api/middleware.ts", "src/scheduler/RequestScheduler.ts",
    "src/credit/CreditTracker.ts", "src/database/index.ts", "src/types.ts",
    "tests/integration.test.ts", "tests/scheduler.test.ts",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _revision(root: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=3,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def harvest(root: str | Path) -> dict[str, Any]:
    base = Path(root).resolve()
    files = []
    text_by_path: dict[str, str] = {}
    for relative in ALLOWLIST:
        path = base / relative
        if not path.is_file() or path.is_symlink():
            continue
        files.append({"path": relative, "size_bytes": path.stat().st_size, "sha256": _sha256(path)})
        if path.suffix in {".ts", ".json", ".md"} and path.stat().st_size <= 2 * 1024 * 1024:
            text_by_path[relative] = path.read_text(encoding="utf-8", errors="replace")
    all_source = "\n".join(text_by_path.values())
    routes = sorted(set(re.findall(r"""(?:router|app)\.(?:get|post|put|patch|delete)\(['"]([^'"]+)""", all_source)))
    tables = sorted(set(re.findall(r"CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_]+)", all_source, flags=re.I)))
    events = sorted(set(re.findall(r"""['"]((?:request|credit|account):[a-zA-Z0-9:_-]+)['"]""", all_source)))
    return {
        "schema": "provider-source-harvest/v1",
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": _revision(base),
        "harvested_files": files,
        "capabilities": {
            "http_routes": routes,
            "sqlite_tables": tables,
            "event_names": events,
            "scheduler_strategies": ["round-robin", "least-used"],
            "openai_compatible": "src/api/openai.ts" in text_by_path,
            "anthropic_compatible": "src/api/anthropic.ts" in text_by_path,
        },
        "exclusions": {
            "environment_files": True, "database_files": True,
            "account_credentials": True, "browser_storage": True,
            "request_prompts_and_completions": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output", default="/tmp/provider-source-harvest/puter-pool.json")
    args = parser.parse_args(argv)
    document = harvest(args.repo_root)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"source={SOURCE_REPOSITORY} files={len(document['harvested_files'])} revision={document['source_revision'] or 'unavailable'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
