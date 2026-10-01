#!/usr/bin/env python3
"""Validate governed Termux fork submodules under refTemplates/smods."""

from __future__ import annotations

import configparser
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GITMODULES = ROOT / ".gitmodules"
SMODS_PREFIX = "refTemplates/smods/"
# Hard checks for operator-owned forks (URL must match + gitlink present).
REQUIRED = {
    "refTemplates/smods/termux-mcp-server_fork": "https://github.com/timerloggedout-spec/termux-mcp-server_fork.git",
    "refTemplates/smods/mcp-android-ssh_fork": "https://github.com/timerloggedout-spec/mcp-android-ssh_fork.git",
    "refTemplates/smods/term_mcp_deepseek_fork": "https://github.com/timerloggedout-spec/term_mcp_deepseek_fork-.git",
    "refTemplates/smods/batteries_fork": "https://github.com/timerloggedout-spec/batteries_fork.git",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.read(GITMODULES, encoding="utf-8")
    discovered: dict[str, str] = {}
    for section in parser.sections():
        if not section.startswith("submodule "):
            continue
        path = parser.get(section, "path", fallback="")
        url = parser.get(section, "url", fallback="")
        if path:
            discovered[path] = url

    smods = {p: u for p, u in discovered.items() if p.startswith(SMODS_PREFIX)}
    if not smods:
        fail("no refTemplates/smods/* entries in .gitmodules")

    for path, expected_url in REQUIRED.items():
        actual_url = discovered.get(path)
        if actual_url != expected_url:
            fail(f"{path}: expected user-owned fork remote {expected_url!r}, got {actual_url!r}")

    listing = subprocess.run(
        ["git", "ls-files", "--stage"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    gitlinks = {
        line.split("\t", 1)[1]
        for line in listing
        if line.startswith("160000 ") and "\t" in line
    }

    status = subprocess.run(
        ["git", "submodule", "status", "--cached"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    drift: list[str] = []
    for path in sorted(smods):
        if path not in gitlinks:
            msg = f"{path}: listed in .gitmodules but missing 160000 gitlink in index"
            if path in REQUIRED:
                fail(msg)
            drift.append(msg)
            print(f"WARN: {msg}", file=sys.stderr)
            continue
        if path not in status:
            msg = f"{path}: not present in cached submodule status"
            if path in REQUIRED:
                fail(msg)
            drift.append(msg)
            print(f"WARN: {msg}", file=sys.stderr)

    for path in REQUIRED:
        if path not in gitlinks:
            fail(f"{path}: missing pinned gitlink in the superproject index")
        if path not in status:
            fail(f"{path}: not present in cached submodule status")

    print(
        f"OK: validated {len(REQUIRED)} governed forks; "
        f"{len(smods)} smods entries; {len(drift)} non-required drift warning(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
