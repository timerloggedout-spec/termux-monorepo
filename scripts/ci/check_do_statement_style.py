#!/usr/bin/env python3
"""Check action-first wording in changed repository instructions and collaboration text."""
from __future__ import annotations

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
    "accept", "add", "align", "apply", "audit", "block", "build", "bump", "check", "close",
    "compare", "create", "define", "deploy", "document", "enforce", "expand", "fix", "gate",
    "include", "inspect", "keep", "measure", "migrate", "move", "open", "preserve",
    "publish", "record", "reconcile", "refresh", "refine", "register", "remove", "rename", "repair",
    "replace", "require", "restore", "route", "run", "set", "skip", "snapshot", "split", "sync",
    "test", "update", "use", "validate", "verify", "wire", "prevent", "collect", "generate", "regenerate", "rebuild",
}
STYLE_PATHS = [
    "AGENTS.md", "moniker.md", "CLAUDE.md", "GEMINI.md", "SKILLS.md",
    ".agents/skills", ".github/skills", ".github/workflows",
    "docs/ops", "docs/proposals",
]

errors: list[str] = []


def inspect_text(label: str, value: str) -> None:
    for number, line in enumerate(value.splitlines(), 1):
        if NEGATIVE_FIRST.match(line):
            errors.append(f"{label}:{number}: lead with the intended DO action")


def subject_verb(subject: str) -> str:
    first = subject.rsplit(": ", 1)[-1].split(maxsplit=1)
    return first[0].lower() if first else ""


def commit_subjects(base: str, head: str) -> list[str]:
    return subprocess.run(
        ["git", "log", "--no-merges", f"{base}..{head}", "--format=%s"],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()


def commit_bodies(base: str, head: str) -> str:
    return subprocess.run(
        ["git", "log", "--no-merges", f"{base}..{head}", "--format=%b"],
        check=True, capture_output=True, text=True,
    ).stdout


def inspect_git_range(base: str, head: str) -> None:
    diff = subprocess.run(
        ["git", "diff", "--unified=0", f"{base}...{head}", "--", *STYLE_PATHS],
        check=True, capture_output=True, text=True,
    ).stdout
    current_path = "changed-file"
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            added = line[1:]
            if NEGATIVE_FIRST.match(added):
                errors.append(
                    f"{current_path}: lead with the intended DO action: {added.strip()}"
                )

    inspect_text("commit.body", commit_bodies(base, head))
    for subject in commit_subjects(base, head):
        verb = subject_verb(subject)
        if verb not in IMPERATIVE:
            errors.append(
                f"commit subject requires an imperative action verb after its scope: {subject}"
            )


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


def inspect_event() -> None:
    if not EVENT_PATH or not Path(EVENT_PATH).is_file():
        return
    event = json.loads(Path(EVENT_PATH).read_text(encoding="utf-8"))
    if EVENT_NAME == "pull_request":
        inspect_text("pull_request.title", event.get("pull_request", {}).get("title") or "")
        inspect_text("pull_request.body", event.get("pull_request", {}).get("body") or "")
    elif EVENT_NAME == "issues":
        inspect_text("issue.title", event.get("issue", {}).get("title") or "")
        inspect_text("issue.body", event.get("issue", {}).get("body") or "")
    elif EVENT_NAME == "discussion":
        inspect_text("discussion.title", event.get("discussion", {}).get("title") or "")
        inspect_text("discussion.body", event.get("discussion", {}).get("body") or "")
    elif EVENT_NAME in {"issue_comment", "pull_request_review_comment", "discussion_comment", "commit_comment"}:
        inspect_text("comment.body", event.get("comment", {}).get("body") or "")


def main() -> int:
    errors.clear()
    event = {}
    if EVENT_PATH and Path(EVENT_PATH).is_file():
        event = json.loads(Path(EVENT_PATH).read_text(encoding="utf-8"))

    inspect_pr_commits()
    inspect_push_commits(event)
    inspect_event()

    if errors:
        print("DO-statement style: FAIL")
        for error in errors:
            print(f" - {error}")
        return 1

    print("DO-statement style: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
