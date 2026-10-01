#!/usr/bin/env python3
"""
repo_gate.py — cheap, device-friendly hygiene gate for termux-monorepo.

ArchW1z invariant gate (P0 spine).

Design constraints (from PR #2 discussion: "Limit local, Android Termux, device, resources, usage."):

  * stdlib only, no pip installs, no network, no toolchains
  * no Rust/cargo build, no Chromium, no adb, no termux-api
  * runs identically on-device (`python3 scripts/ci/repo_gate.py`) and in CI
  * reads the git *index*, not the working tree, so it works in a sparse or
    partially materialised checkout and never follows a dangling symlink

Two kinds of check:

  HARD   — always fail. Scoped to files changed against the base ref, so master's
           pre-existing breakage never blocks an unrelated PR.
  RATCHET — repo-wide debt counters compared against scripts/ci/baseline.json.
           Fail if a counter goes UP. Print a nudge if it goes DOWN so the
           baseline can be lowered. Debt can only shrink.

One HARD check deserves its own note: `check_yaml_structure`. A workflow file with
invalid YAML never schedules a job, so it fails *silently* — the run is red with no
step output, and every tool that reads the file leniently (regex parsing, docs
catalogues) keeps reporting it as healthy. A control-plane schema is worse: nothing
parses it at all, so the breakage is invisible until a consumer adds a parser. Five
workflow files and one schema in this repository reached that state.
`yaml_structure_faults()` is a stdlib-only structural check for the failure classes
actually observed:

  * a root-level (column 0) line that is not a mapping key — the signature of a
    heredoc or quoted string body whose continuation lines lost their indentation
    while the surrounding `run: |` block scalar stayed behind;
  * a mapping value starting with `!(` — YAML reads `!` as a tag token, so an
    unquoted `if: !(...)` is a scanner error, not a boolean expression;
  * a block scalar whose first body line is not indented past its header;
  * a plain scalar value containing `: `, which the scanner reads as a nested
    mapping ("mapping values are not allowed here");
  * a literal `\\n` / `\\r` / `\\t` escape in an unquoted scalar — a JSON body
    pasted into YAML, where the author meant a newline and YAML keeps the two
    characters. `\\n` is only an escape inside a double-quoted scalar, so in an
    unquoted position it silently swallows the rest of the line and the next key
    it was carrying. Quoted scalars are exempt in both styles: quoting is how an
    author says "I mean the backslash".

The same check covers the three surfaces where a silent parse failure does real
damage: `.github/workflows/*.yml`, the control-plane schemas in `docs/schemas/`,
and the research lane registry in `docs/research/` (a live dependency of
`config/foresight_digest_sources.json`).

It is validated to agree with a full YAML parse on every file in its scope across
the repository (see tests/test_repo_gate_workflow_yaml.py). It is not a YAML parser
and does not replace the advisory actionlint lane; it exists so the specific
silent-failure classes above cannot grow again.

Usage:
  python3 scripts/ci/repo_gate.py                    # full gate
  python3 scripts/ci/repo_gate.py --base origin/master
  python3 scripts/ci/repo_gate.py --ratchet-only
  python3 scripts/ci/repo_gate.py --write-baseline   # re-record counters
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = Path(__file__).resolve().parent / "baseline.json"

# Scratch/among-the-weeds trees that hold captured agent output rather than
# source we maintain. Syntax checks skip these; the ratchet still counts them.
SCRATCH_PREFIXES = (
    "termux-multi-agent/workspace/",
    "workspace/llm_map/",
    "workspace/maxc/",
    "patches_backup_20260718/",
    "sandbox/",
    "tmp/",
    "exchanges/",
)

DEVICE_PATH_PREFIXES = (
    "/data/data/com.termux/",
    "/storage/emulated/",
    "/sdcard/",
)

SESSION_ARTIFACT_RE = re.compile(
    r"(^|/)(\.deepcli|\.pi|\.synthegration|\.cedar|\.approxination)/|(^|/)session_store/"
)
BACKUP_RE = re.compile(r"\.bak(\.|$)|\.backup(\.|$)|\.old$|~$")

# A committed Chromium profile is a credential store, not test data. The Cookies
# DB holds live session tokens; on Termux/Linux there is usually no keyring, so
# Chromium falls back to a hardcoded OSCrypt password and "encrypted_value" is
# recoverable by anyone who can read the file. See docs/CREDENTIAL-EXPOSURE.md.
BROWSER_PROFILE_RE = re.compile(
    r"(^|/)(browser-data|browser-profile|chrome-profile|chromium-profile|"
    r"puppeteer-data|playwright-data|user-data-dir)[^/]*/"
)
BROWSER_CREDENTIAL_RE = re.compile(
    r"(^|/)("
    r"Cookies|Login Data|Login Data For Account|Web Data|Account Web Data|"
    r"Local State|Trust Tokens|Safe Browsing Cookies|"
    r"Session Storage|Local Storage|Sessions|IndexedDB"
    r")($|-journal$|-wal$|/)"
)

# Deliberately narrow: shaped, high-confidence key material only. Anything
# fuzzier produces noise on a repo that legitimately talks *about* API keys.
SECRET_PATTERNS = (
    ("openai/anthropic-style key", re.compile(r"\b(?:sk|rk)-[A-Za-z0-9_\-]{32,}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("aws access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("slack token", re.compile(r"\bxox[abprs]-[0-9A-Za-z\-]{10,}\b")),
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
)

# --------------------------------------------------------------------------- #
# Workflow YAML structure (see the module docstring)
# --------------------------------------------------------------------------- #

# YAML surfaces where a parse failure is silent and high-impact: a workflow never
# schedules a job, a control-plane schema is read by policy gates and doc
# generators that do not parse it, and docs/research/RESEARCH-LANES.yaml is the
# live lane registry for config/foresight_digest_sources.json.
CONTROL_PLANE_YAML_RE = re.compile(
    r"^(?:\.github/workflows/[^/]+\.ya?ml"
    r"|docs/schemas/[^/]+\.ya?ml"
    r"|docs/research/[^/]+\.ya?ml)$"
)

# A block scalar header: an optional `- ` sequence marker, a mapping key, and a
# `|`/`>` value with optional chomping/indent indicators and a trailing comment.
# Deliberately keyed on a real mapping key so a shell pipeline that happens to end
# a line with `|` is not mistaken for a block scalar.
BLOCK_SCALAR_HEADER_RE = re.compile(
    r"^(?P<indent>[ ]*)(?:- +)?[A-Za-z_][A-Za-z0-9_.\-]* *: *[|>][-+0-9]* *(?:#.*)?$"
)
# A line that is legal at the document root: a document marker or a mapping key.
# `(?:\s|$)` rather than `\b`: `-` and `.` are non-word characters, so a trailing
# word boundary can never match after `---` / `...`.
ROOT_MARKER_RE = re.compile(r"^(?:---|\.\.\.|%YAML|%TAG)(?:\s|$)")
# Leading whitespace, tabs included, so indentation faults are measured the way the
# YAML scanner measures them.
INDENT_RE = re.compile(r"^[ \t]*")
ROOT_MAPPING_KEY_RE = re.compile(r"^[^\s#][^:]*:")
# `key: !(...)` — `!` starts a tag; `(` is not a legal shorthand tag character.
UNQUOTED_TAG_VALUE_RE = re.compile(r"^[ ]*(?:- +)?[A-Za-z_][A-Za-z0-9_.\-]* *: +!\(")
# `key: value` whose plain (unquoted, non-flow, non-block) value itself contains a
# `: ` — the scanner reads that as a nested mapping and raises
# "mapping values are not allowed here". Shell/JS code inside a block scalar is
# full of these, so the rule is only applied outside a block scalar body.
PLAIN_VALUE_COLON_RE = re.compile(
    r"^(?P<indent>[ ]*)(?:- +)?[A-Za-z_][A-Za-z0-9_.\-]* *: +"
    r"(?P<value>[^\s'\"|>\[\]{#*&!%@`].*)$"
)
TRAILING_COMMENT_RE = re.compile(r"\s+#.*$")
# A YAML escape (`\n`, `\r`, `\t`) sitting in an unquoted scalar. Double-quoted is
# the only style where those are real escapes; unquoted, they are two literal
# characters, which is what a JSON body pasted into YAML looks like. YAML does not
# reject it — the escape just eats the rest of the line, so
# `inputs: [a, b]\n    contributors: [c]` carries the next key inside the value, or
# fails to parse further down.
LITERAL_ESCAPE_RE = re.compile(r"\\[nrt]")


def literal_escape_fault(line: str) -> str | None:
    """Return the offending `\\x` escape in `line`, or None.

    Scans left to right tracking quoted-scalar state, so the rule fires only where
    the escape is unquoted and therefore unintended: inside either quote style the
    author has explicitly asked for the backslash (as a real escape in `"..."`, as
    a literal character in `'...'`), and an escape inside a trailing comment is not
    content at all.

    A backslash that is itself preceded by an odd run of backslashes does not
    introduce anything, and is skipped — `C:\\\\Users\\\\runner` is a path, not a `\\r`
    escape. The same parity test every lexer uses.

    Finally the escape has to sit where a swallowed newline would: at the end of
    the line, in front of whitespace, or directly after a flow/sequence delimiter
    (`]`, `}`, `,`) — the JSON-paste shape. A path like `C:\\temp` or a prose value
    like `line one\\nline two` is left alone: a Windows path is not this class's
    business, and a plain scalar holding a stray backslash still parses, so it is
    not structural.
    """
    index = 0
    in_single = in_double = False
    while index < len(line):
        char = line[index]
        if in_double:
            if char == "\\":
                index += 2
                continue
            if char == '"':
                in_double = False
        elif in_single:
            if char == "'":
                if line[index + 1 : index + 2] == "'":
                    index += 2
                    continue
                in_single = False
        elif char == '"':
            in_double = True
        elif char == "'":
            in_single = True
        elif char == "#" and (index == 0 or line[index - 1] in " \t"):
            break
        elif char == "\\" and LITERAL_ESCAPE_RE.match(line, index):
            preceding = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                preceding += 1
                cursor -= 1
            after = line[index + 2 : index + 3]
            before = line[index - 1 : index]
            if preceding % 2 == 0 and (
                after == "" or after.isspace() or before in ("]", "}", ",")
            ):
                return line[index : index + 2]
        index += 1
    return None


def indent_of(line: str) -> tuple[int, str]:
    """Return `(width, text)` of a line's leading whitespace, tabs included."""
    whitespace = INDENT_RE.match(line).group(0)
    return len(whitespace), whitespace


def block_scalar_body_lines(lines: list[str]) -> set[int]:
    """Line indices (0-based) that fall inside a block scalar body.

    A block scalar runs until the first non-blank line indented no further than its
    header. That boundary is what makes the root-level rule below work: a heredoc
    body that has lost its indentation *terminates* the surrounding block scalar, so
    the offending lines are reported rather than skipped as body content.
    """
    inside: set[int] = set()
    index = 0
    while index < len(lines):
        header = BLOCK_SCALAR_HEADER_RE.match(lines[index])
        if header is None:
            index += 1
            continue
        header_indent = len(header.group("indent"))
        index += 1
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                inside.add(index)
                index += 1
                continue
            if indent_of(line)[0] <= header_indent:
                break
            inside.add(index)
            index += 1
    return inside


def yaml_structure_faults(text: str) -> list[str]:
    """Return structural YAML faults, as `line N: reason` strings.

    Only high-precision rules for the observed silent-failure classes; see the
    module docstring. An empty list means "no fault found", not "valid YAML" — the
    authoritative lint remains the advisory actionlint lane.
    """
    faults: list[str] = []
    lines = text.split("\n")
    inside_block = block_scalar_body_lines(lines)

    for index, line in enumerate(lines):
        number = index + 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent, indent_text = indent_of(line)
        if (
            indent == 0
            and not ROOT_MARKER_RE.match(line)
            and not ROOT_MAPPING_KEY_RE.match(line)
        ):
            faults.append(
                f"line {number}: root-level line is neither a mapping key nor a document "
                f"marker (an escaped string/heredoc body?): {line.strip()[:60]!r}"
            )
            continue
        if index in inside_block:
            continue
        if "\t" in indent_text:
            faults.append(f"line {number}: tab used for indentation (YAML forbids tabs)")
            continue
        escape = literal_escape_fault(line)
        if escape is not None:
            faults.append(
                f"line {number}: literal '\\{escape[1]}' escape in an unquoted scalar — "
                f"YAML keeps the two characters, so this line no longer means what it says "
                f"(a JSON body pasted into YAML?): {line.strip()[:60]!r}"
            )
            continue
        if UNQUOTED_TAG_VALUE_RE.match(line):
            faults.append(
                f"line {number}: value starts with '!(', which YAML scans as a tag rather "
                f"than a string — quote the whole expression: {line.strip()[:60]!r}"
            )
            continue
        match = PLAIN_VALUE_COLON_RE.match(line)
        if match:
            value = TRAILING_COMMENT_RE.sub("", match.group("value"))
            if ": " in value or value.endswith(":"):
                faults.append(
                    f"line {number}: plain scalar value contains ': ', which YAML scans as "
                    f"a nested mapping — quote the value or use a block scalar: "
                    f"{value.strip()[:60]!r}"
                )

    for index, line in enumerate(lines):
        header = BLOCK_SCALAR_HEADER_RE.match(line)
        if not header:
            continue
        header_indent = len(header.group("indent"))
        body = index + 1
        while body < len(lines) and not lines[body].strip():
            body += 1
        if body >= len(lines):
            continue
        body_line = lines[body]
        body_indent = len(body_line) - len(body_line.lstrip(" "))
        if body_indent <= header_indent:
            faults.append(
                f"line {body + 1}: block scalar body indented {body_indent}, not past its "
                f"header on line {index + 1} at {header_indent}: {body_line.strip()[:60]!r}"
            )

    return faults


def check_yaml_structure(report: Report, paths: list[str], index: dict[str, IndexEntry]) -> int:
    checked = 0
    for path in paths:
        if not CONTROL_PLANE_YAML_RE.match(path):
            continue
        entry = index.get(path)
        if entry is None or entry.is_symlink or entry.is_gitlink:
            continue
        checked += 1
        text = blob(entry.sha).decode("utf-8", "replace")
        for fault in yaml_structure_faults(text):
            report.fail(
                "yaml-structure",
                f"{path}: {fault} — nothing will run or read this file until it parses",
            )
    return checked

BOLD, RED, YELLOW, GREEN, DIM, RESET = (
    ("\033[1m", "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m")
    if sys.stdout.isatty()
    else ("", "", "", "", "", "")
)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def git_ok(*args: str) -> bool:
    return (
        subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
        ).returncode
        == 0
    )


class IndexEntry:
    __slots__ = ("mode", "path", "sha")

    def __init__(self, mode: str, sha: str, path: str) -> None:
        self.mode = mode
        self.sha = sha
        self.path = path

    @property
    def is_symlink(self) -> bool:
        return self.mode == "120000"

    @property
    def is_gitlink(self) -> bool:
        """A submodule entry points to a commit, not a blob in this repository."""
        return self.mode == "160000"


def read_index() -> list[IndexEntry]:
    """Parse `git ls-files -s -z`. NUL-delimited: 452 tracked paths contain spaces."""
    raw = subprocess.run(
        ["git", "ls-files", "-s", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8", "surrogateescape")
    entries: list[IndexEntry] = []
    for record in raw.split("\0"):
        if not record:
            continue
        meta, _, path = record.partition("\t")
        parts = meta.split()
        if len(parts) < 3 or not path:
            continue
        entries.append(IndexEntry(parts[0], parts[1], path))
    return entries


def blob(sha: str) -> bytes:
    return subprocess.run(
        ["git", "cat-file", "blob", sha],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout


def symlink_target(entry: IndexEntry) -> str:
    """Symlink target lives in the blob — never touches the filesystem."""
    return blob(entry.sha).decode("utf-8", "replace").strip()


def resolve_base(requested: str | None) -> str | None:
    candidates = [requested] if requested else []
    candidates += [
        os.environ.get("GATE_BASE"),
        "origin/master",
        "master",
        "origin/HEAD",
    ]
    for ref in candidates:
        if ref and git_ok("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"):
            return ref
    return None


def changed_paths(base: str) -> list[str]:
    merge_base = base
    try:
        merge_base = git("merge-base", base, "HEAD").strip() or base
    except subprocess.CalledProcessError:
        pass
    raw = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "-z", merge_base, "--"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8", "surrogateescape")
    return [p for p in raw.split("\0") if p]


def is_scratch(path: str) -> bool:
    return path.startswith(SCRATCH_PREFIXES)


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.notes: list[str] = []

    def fail(self, check: str, detail: str) -> None:
        self.failures.append(f"{check}: {detail}")

    def note(self, detail: str) -> None:
        self.notes.append(detail)


# --------------------------------------------------------------------------- #
# HARD checks (changed files only)
# --------------------------------------------------------------------------- #


def check_python_syntax(report: Report, paths: list[str], index: dict[str, IndexEntry]) -> int:
    checked = 0
    for path in paths:
        if not path.endswith(".py") or is_scratch(path):
            continue
        entry = index.get(path)
        if entry is None or entry.is_symlink or entry.is_gitlink:
            continue
        checked += 1
        source = blob(entry.sha)
        try:
            ast.parse(source, filename=path)
        except SyntaxError as exc:
            report.fail("python-syntax", f"{path}:{exc.lineno}: {exc.msg}")
        except ValueError as exc:  # e.g. embedded NUL
            report.fail("python-syntax", f"{path}: {exc}")
    return checked


def check_shell_syntax(report: Report, paths: list[str], index: dict[str, IndexEntry]) -> int:
    bash = shutil.which("bash")
    if bash is None:
        report.note("bash not found — shell syntax check skipped")
        return 0
    checked = 0
    for path in paths:
        if not path.endswith((".sh", ".bash")) or is_scratch(path):
            continue
        entry = index.get(path)
        if entry is None or entry.is_symlink or entry.is_gitlink:
            continue
        checked += 1
        proc = subprocess.run(
            [bash, "-n", "-"], input=blob(entry.sha), capture_output=True, check=False
        )
        if proc.returncode != 0:
            first = (
                proc.stderr.decode("utf-8", "replace").strip().splitlines() or ["syntax error"]
            )[0]
            report.fail("shell-syntax", f"{path}: {first}")
    return checked


def check_json_parses(report: Report, paths: list[str], index: dict[str, IndexEntry]) -> int:
    checked = 0
    for path in paths:
        if not path.endswith(".json") or is_scratch(path):
            continue
        entry = index.get(path)
        if entry is None or entry.is_symlink or entry.is_gitlink:
            continue
        raw = blob(entry.sha)
        if not raw.strip():
            continue
        checked += 1
        try:
            json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            report.fail("json-parse", f"{path}: {exc}")
    return checked


def check_new_symlinks(report: Report, paths: list[str], index: dict[str, IndexEntry]) -> int:
    checked = 0
    for path in paths:
        entry = index.get(path)
        if entry is None or not entry.is_symlink:
            continue
        checked += 1
        target = symlink_target(entry)
        if target.startswith(DEVICE_PATH_PREFIXES):
            report.fail(
                "portable-symlink",
                f"{path} -> {target} (device-absolute; see docs/PORTABILITY.md)",
            )
        elif target.startswith("/"):
            report.fail(
                "portable-symlink",
                f"{path} -> {target} (absolute target; use a relative link or vendor the file)",
            )
    return checked


def check_new_debt_paths(report: Report, paths: list[str]) -> None:
    for path in paths:
        if BROWSER_CREDENTIAL_RE.search(path) and BROWSER_PROFILE_RE.search(path):
            report.fail(
                "no-browser-credential-stores",
                f"{path} — browser profile credential store. Rotate the affected "
                f"session and keep the profile dir untracked "
                f"(see docs/CREDENTIAL-EXPOSURE.md)",
            )
        elif BROWSER_PROFILE_RE.search(path):
            report.fail(
                "no-browser-profiles",
                f"{path} — browser profile data is runtime state, not source; "
                f"point the automation at a gitignored dir instead",
            )
        if SESSION_ARTIFACT_RE.search(path):
            report.fail(
                "no-session-artifacts",
                f"{path} — agent session stores must stay untracked (see SECURITY.md)",
            )
        if BACKUP_RE.search(Path(path).name):
            report.fail(
                "no-committed-backups",
                f"{path} — use git history instead of .bak/.old copies",
            )
        if "$(" in path or "`" in path:
            report.fail(
                "no-unexpanded-shell-in-path",
                f"{path} — filename contains an unexpanded command substitution",
            )


def check_secrets(report: Report, paths: list[str], index: dict[str, IndexEntry]) -> int:
    checked = 0
    for path in paths:
        entry = index.get(path)
        if entry is None or entry.is_symlink or entry.is_gitlink:
            continue
        if path.startswith("scripts/ci/"):  # the patterns themselves live here
            continue
        raw = blob(entry.sha)
        if len(raw) > 2_000_000 or b"\0" in raw[:8192]:
            continue
        text = raw.decode("utf-8", "replace")
        checked += 1
        for label, pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                report.fail(
                    "no-secrets",
                    f"{path}:{line}: possible {label} — rotate it, then remove it from the diff",
                )
                break
    return checked


# --------------------------------------------------------------------------- #
# RATCHET counters (repo-wide)
# --------------------------------------------------------------------------- #


def measure(index: list[IndexEntry]) -> dict[str, int]:
    device_symlinks = 0
    absolute_symlinks = 0
    tracked_session_artifacts = 0
    tracked_backup_files = 0
    paths_with_spaces = 0
    tracked_browser_profile_files = 0
    tracked_browser_credential_stores = 0
    invalid_control_plane_yaml = 0

    blob_cache: dict[str, str] = {}

    for entry in index:
        path = entry.path

        if " " in path:
            paths_with_spaces += 1

        if CONTROL_PLANE_YAML_RE.match(path) and not entry.is_symlink and not entry.is_gitlink:
            text = blob(entry.sha).decode("utf-8", "replace")
            if yaml_structure_faults(text):
                invalid_control_plane_yaml += 1

        if entry.is_symlink:
            target = blob_cache.get(entry.sha)
            if target is None:
                target = symlink_target(entry)
                blob_cache[entry.sha] = target
            if target.startswith(DEVICE_PATH_PREFIXES):
                device_symlinks += 1
            elif target.startswith("/"):
                absolute_symlinks += 1

        if SESSION_ARTIFACT_RE.search(path):
            tracked_session_artifacts += 1

        filename = path.rsplit("/", 1)[-1]
        if BACKUP_RE.search(filename):
            tracked_backup_files += 1

        if BROWSER_PROFILE_RE.search(path):
            tracked_browser_profile_files += 1
            if BROWSER_CREDENTIAL_RE.search(path):
                tracked_browser_credential_stores += 1

    return {
        "device_absolute_symlinks": device_symlinks,
        "other_absolute_symlinks": absolute_symlinks,
        "tracked_session_artifacts": tracked_session_artifacts,
        "tracked_backup_files": tracked_backup_files,
        "paths_with_spaces": paths_with_spaces,
        "tracked_browser_profile_files": tracked_browser_profile_files,
        "tracked_browser_credential_stores": tracked_browser_credential_stores,
        "invalid_control_plane_yaml": invalid_control_plane_yaml,
    }


def check_ratchet(report: Report, index: list[IndexEntry]) -> dict[str, int]:
    current = measure(index)
    if not BASELINE_PATH.exists():
        report.note(f"no baseline at {BASELINE_PATH.name}; run --write-baseline")
        return current
    baseline = json.loads(BASELINE_PATH.read_text()).get("counters", {})
    for key, value in sorted(current.items()):
        limit = baseline.get(key)
        if limit is None:
            report.note(f"ratchet: new counter {key}={value} (add it to the baseline)")
        elif value > limit:
            report.fail(
                "ratchet",
                f"{key} rose {limit} -> {value}; this PR adds debt the repo is trying to shed",
            )
        elif value < limit:
            report.note(
                f"ratchet: {key} improved {limit} -> {value} — lower the baseline "
                f"(`python3 scripts/ci/repo_gate.py --write-baseline`)"
            )
    return current


def write_baseline(counters: dict[str, int]) -> None:
    BASELINE_PATH.write_text(
        json.dumps(
            {
                "_comment": (
                    "Debt counters for scripts/ci/repo_gate.py. These may only go "
                    "down. Regenerate with: python3 scripts/ci/repo_gate.py "
                    "--write-baseline"
                ),
                "counters": dict(sorted(counters.items())),
            },
            indent=2,
        )
        + "\n"
    )


# --------------------------------------------------------------------------- #


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="base ref for the changed-file scope")
    parser.add_argument("--ratchet-only", action="store_true")
    parser.add_argument("--hard-only", action="store_true")
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args()

    index = read_index()
    by_path = {e.path: e for e in index}
    report = Report()

    if args.write_baseline:
        write_baseline(measure(index))
        print(f"{GREEN}wrote{RESET} {BASELINE_PATH.relative_to(REPO_ROOT)}")
        return 0

    print(f"{BOLD}repo gate{RESET} — {len(index)} tracked paths")

    if not args.ratchet_only:
        base = resolve_base(args.base)
        if base is None:
            print(f"{YELLOW}no base ref resolved; hard checks skipped{RESET}")
        else:
            paths = changed_paths(base)
            print(f"  base {DIM}{base}{RESET} — {len(paths)} changed path(s)")
            counts = {
                "py": check_python_syntax(report, paths, by_path),
                "sh": check_shell_syntax(report, paths, by_path),
                "json": check_json_parses(report, paths, by_path),
                "yaml-structure": check_yaml_structure(report, paths, by_path),
                "symlinks": check_new_symlinks(report, paths, by_path),
                "scanned": check_secrets(report, paths, by_path),
            }
            check_new_debt_paths(report, paths)
            print(
                "  hard checks: "
                + ", ".join(f"{k}={v}" for k, v in counts.items())
            )

    if not args.hard_only:
        current = check_ratchet(report, index)
        print("  " + f"{DIM}counters{RESET} " + ", ".join(
            f"{k}={v}" for k, v in sorted(current.items())
        ))

    for note in report.notes:
        print(f"{YELLOW}note{RESET}  {note}")
    for failure in report.failures:
        print(f"{RED}FAIL{RESET}  {failure}")

    if report.failures:
        print(f"\n{RED}{BOLD}{len(report.failures)} failure(s){RESET}")
        return 1
    print(f"\n{GREEN}{BOLD}gate passed{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
