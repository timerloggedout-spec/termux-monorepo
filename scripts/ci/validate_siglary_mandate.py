#!/usr/bin/env python3
"""Validate the Siglary rule map and newly authored text on a repository diff."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANDATE = Path("docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md")
MATRICE = Path("docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md")
CLAUDE = Path("CLAUDE.md")
EXPECTED_RULE_IDS = [f"SG{i:03d}" for i in range(1, 9)]
CLAUDE_REFERENCES = (
    str(MANDATE),
    "docs/proposals/active/notation-sets/SIGLARY-STANDARD.md",
    str(MATRICE),
    "scripts/ci/validate_siglary_mandate.py",
)
CROSSWALK_TOKENS = (
    "∧", "∨", "¬", "⇒", "⇔", "∈", "∉", "∀", "∃", "∅", "≠", "≡",
    "≈", "≤", "≥", "∝", "⊢", "⊬", "⊩", "≟", "∎", "⤴", "↳", "⤵",
    "↻", "⊕", "⊗", "⋈", "⏸", "▶", "✓", "✗", "⧖", "⚡", "∆", "Δ",
    "§", "⌖", "⊘", "→", "~",
)
AVOID_RE = re.compile(r"\b(?:no|not|never|don['’]t)\b", re.IGNORECASE)
INLINE_CODE_RE = re.compile(r"(?<!`)`+[^`]*`+(?!`)")
LINK_DESTINATION_RE = re.compile(r"\]\([^)]*\)")
URL_RE = re.compile(r"\bhttps?://[^\s)>\]]+", re.IGNORECASE)
QUOTED_TEXT_RE = re.compile(r'"[^"\n]*"|“[^”\n]*”|‘[^’\n]*’|(?<!\w)\'[^\'\n]+\'(?!\w)')
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HUNK_RE = re.compile(r"^@@ .* \+(\d+)(?:,\d+)? @@")


class ValidationError(Exception):
    """A deterministic mapping or lint invariant failed."""


def _section(text: str, heading: str, next_heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        raise ValidationError(f"missing section: {heading}")
    end = text.find(next_heading, start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def rule_ids(text: str) -> list[str]:
    block = _section(text, "## SG rule registry and enforcement boundary", "### Automated coverage")
    return re.findall(r"(?m)^\|\s*(SG\d{3})\s*\|", block)


def crosswalk_tokens(text: str) -> set[str]:
    block = _section(text, "## 2026-11-25 — Siglary mandate crosswalk (candidate mappings)", "\n## ")
    spans = re.findall(r"`([^`]+)`", block)
    return {token for span in spans for token in span.split()}


def prose_payload(line: str) -> str:
    """Return authored prose with code spans and URL destinations masked."""
    line = URL_RE.sub(" ", line)
    line = LINK_DESTINATION_RE.sub("]", line)
    return INLINE_CODE_RE.sub(" ", line)


def avoid_matches(text: str) -> list[str]:
    """Find AVOID vocabulary outside literal, quoted, fenced, and quoted-block text."""
    findings: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker[0]
            elif marker[0] == fence:
                fence = None
            continue
        if fence is not None or line.lstrip().startswith(">"):
            continue
        payload = QUOTED_TEXT_RE.sub(" ", prose_payload(line))
        findings.extend(match.group(0) for match in AVOID_RE.finditer(payload))
    return findings


def markdown_added_prose(path: str, added_lines: set[int]) -> list[tuple[int, str]]:
    target = ROOT / path
    if not target.is_file():
        return []
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    findings: list[tuple[int, str]] = []
    fence: str | None = None
    in_html_comment = False
    suffix = target.suffix.lower()
    prose_suffixes = {".md", ".markdown", ".rst", ".txt"}
    comment_suffixes = {".py", ".sh", ".yml", ".yaml", ".toml", ".ini", ".js", ".ts"}

    for number, line in enumerate(lines, 1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker[0]
            elif marker[0] == fence:
                fence = None
            continue
        if number not in added_lines or fence is not None:
            if in_html_comment and "-->" in line:
                in_html_comment = False
            elif "<!--" in line and "-->" not in line:
                in_html_comment = True
            continue
        stripped = line.lstrip()
        if stripped.startswith(">"):
            continue
        if in_html_comment:
            if "-->" in line:
                in_html_comment = False
            continue
        if "<!--" in line:
            before, _, after = line.partition("<!--")
            if "-->" not in after:
                in_html_comment = True
            line = before + after.partition("-->")[2]
        if suffix in prose_suffixes:
            payload = prose_payload(line)
        elif suffix in comment_suffixes:
            if stripped.startswith("#"):
                payload = prose_payload(stripped[1:])
            elif stripped.startswith("//"):
                payload = prose_payload(stripped[2:])
            elif stripped.startswith(("/*", "*", "*/")):
                payload = prose_payload(stripped.lstrip("/* "))
            else:
                continue
        else:
            continue
        matches = avoid_matches(payload)
        findings.extend((number, token) for token in matches)
    return findings


def changed_markdown(base: str) -> dict[str, set[int]]:
    command = ["git", "diff", "--no-ext-diff", "--unified=0", base, "--"]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        detail = result.stderr.strip() or f"git diff exited {result.returncode}"
        raise ValidationError(f"cannot read diff against {base}: {detail}")
    additions: dict[str, set[int]] = {}
    current_path: str | None = None
    new_line = 0
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            current_path = line[6:]
            additions.setdefault(current_path, set())
        elif line.startswith("@@"):
            match = HUNK_RE.match(line)
            if match:
                new_line = int(match.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            if current_path is not None:
                additions[current_path].add(new_line)
            new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        elif line.startswith(" "):
            new_line += 1
    return {path: numbers for path, numbers in additions.items() if numbers}


def commit_text(base: str) -> str:
    result = subprocess.run(
        ["git", "log", f"{base}..HEAD", "--format=%B"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or f"git log exited {result.returncode}"
        raise ValidationError(f"cannot inspect commit messages against {base}: {detail}")
    return result.stdout


def event_text(path: str | None) -> str:
    if not path:
        return ""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    parts: list[str] = []
    for key in ("pull_request", "issue", "comment", "review"):
        value = data.get(key)
        if isinstance(value, dict):
            for field in ("title", "body"):
                item = value.get(field)
                if isinstance(item, str):
                    parts.append(item)
    return "\n".join(parts)


def validate_registry() -> list[str]:
    errors: list[str] = []
    mandate_text = (ROOT / MANDATE).read_text(encoding="utf-8")
    observed_ids = rule_ids(mandate_text)
    if observed_ids != EXPECTED_RULE_IDS:
        errors.append(f"SG registry IDs must occur once and in order: {observed_ids}")

    claude_text = (ROOT / CLAUDE).read_text(encoding="utf-8")
    for reference in CLAUDE_REFERENCES:
        if reference not in claude_text:
            errors.append(f"CLAUDE.md lacks canonical pointer: {reference}")
        if not (ROOT / reference).is_file():
            errors.append(f"canonical pointer target is missing: {reference}")
    if re.search(r"\bSG00[1-8]\b", claude_text):
        errors.append("CLAUDE.md duplicates rule IDs instead of routing to the registry")

    matrice_text = (ROOT / MATRICE).read_text(encoding="utf-8")
    observed_tokens = crosswalk_tokens(matrice_text)
    missing_tokens = [token for token in CROSSWALK_TOKENS if token not in observed_tokens]
    if missing_tokens:
        errors.append(f"Matrice crosswalk lacks supplied tokens: {', '.join(missing_tokens)}")
    crosswalk = _section(
        matrice_text,
        "## 2026-11-25 — Siglary mandate crosswalk (candidate mappings)",
        "\n## ",
    )
    if "Issued GLYPH meaning is dispatch" not in crosswalk:
        errors.append("Matrice crosswalk must preserve ⤴ as the issued dispatch GLYPH")
    if "Canonical change OPERATOR" not in crosswalk or "Candidate alias for `∆`" not in crosswalk:
        errors.append("Matrice crosswalk must preserve canonical ∆ and flag Δ alias review")
    return errors


def validate_new_text(base: str, event_file: str | None) -> list[str]:
    errors: list[str] = []
    for path, line_numbers in changed_markdown(base).items():
        for number, token in markdown_added_prose(path, line_numbers):
            errors.append(f"{path}:{number}: AVOID vocabulary match: {token!r}")

    for token in avoid_matches(commit_text(base)):
        errors.append(f"commit message: AVOID vocabulary match: {token!r}")
    if event_file:
        for token in avoid_matches(event_text(event_file)):
            errors.append(f"event title/body: AVOID vocabulary match: {token!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/master", help="diff base ref")
    parser.add_argument("--event-file", help="GitHub Actions event JSON path")
    args = parser.parse_args(argv)

    try:
        errors = validate_registry()
        errors.extend(validate_new_text(args.base, args.event_file))
    except (OSError, ValueError, ValidationError) as exc:
        errors = [str(exc)]

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        "PASS: SG001–SG008 registry, CLAUDE source map, Matrice crosswalk, "
        "and changed-text AVOID checks are consistent."
    )
    print(
        "Coverage: changed authored source and PR event text; semantic and live-chat "
        "judgments remain in their owning review lanes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
