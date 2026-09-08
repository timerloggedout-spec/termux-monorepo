#!/usr/bin/env python3
"""Report only whether governed fork pins lag their declared fork branches."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen


FORKS = {
    "refTemplates/smods/termux-mcp-server_fork": ("timerloggedout-spec/termux-mcp-server_fork", "master"),
    "refTemplates/smods/mcp-android-ssh_fork": ("timerloggedout-spec/mcp-android-ssh_fork", "main"),
    "refTemplates/smods/term_mcp_deepseek_fork": ("timerloggedout-spec/term_mcp_deepseek_fork-", "main"),
}


def gitlinks() -> dict[str, str]:
    output = subprocess.run(
        ["git", "ls-files", "--stage"], capture_output=True, text=True, check=True
    ).stdout.splitlines()
    result: dict[str, str] = {}
    for line in output:
        if not line.startswith("160000 ") or "\t" not in line:
            continue
        metadata, path = line.split("\t", 1)
        result[path] = metadata.split()[1]
    return result


def remote_head(repository: str, branch: str, token: str) -> str:
    request = Request(
        f"https://api.github.com/repos/{repository}/commits/{branch}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=20) as response:  # nosec B310: fixed GitHub API URL
        payload = json.load(response)
    return payload["sha"]


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("FAIL: GITHUB_TOKEN is required for the read-only fork audit", file=sys.stderr)
        return 2
    pins = gitlinks()
    drift = False
    for path, (repository, branch) in FORKS.items():
        pin = pins.get(path)
        if not pin:
            print(f"FAIL: missing pinned Git link for {path}", file=sys.stderr)
            drift = True
            continue
        head = remote_head(repository, branch, token)
        state = "CURRENT" if pin == head else "UPDATE_AVAILABLE"
        print(f"{state} {path}: pinned={pin} head={head}")
        drift = drift or state == "UPDATE_AVAILABLE"
    print("INFO: this workflow reports drift only; it never advances submodule pins.")
    return 0 if not drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
