#!/usr/bin/env python3
"""Review action-first wording without blocking hedged collaboration prose."""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path
from do_statement_policy import ACTION_VERBS, is_hedged_instruction, subject_action_verb

EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH", "")
EVENT_NAME = os.environ.get("GITHUB_EVENT_NAME", "")
BASE_REF = os.environ.get("GITHUB_BASE_REF", "")
STYLE_PATHS = [
    "AGENTS.md", "moniker.md", "CLAUDE.md", "GEMINI.md", "SKILLS.md",
    ".agents/skills", ".github/skills", ".github/workflows",
    "docs/ops", "docs/proposals",
]
errors: list[str] = []
reviews: list[str] = []

def inspect_text(label: str, value: str) -> None:
    for number, line in enumerate(value.splitlines(), 1):
        if is_hedged_instruction(line):
            reviews.append(f"{label}:{number}: consider a direct action form: {line.strip()}")

def inspect_git_range(base: str, head: str) -> None:
    diff = subprocess.run(
        ["git", "diff", "--unified=0", f"{base}...{head}", "--", *STYLE_PATHS],
        check=True, capture_output=True, text=True,
    ).stdout
    current_path = "changed-file"
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_path = line[6:]
        elif line.startswith("+") and not line.startswith("+++") and is_hedged_instruction(line[1:]):
            reviews.append(f"{current_path}: consider a direct action form: {line[1:].strip()}")
    subjects = subprocess.run(
        ["git", "log", "--no-merges", f"{base}..{head}", "--format=%s"],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    bodies = subprocess.run(
        ["git", "log", "--no-merges", f"{base}..{head}", "--format=%b"],
        check=True, capture_output=True, text=True,
    ).stdout
    inspect_text("commit.body", bodies)
    for subject in subjects:
        if subject_action_verb(subject) not in ACTION_VERBS:
            errors.append(f"commit subject requires an imperative action verb after its scope: {subject}")

def inspect_pr_commits() -> None:
    if EVENT_NAME == "pull_request" and BASE_REF:
        subprocess.run(["git", "fetch", "origin", BASE_REF], check=True)
        inspect_git_range(f"origin/{BASE_REF}", "HEAD")

def inspect_push_commits(event: dict) -> None:
    if EVENT_NAME == "push":
        before = event.get("before") or ""
        after = event.get("after") or "HEAD"
        if before and set(before) != {"0"}:
            inspect_git_range(before, after)

def inspect_event() -> None:
    if not EVENT_PATH or not Path(EVENT_PATH).is_file():
        return
    event = json.loads(Path(EVENT_PATH).read_text(encoding="utf-8"))
    if EVENT_NAME == "pull_request":
        pull = event.get("pull_request", {})
        inspect_text("pull_request.title", pull.get("title") or "")
        inspect_text("pull_request.body", pull.get("body") or "")
    elif EVENT_NAME == "issues":
        issue = event.get("issue", {})
        inspect_text("issue.title", issue.get("title") or "")
        inspect_text("issue.body", issue.get("body") or "")
    elif EVENT_NAME == "discussion":
        discussion = event.get("discussion", {})
        inspect_text("discussion.title", discussion.get("title") or "")
        inspect_text("discussion.body", discussion.get("body") or "")
    elif EVENT_NAME in {"issue_comment", "pull_request_review_comment", "discussion_comment", "commit_comment"}:
        inspect_text("comment.body", event.get("comment", {}).get("body") or "")
    elif EVENT_NAME == "pull_request_review":
        inspect_text("pull_request_review.body", event.get("review", {}).get("body") or "")
    elif EVENT_NAME == "release":
        release = event.get("release", {})
        inspect_text("release.name", release.get("name") or "")
        inspect_text("release.body", release.get("body") or "")

event = {}
if EVENT_PATH and Path(EVENT_PATH).is_file():
    event = json.loads(Path(EVENT_PATH).read_text(encoding="utf-8"))
inspect_pr_commits()
inspect_push_commits(event)
inspect_event()
for review in reviews:
    print(f"REVIEW {review}")
if errors:
    print("DO-statement style: FAIL")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)
print("DO-statement style: PASS" if not reviews else f"DO-statement style: PASS WITH {len(reviews)} REVIEW finding(s)")
