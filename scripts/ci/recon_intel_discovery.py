#!/usr/bin/env python3
"""Read-only GitHub–GitLab topology classification for RECON INTEL.

The helper is intentionally limited to fetching one allowlisted GitLab ref into the
current checkout and emitting a SHA-bound, metadata-only result. It never pushes,
creates GitHub resources, invokes providers, or writes credentials to disk.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".github" / "agentic" / "recon-intel-policy.json"
DEFAULT_GITLAB_REMOTE = "https://gitlab.com/a-group2180532/termux-monorepo.git"


@dataclass(frozen=True)
class DiscoveryResult:
    state: str
    lane: str
    github_sha: str
    gitlab_sha: str
    gitlab_ref: str
    policy_version: str
    detail: str


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def classify_topology(
    github_sha: str,
    gitlab_sha: str,
    has_merge_base: Callable[[str, str], bool],
    is_ancestor: Callable[[str, str], bool],
) -> str:
    if github_sha == gitlab_sha:
        return "aligned"
    if not has_merge_base(github_sha, gitlab_sha):
        return "no-common-ancestor"
    if is_ancestor(gitlab_sha, github_sha):
        return "github-ahead"
    if is_ancestor(github_sha, gitlab_sha):
        return "gitlab-ahead"
    return "diverged"


def run_git(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_exit_is_zero(args: list[str]) -> bool:
    return run_git(args).returncode == 0


def create_askpass() -> Path:
    handle = tempfile.NamedTemporaryFile("w", prefix="recon-intel-askpass-", delete=False)
    try:
        handle.write(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  *Username*) printf '%s\\n' 'oauth2' ;;\n"
            "  *Password*) printf '%s\\n' \"${RECON_INTEL_GITLAB_READ_TOKEN:?missing token}\" ;;\n"
            "  *) exit 1 ;;\n"
            "esac\n"
        )
        handle.flush()
    finally:
        handle.close()
    path = Path(handle.name)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def fetch_gitlab_ref(gitlab_ref: str, token: str) -> tuple[bool, str, str]:
    askpass = create_askpass()
    try:
        env = os.environ.copy()
        env.update(
            {
                "GIT_ASKPASS": str(askpass),
                "GIT_TERMINAL_PROMPT": "0",
                "RECON_INTEL_GITLAB_READ_TOKEN": token,
            }
        )
        local_ref = f"refs/recon-intel/gitlab/{gitlab_ref}"
        result = subprocess.run(
            [
                "git",
                "fetch",
                "--no-tags",
                "--no-recurse-submodules",
                DEFAULT_GITLAB_REMOTE,
                f"+refs/heads/{gitlab_ref}:{local_ref}",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            return False, "", "GitLab read fetch was denied or unavailable."
        sha = run_git(["rev-parse", local_ref]).stdout.strip()
        if not sha:
            return False, "", "GitLab ref did not resolve to a commit SHA."
        return True, sha, "GitLab ref fetched with a dedicated read credential."
    finally:
        askpass.unlink(missing_ok=True)


def discovery_result(github_sha: str, gitlab_ref: str, token: str) -> DiscoveryResult:
    policy = load_policy()
    states = policy["lease_states"]
    policy_version = policy["policy_version"]
    if gitlab_ref not in policy["discovery"]["allowed_gitlab_refs"]:
        return DiscoveryResult(
            "external-access-denied",
            states["external-access-denied"]["lane"],
            github_sha,
            "",
            gitlab_ref,
            policy_version,
            "GitLab ref is not allowlisted by the RECON INTEL policy.",
        )
    if not token:
        return DiscoveryResult(
            "not-configured",
            states["not-configured"]["lane"],
            github_sha,
            "",
            gitlab_ref,
            policy_version,
            "RECON_INTEL_GITLAB_READ_TOKEN is not configured; discovery is advisory only.",
        )
    fetched, gitlab_sha, detail = fetch_gitlab_ref(gitlab_ref, token)
    if not fetched:
        return DiscoveryResult(
            "external-access-denied",
            states["external-access-denied"]["lane"],
            github_sha,
            "",
            gitlab_ref,
            policy_version,
            detail,
        )
    state = classify_topology(
        github_sha,
        gitlab_sha,
        lambda left, right: git_exit_is_zero(["merge-base", "--is-ancestor", left, right])
        or git_exit_is_zero(["merge-base", "--is-ancestor", right, left])
        or run_git(["merge-base", left, right]).returncode == 0,
        lambda left, right: git_exit_is_zero(["merge-base", "--is-ancestor", left, right]),
    )
    return DiscoveryResult(state, states[state]["lane"], github_sha, gitlab_sha, gitlab_ref, policy_version, detail)


def emit(result: DiscoveryResult, output_path: str | None) -> None:
    fields = {
        "state": result.state,
        "lane": result.lane,
        "github_sha": result.github_sha,
        "gitlab_sha": result.gitlab_sha,
        "gitlab_ref": result.gitlab_ref,
        "policy_version": result.policy_version,
        "detail": result.detail,
    }
    for key, value in fields.items():
        print(f"{key}={value}")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as handle:
            for key, value in fields.items():
                handle.write(f"{key}={value}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github-sha", required=True)
    parser.add_argument("--gitlab-ref", default="master")
    parser.add_argument("--output", default=os.environ.get("GITHUB_OUTPUT"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = discovery_result(
        github_sha=args.github_sha.strip(),
        gitlab_ref=args.gitlab_ref.strip(),
        token=os.environ.get("RECON_INTEL_GITLAB_READ_TOKEN", ""),
    )
    emit(result, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
