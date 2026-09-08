#!/usr/bin/env python3
"""Read-only GitHub–GitLab topology classification for RECON INTEL.

The helper first attempts a single allowlisted Git ref fetch. If Git transport is
unavailable but the token has GitLab REST project access, it resolves the GitLab
branch and compares commit topology through read-only REST endpoints. It never
pushes, creates GitHub resources, invokes providers, or writes credentials to
disk.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".github" / "agentic" / "recon-intel-policy.json"
GITLAB_PROJECT = "a-group2180532/termux-monorepo"
GITLAB_PROJECT_PATH = urllib.parse.quote(GITLAB_PROJECT, safe="")
GITLAB_API = "https://gitlab.com/api/v4"
GITHUB_API = "https://api.github.com"
GITHUB_REPOSITORY = "timerloggedout-spec/termux-monorepo"
MIRROR_HISTORY_WINDOW = 100
DEFAULT_GITLAB_REMOTE = f"https://gitlab.com/{GITLAB_PROJECT}.git"


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


def classify_commit_counts(github_only: int, gitlab_only: int) -> str:
    if github_only == 0 and gitlab_only == 0:
        return "aligned"
    if github_only > 0 and gitlab_only == 0:
        return "github-ahead"
    if gitlab_only > 0 and github_only == 0:
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
            return False, "", "GitLab Git transport was denied or unavailable."
        sha = run_git(["rev-parse", local_ref]).stdout.strip()
        if not sha:
            return False, "", "GitLab ref did not resolve to a commit SHA."
        return True, sha, "GitLab ref fetched through read-only Git transport."
    finally:
        askpass.unlink(missing_ok=True)


def rest_get(path: str, token: str, query: list[tuple[str, str]] | None = None) -> tuple[int, dict]:
    suffix = f"?{urllib.parse.urlencode(query or [])}" if query else ""
    request = urllib.request.Request(
        f"{GITLAB_API}{path}{suffix}",
        headers={"PRIVATE-TOKEN": token, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, {}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return 0, {}


def github_rest_get(path: str, token: str, query: list[tuple[str, str]] | None = None) -> tuple[int, object]:
    suffix = f"?{urllib.parse.urlencode(query or [])}" if query else ""
    request = urllib.request.Request(
        f"{GITHUB_API}{path}{suffix}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, {}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return 0, {}


def rest_compare_counts(gitlab_sha: str, github_sha: str, token: str) -> tuple[bool, int, int]:
    status, payload = rest_get(
        f"/projects/{GITLAB_PROJECT_PATH}/repository/diverging_commits",
        token,
        [("from", gitlab_sha), ("to", github_sha), ("max_count", "1")],
    )
    if status == 200 and isinstance(payload.get("ahead"), int) and isinstance(payload.get("behind"), int):
        return True, payload["ahead"], payload["behind"]
    forward_status, forward = rest_get(
        f"/projects/{GITLAB_PROJECT_PATH}/repository/compare",
        token,
        [("from", gitlab_sha), ("to", github_sha), ("straight", "true")],
    )
    reverse_status, reverse = rest_get(
        f"/projects/{GITLAB_PROJECT_PATH}/repository/compare",
        token,
        [("from", github_sha), ("to", gitlab_sha), ("straight", "true")],
    )
    if forward_status == 200 and reverse_status == 200:
        return True, len(forward.get("commits", [])), len(reverse.get("commits", []))
    return False, 0, 0


def mirror_history_counts(github_sha: str, gitlab_sha: str, gitlab_token: str, github_token: str) -> tuple[bool, int, int, str]:
    """Return native-platform distances to the nearest shared mirror commit.

    GitLab cannot compare a GitHub-only tip directly, and GitHub cannot compare a
    GitLab-only tip directly. A bounded overlap of native first-parent histories
    establishes the shared mirror anchor without checking out either untrusted
    ref or giving either platform write authority.
    """
    if not github_token:
        return False, 0, 0, "GitHub read token was unavailable for mirror-history overlap detection."
    github_status, github_history = github_rest_get(
        f"/repos/{GITHUB_REPOSITORY}/commits",
        github_token,
        [("sha", github_sha), ("per_page", str(MIRROR_HISTORY_WINDOW))],
    )
    gitlab_status, gitlab_history = rest_get(
        f"/projects/{GITLAB_PROJECT_PATH}/repository/commits",
        gitlab_token,
        [("ref_name", gitlab_sha), ("per_page", str(MIRROR_HISTORY_WINDOW))],
    )
    if github_status != 200 or not isinstance(github_history, list) or gitlab_status != 200 or not isinstance(gitlab_history, list):
        return False, 0, 0, "Native mirror-history lookup was denied or unavailable."
    github_commits = [str(item.get("sha", "")) for item in github_history if isinstance(item, dict)]
    gitlab_commits = [str(item.get("id", "")) for item in gitlab_history if isinstance(item, dict)]
    gitlab_positions = {sha: index for index, sha in enumerate(gitlab_commits) if sha}
    candidates = [
        (max(github_index, gitlab_positions[sha]), github_index, gitlab_positions[sha], sha)
        for github_index, sha in enumerate(github_commits)
        if sha in gitlab_positions
    ]
    if not candidates:
        return False, 0, 0, f"No shared commit appeared within the bounded {MIRROR_HISTORY_WINDOW}-commit mirror-history windows."
    _, github_only, gitlab_only, anchor = min(candidates)
    return True, github_only, gitlab_only, f"Native GitHub and GitLab histories share anchor {anchor[:12]}."


def rest_gitlab_discovery(github_sha: str, gitlab_ref: str, token: str, github_token: str) -> tuple[str, str, str]:
    branch_status, branch = rest_get(
        f"/projects/{GITLAB_PROJECT_PATH}/repository/branches/{urllib.parse.quote(gitlab_ref, safe='')}",
        token,
    )
    gitlab_sha = str(branch.get("commit", {}).get("id", "")) if branch_status == 200 else ""
    if not gitlab_sha:
        return "external-access-denied", "", "GitLab REST branch lookup was denied or unavailable."
    if github_sha == gitlab_sha:
        return "aligned", gitlab_sha, "GitLab REST comparison found matching commit SHAs."
    base_status, _ = rest_get(
        f"/projects/{GITLAB_PROJECT_PATH}/repository/merge_base",
        token,
        [("refs[]", gitlab_sha), ("refs[]", github_sha)],
    )
    if base_status == 200:
        compared, github_only, gitlab_only = rest_compare_counts(gitlab_sha, github_sha, token)
        if compared:
            state = classify_commit_counts(github_only, gitlab_only)
            return state, gitlab_sha, "GitLab Git transport was unavailable; read-only REST topology comparison succeeded."
    elif base_status not in {400, 404}:
        return "external-access-denied", gitlab_sha, "GitLab REST merge-base lookup was denied or unavailable."

    # GitLab cannot name a GitHub-only tip, so establish the mirror relation from
    # each platform's own bounded history instead of treating the missing foreign
    # SHA as evidence of unrelated repositories.
    overlapping, github_only, gitlab_only, mirror_detail = mirror_history_counts(
        github_sha, gitlab_sha, token, github_token
    )
    if overlapping:
        state = classify_commit_counts(github_only, gitlab_only)
        return state, gitlab_sha, f"GitLab Git transport was unavailable; {mirror_detail}"
    if mirror_detail.startswith("No shared commit"):
        return "no-common-ancestor", gitlab_sha, mirror_detail
    return "external-access-denied", gitlab_sha, mirror_detail


def discovery_result(github_sha: str, gitlab_ref: str, token: str, github_token: str = "") -> DiscoveryResult:
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
    if fetched:
        state = classify_topology(
            github_sha,
            gitlab_sha,
            lambda left, right: git_exit_is_zero(["merge-base", "--is-ancestor", left, right])
            or git_exit_is_zero(["merge-base", "--is-ancestor", right, left])
            or run_git(["merge-base", left, right]).returncode == 0,
            lambda left, right: git_exit_is_zero(["merge-base", "--is-ancestor", left, right]),
        )
        return DiscoveryResult(state, states[state]["lane"], github_sha, gitlab_sha, gitlab_ref, policy_version, detail)
    state, gitlab_sha, rest_detail = rest_gitlab_discovery(github_sha, gitlab_ref, token, github_token)
    return DiscoveryResult(state, states[state]["lane"], github_sha, gitlab_sha, gitlab_ref, policy_version, rest_detail)


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
        github_token=os.environ.get("GITHUB_TOKEN", ""),
    )
    emit(result, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
