#!/usr/bin/env python3
"""Lint newly authored repository prose against the DO-first communication law."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

NEGATIVE_RE = re.compile(r"\b(?:do\s+not|don't|dont|never|cannot|can't|won't|wont|not|no)\b", re.I)
ALLOWLIST_RE = re.compile(r"\b(?:no-go|no-cost|no-op|no-fallback|not-found|not_found|not requested|not-requested|not configured|not-configured|not_applicable|not-applicable)\b", re.I)
FENCE_RE = re.compile(r"^ {0,3}(\x60{3,}|~{3,})")
HUNK_RE = re.compile(r"\+(\d+)(?:,(\d+))?")
URL_RE = re.compile(r"https?://\S+")
INLINE_CODE_RE = re.compile(r"\x60+[^\x60]*\x60+")

SKIP_PREFIXES = ("vendor/", "third_party/", "docs/proposals/legacy/", "docs/ops/corpus/", "tmp/", "sandbox/", "workspace/", "exchanges/")
PROSE_SUFFIXES = {".md", ".mdx", ".txt", ".rst"}
COMMENT_SUFFIXES = {".py", ".sh", ".bash", ".yml", ".yaml", ".toml", ".ini", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".c", ".h", ".sql"}
SUGGESTION = "Rewrite as an affirmative action, condition, or state; preserve exact technical meaning."


def run_git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def changed_paths(base):
    raw = subprocess.run(["git", "diff", "--name-only", "--diff-filter=ACMR", "-z", base + "...HEAD", "--"], check=True, capture_output=True).stdout.decode("utf-8", "surrogateescape")
    return [path for path in raw.split("\0") if path]


def changed_line_numbers(base, path):
    proc = subprocess.run(["git", "diff", "--unified=0", "--no-ext-diff", "--no-color", base + "...HEAD", "--", path], check=True, capture_output=True, text=True)
    added = set()
    current = 0
    for line in proc.stdout.splitlines():
        if line.startswith("@@"):
            match = HUNK_RE.search(line)
            current = int(match.group(1)) if match else 0
        elif line.startswith("+++") or line.startswith("---"):
            continue
        elif line.startswith("+"):
            if current:
                added.add(current)
                current += 1
        elif line.startswith(" ") and current:
            current += 1
    return added


def comment_body(line, suffix):
    stripped = line.lstrip()
    if suffix in PROSE_SUFFIXES or not suffix:
        return line
    if suffix in {".py", ".sh", ".bash", ".yml", ".yaml", ".toml", ".ini"}:
        return stripped[1:].lstrip() if stripped.startswith("#") else None
    if suffix == ".sql":
        return stripped[2:].lstrip() if stripped.startswith("--") else None
    if suffix in {".js", ".mjs", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".c", ".h"}:
        for prefix in ("///", "//! ", "//", "/*", "*"):
            if stripped.startswith(prefix):
                return stripped[len(prefix):].lstrip()
    return None


def excluded_lines(lines):
    excluded = set()
    fence = None
    for number, line in enumerate(lines, 1):
        match = FENCE_RE.match(line)
        if fence:
            excluded.add(number)
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            continue
        if match:
            excluded.add(number)
            fence = match.group(1)
            continue
        if re.match(r"^\s*>", line):
            excluded.add(number)
    return excluded


def scan_text(text, path, line_numbers=None):
    if path.startswith(SKIP_PREFIXES):
        return []
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    if lines and "LinguistProjection: generated" in lines[0]:
        return []
    excluded = excluded_lines(lines)
    suffix = Path(path).suffix.lower()
    selected = line_numbers if line_numbers is not None else set(range(1, len(lines) + 1))
    findings = []
    for number in sorted(selected):
        if number < 1 or number > len(lines) or number in excluded:
            continue
        body = comment_body(lines[number - 1], suffix)
        if body is None:
            continue
        body = URL_RE.sub(" ", body)
        body = INLINE_CODE_RE.sub(" ", body)
        body = ALLOWLIST_RE.sub(" ", body)
        for match in NEGATIVE_RE.finditer(body):
            findings.append({"path": path, "line": number, "phrase": match.group(0), "suggestion": SUGGESTION})
    return findings


def index_text(path):
    proc = subprocess.run(["git", "show", ":" + path], capture_output=True, check=False)
    if proc.returncode:
        return None
    return proc.stdout.decode("utf-8", "replace")


def lint_changes(base):
    findings = []
    checked_files = 0
    for path in changed_paths(base):
        suffix = Path(path).suffix.lower()
        if suffix not in PROSE_SUFFIXES | COMMENT_SUFFIXES:
            continue
        content = index_text(path)
        if content is None:
            continue
        checked_files += 1
        findings.extend(scan_text(content, path, changed_line_numbers(base, path)))
    commit_text = subprocess.run(["git", "log", "--format=%B", base + "..HEAD"], capture_output=True, check=False, text=True).stdout
    findings.extend(scan_text(commit_text, "<commit-messages>"))
    for env_name, label in (("SIGLARY_PR_TITLE", "<PR title>"), ("SIGLARY_PR_BODY", "<PR body>")):
        value = os.environ.get(env_name, "")
        if value:
            findings.extend(scan_text(value, label))
    return {"schema": "siglary-lint/v1", "checked_files": checked_files, "finding_count": len(findings), "findings": findings}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="base ref for changed-file scope")
    parser.add_argument("--json", action="store_true", help="emit machine-readable findings")
    args = parser.parse_args(argv)
    result = lint_changes(args.base)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        for finding in result["findings"]:
            print("{}:{}: avoidable negative phrase {!r}; {}".format(finding["path"], finding["line"], finding["phrase"], finding["suggestion"]))
        print("communication lint: {} file(s), {} finding(s)".format(result["checked_files"], result["finding_count"]))
    return 1 if result["finding_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
