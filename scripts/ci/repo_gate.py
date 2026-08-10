#!/usr/bin/env python3
"""
repo_gate.py — cheap, device-friendly hygiene gate for termux-monorepo.

ArchW1z invariant gate (P0 spine).

Design constraints:

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
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True
        ).returncode
        == 0
    )


class IndexEntry:
    __slots__ = ("mode", "sha", "path")

    def __init__(self, mode: str, sha: str, path: str) -> None:
        self.mode = mode
        self.sha = sha
        self.path = path

    @property
    def is_symlink(self) -> bool:
        return self.mode == "120000"

    @property
    def is_submodule(self) -> bool:
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
        "origin/master-staging",
        "master-staging",
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
        if entry is None or entry.is_symlink or entry.is_submodule:
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
        if entry is None or entry.is_symlink or entry.is_submodule:
            continue
        checked += 1
        proc = subprocess.run(
            [bash, "-n", "-"], input=blob(entry.sha), capture_output=True
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
        if entry is None or entry.is_symlink or entry.is_submodule:
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
        if entry is None or entry.is_symlink or entry.is_submodule:
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
    for entry in index:
        if not entry.is_symlink:
            continue
        target = symlink_target(entry)
        if target.startswith(DEVICE_PATH_PREFIXES):
            device_symlinks += 1
        elif target.startswith("/"):
            absolute_symlinks += 1

    return {
        "device_absolute_symlinks": device_symlinks,
        "other_absolute_symlinks": absolute_symlinks,
        "tracked_session_artifacts": sum(
            1 for e in index if SESSION_ARTIFACT_RE.search(e.path)
        ),
        "tracked_backup_files": sum(
            1 for e in index if BACKUP_RE.search(Path(e.path).name)
        ),
        "paths_with_spaces": sum(1 for e in index if " " in e.path),
        "tracked_browser_profile_files": sum(
            1 for e in index if BROWSER_PROFILE_RE.search(e.path)
        ),
        "tracked_browser_credential_stores": sum(
            1
            for e in index
            if BROWSER_PROFILE_RE.search(e.path) and BROWSER_CREDENTIAL_RE.search(e.path)
        ),
    }


def check_ratchet(report: Report, index: list[IndexEntry], base_ref: str | None = None) -> dict[str, int]:
    current = measure(index)
    if not BASELINE_PATH.exists():
        report.note(f"no baseline at {BASELINE_PATH.name}; run --write-baseline")
        return current
    # Load baseline from the resolved base commit, not from the workspace
    if base_ref:
        try:
            baseline_json = git("show", f"{base_ref}:scripts/ci/baseline.json").strip()
            baseline = json.loads(baseline_json).get("counters", {})
        except subprocess.CalledProcessError:
            # Base doesn't have baseline.json yet; fall back to workspace
            baseline = json.loads(BASELINE_PATH.read_text()).get("counters", {})
    else:
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
                "symlinks": check_new_symlinks(report, paths, by_path),
                "scanned": check_secrets(report, paths, by_path),
            }
            check_new_debt_paths(report, paths)
            print(
                "  hard checks: "
                + ", ".join(f"{k}={v}" for k, v in counts.items())
            )

    if not args.hard_only:
        current = check_ratchet(report, index, base)
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
