#!/usr/bin/env python3
"""Enforce action-first collaboration language on newly authored GitHub surfaces."""
from __future__ import annotations
import json
import os
import subprocess
from pathlib import Path
from do_statement_policy import is_hedged_instruction, is_imperative_subject

EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH", "")
EVENT_NAME = os.environ.get("GITHUB_EVENT_NAME", "")
BASE_REF = os.environ.get("GITHUB_BASE_REF", "")
# Compatibility pins: "guard" and "export" remain registered in the shared action vocabulary.
STYLE_PATHS = [
    "AGENTS.md", "moniker.md", "CLAUDE.md", "CLAUDE.hum.md", "GEMINI.md", "SKILLS.md",
    ".agents/skills", ".github/skills", ".github/workflows", "docs/icm", "docs/ops", "docs/proposals",
]
errors: list[str] = []

def inspect_text(label: str, value: str) -> None:
    for number, line in enumerate(value.splitlines(), 1):
        if is_hedged_instruction(line):
            errors.append(f"{label}:{number}: replace hedged framing with the direct action")

def run_git(args: list[str]) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout

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
    diff = run_git(["git", "diff", "--unified=0", f"{base}...{head}", "--", *STYLE_PATHS])
    current_path = "changed-file"
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            added = line[1:]
            if is_hedged_instruction(added):
                errors.append(f"{current_path}: replace hedged framing with the direct action: {added.strip()}")
    inspect_text("commit.body", commit_bodies(base, head))
    for subject in commit_subjects(base, head):
        if not is_imperative_subject(subject):
            errors.append(f"commit subject requires an imperative action verb after its scope: {subject}")

def inspect_pr_commits() -> None:
    if EVENT_NAME == "pull_request" and BASE_REF:
        subprocess.run(["git", "fetch", "origin", BASE_REF], check=True)
        inspect_git_range(f"origin/{BASE_REF}", "HEAD")

def inspect_push_commits(event: dict) -> None:
    if EVENT_NAME != "push":
        return
    before = event.get("before") or ""
    after = event.get("after") or "HEAD"
    if before and set(before) != {"0"}:
        inspect_git_range(before, after)

def inspect_event(event: dict) -> None:
    if EVENT_NAME == "pull_request":
        item = event.get("pull_request", {})
        inspect_text("pull_request.title", item.get("title") or "")
        inspect_text("pull_request.body", item.get("body") or "")
    elif EVENT_NAME == "issues":
        item = event.get("issue", {})
        inspect_text("issue.title", item.get("title") or "")
        inspect_text("issue.body", item.get("body") or "")
    elif EVENT_NAME == "discussion":
        item = event.get("discussion", {})
        inspect_text("discussion.title", item.get("title") or "")
        inspect_text("discussion.body", item.get("body") or "")
    elif EVENT_NAME in {"issue_comment", "pull_request_review_comment", "discussion_comment", "commit_comment"}:
        inspect_text(f"{EVENT_NAME}.body", event.get("comment", {}).get("body") or "")
    elif EVENT_NAME == "pull_request_review":
        inspect_text("pull_request_review.body", event.get("review", {}).get("body") or "")
    elif EVENT_NAME == "release":
        item = event.get("release", {})
        inspect_text("release.name", item.get("name") or "")
        inspect_text("release.body", item.get("body") or "")

def main() -> int:
    event: dict = {}
    if EVENT_PATH and Path(EVENT_PATH).is_file():
        event = json.loads(Path(EVENT_PATH).read_text(encoding="utf-8"))
    inspect_pr_commits()
    inspect_push_commits(event)
    inspect_event(event)
    if errors:
        print("DO Statement gate: FAIL")
        for error in errors:
            print(f" - {error}")
        return 1
    print("DO Statement gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
