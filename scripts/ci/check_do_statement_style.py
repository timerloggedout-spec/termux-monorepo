#!/usr/bin/env python3
"""Check action-first wording in newly authored repository instructions and comments."""
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
    "add", "align", "apply", "audit", "build", "bump", "check", "close",
    "compare", "create", "document", "enforce", "expand", "fix", "gate",
    "include", "keep", "measure", "migrate", "move", "open", "preserve",
    "publish", "record", "refine", "register", "remove", "rename", "repair",
    "replace", "require", "restore", "route", "run", "set", "split", "sync",
    "test", "update", "use", "validate", "verify", "wire",
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

def inspect_pr_commits() -> None:
    if EVENT_NAME != "pull_request" or not BASE_REF:
        return
    subprocess.run(["git", "fetch", "origin", BASE_REF], check=True)
    diff = subprocess.run(
        ["git", "diff", "--unified=0", f"origin/{BASE_REF}...HEAD", "--", *STYLE_PATHS],
        check=True, capture_output=True, text=True,
    ).stdout
    current_path = "changed-file"
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            added = line[1:]
            if NEGATIVE_FIRST.match(added):
                errors.append(f"{current_path}: lead with the intended DO action: {added.strip()}")

    subjects = subprocess.run(
        ["git", "log", f"origin/{BASE_REF}..HEAD", "--format=%s"],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    for subject in subjects:
        verb = subject.rsplit(": ", 1)[-1].split(maxsplit=1)[0].lower() if ": " in subject else subject.split(maxsplit=1)[0].lower()
        if verb not in IMPERATIVE:
            errors.append(f"commit subject requires an imperative action verb after its scope: {subject}")

def inspect_event() -> None:
    if not EVENT_PATH or not Path(EVENT_PATH).is_file():
        return
    event = json.loads(Path(EVENT_PATH).read_text(encoding="utf-8"))
    if EVENT_NAME == "pull_request":
        inspect_text("pull_request.body", event.get("pull_request", {}).get("body") or "")
    elif EVENT_NAME == "issues":
        inspect_text("issue.title", event.get("issue", {}).get("title") or "")
        inspect_text("issue.body", event.get("issue", {}).get("body") or "")
    elif EVENT_NAME in {"issue_comment", "pull_request_review_comment", "commit_comment"}:
        inspect_text("comment.body", event.get("comment", {}).get("body") or "")

inspect_pr_commits()
inspect_event()

if errors:
    print("DO-statement style: FAIL")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print("DO-statement style: PASS")
