#!/usr/bin/env python3
"""Fail when a workflow_run trigger omits the required workflows list.

GitHub treats that omission as an invalid workflow file and records a
zero-job failure. Runs 37085767517 and 37085844806 on n8n-she-bridge.yml
were that class. This check is stdlib-only so repo gate can run it.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def missing_workflow_run_workflows(text: str) -> list[str]:
    """Return human-readable findings for workflow_run blocks without workflows."""
    findings: list[str] = []
    in_on = False
    in_wr = False
    wr_indent = 0
    saw_workflows = False
    wr_line = 0

    def close_block(line_no: int) -> None:
        nonlocal in_wr, saw_workflows
        if in_wr and not saw_workflows:
            findings.append(
                f"workflow_run at line {wr_line} omits required workflows list "
                f"(closed at line {line_no})"
            )
        in_wr = False
        saw_workflows = False

    for line_no, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = _indent(raw)
        key = stripped.split(":", 1)[0]
        if indent == 0:
            if in_wr:
                close_block(line_no)
            in_on = key == "on"
            continue
        if not in_on:
            continue
        if key == "workflow_run":
            if in_wr:
                close_block(line_no)
            in_wr = True
            wr_indent = indent
            wr_line = line_no
            saw_workflows = False
            continue
        if in_wr and indent <= wr_indent:
            close_block(line_no)
            continue
        if in_wr and key == "workflows":
            saw_workflows = True
    if in_wr:
        close_block(len(text.splitlines()) + 1)
    return findings


def scan_workflows(root: Path) -> list[str]:
    findings: list[str] = []
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.is_dir():
        return [f"missing workflow directory: {workflow_dir}"]
    for path in sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        for finding in missing_workflow_run_workflows(text):
            findings.append(f"{path.as_posix()}: {finding}")
    return findings


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    findings = scan_workflows(root)
    if findings:
        print("workflow_run contract failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("workflow_run contract ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
