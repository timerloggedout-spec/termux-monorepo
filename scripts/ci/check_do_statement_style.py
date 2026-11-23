#!/usr/bin/env python3
"""Check action-first wording in repository instructions and collaboration text."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH", "")
EVENT_NAME = os.environ.get("GITHUB_EVENT_NAME", "")
BASE_REF = os.environ.get("GITHUB_BASE_REF", "")
NEGATIVE_FIRST = re.compile(
    r"^\s*(?:(?:[-*]\s*)|(?:#+\s*))?(?:do not|don't|never|no\b|not\b|avoid\b)",
    re.IGNORECASE,
)
IMPERATIVE = {
    "accept", "account", "allow", "add", "align", "apply", "assert", "audit", "bind", "build", "bump", "check", "clarify", "close",
    "correct", "cover", "centralize", "export", "format", "implement", "initialize", "invoke", "isolate", "link", "normalize",
    "parse", "pin", "recognize", "reject", "sort",
    "compare", "create", "define", "deploy", "document", "enforce", "expand", "fix", "gate",
    "include", "inspect", "keep", "measure", "migrate", "move", "open", "preserve", "guard", "surface",
    "publish", "record", "reconcile", "refresh", "refine", "register", "remove", "rename", "repair",
    "replace", "require", "restore", "route", "run", "set", "snapshot", "split", "sync",
    "test", "update", "use", "validate", "verify", "wire", "collect", "generate", "regenerate", "rebuild",
}
STYLE_PATHS = [
    "AGENTS.md", "moniker.md", "CLAUDE.md", "GEMINI.md", "SKILLS.md", "CONTRIBUTING.md",
    ".agents/skills", ".github/skills", ".github/workflows",
    "docs/ops", "docs/proposals",
]

errors: list[str] = []


def inspect_text(label: str, value: str) -> None:
    for number, line in enumerate(value.splitlines(), 1):
        if NEGATIVE_FIRST.match(line):
            errors.append(f"{label}:{number}: lead with the intended DO action")


def run_git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout


def inspect_added_lines(label: str, diff: str) -> None:
    current_path = label
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            added = line[1:]
            if NEGATIVE_FIRST.match(added):
                errors.append(
                    f"{current_path}: lead with the intended DO action: {added.strip()}"
                )


def inspect_git_range(base: str, head: str) -> None:
    diff = run_git(
        "diff", "--unified=0", f"{base}...{head}", "--", *STYLE_PATHS
    )
    inspect_added_lines("changed-file", diff)

    subjects = run_git(
        "log", "--no-merges", f"{base}..{head}", "--format=%s"
    ).splitlines()
    bodies = run_git(
        "log", "--no-merges", f"{base}..{head}", "--format=%b"
    )
    inspect_text("commit.body", bodies)
    for subject in subjects:
        scoped = re.match(r"^[a-z][a-z0-9-]*(?:\([^)]+\))?:\s*(.+)$", subject)
        description = scoped.group(1) if scoped else subject
        first = description.split(maxsplit=1)
        verb = first[0].lower() if first else ""
        if verb not in IMPERATIVE:
            errors.append(
                f"commit subject requires an imperative action verb after its scope: {subject}"
            )


def is_style_path(path: str) -> bool:
    return any(
        path == item or path.startswith(item.rstrip("/") + "/")
        for item in STYLE_PATHS
    )


def inspect_worktree() -> None:
    """Inspect staged + unstaged tracked edits and untracked instruction files."""
    diff = run_git("diff", "--unified=0", "HEAD", "--", *STYLE_PATHS)
    inspect_added_lines("working-tree", diff)

    untracked = run_git("ls-files", "--others", "--exclude-standard", "-z")
    for raw_path in untracked.split("\0"):
        if not raw_path or not is_style_path(raw_path):
            continue
        path = Path(raw_path)
        try:
            inspect_text(raw_path, path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            errors.append(f"{raw_path}: UTF-8 decode failed; inspect the file encoding")


def inspect_pr_commits() -> None:
    if EVENT_NAME != "pull_request" or not BASE_REF:
        return
    subprocess.run(["git", "fetch", "origin", BASE_REF], check=True)
    inspect_git_range(f"origin/{BASE_REF}", "HEAD")


def inspect_push_commits(event: dict) -> None:
    if EVENT_NAME != "push":
        return
    before = event.get("before") or ""
    after = event.get("after") or "HEAD"
    if not before or set(before) == {"0"}:
        return
    inspect_git_range(before, after)


def inspect_event(event: dict) -> None:
    if EVENT_NAME == "pull_request":
        inspect_text("pull_request.title", event.get("pull_request", {}).get("title") or "")
        inspect_text("pull_request.body", event.get("pull_request", {}).get("body") or "")
    elif EVENT_NAME == "issues":
        inspect_text("issue.title", event.get("issue", {}).get("title") or "")
        inspect_text("issue.body", event.get("issue", {}).get("body") or "")
    elif EVENT_NAME == "discussion":
        inspect_text("discussion.title", event.get("discussion", {}).get("title") or "")
        inspect_text("discussion.body", event.get("discussion", {}).get("body") or "")
    elif EVENT_NAME in {
        "issue_comment", "pull_request_review_comment",
        "discussion_comment", "commit_comment",
    }:
        inspect_text("comment.body", event.get("comment", {}).get("body") or "")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight DO-first language before commit or collaboration."
    )
    parser.add_argument(
        "--preflight", action="store_true",
        help="inspect the local branch, worktree, untracked instruction files, and draft text",
    )
    parser.add_argument(
        "--base", help="base branch/ref for local preflight, e.g. origin/master",
    )
    parser.add_argument(
        "--text-file", action="append", default=[],
        help="draft comment/PR/issue text file; repeat for multiple drafts",
    )
    args = parser.parse_args()

    if args.preflight:
        base = args.base or "origin/master"
        if subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"],
            capture_output=True,
        ).returncode != 0:
            print(f"DO-statement preflight: BLOCKED — base ref unavailable: {base}")
            return 2
        inspect_git_range(base, "HEAD")
        inspect_worktree()
        for filename in args.text_file:
            path = Path(filename)
            if not path.is_file():
                errors.append(f"{filename}: draft file unavailable")
                continue
            inspect_text(filename, path.read_text(encoding="utf-8"))
    else:
        if not EVENT_PATH or not Path(EVENT_PATH).is_file():
            print(
                "DO-statement style: local invocation requires "
                "--preflight --base <ref>; CI invocation requires GITHUB_EVENT_PATH"
            )
            return 2
        event = json.loads(Path(EVENT_PATH).read_text(encoding="utf-8"))
        inspect_pr_commits()
        inspect_push_commits(event)
        inspect_event(event)

    if errors:
        print("DO-statement style: FAIL")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)

    print("DO-statement style: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
