#!/usr/bin/env python3
"""
termux_smoke.py — Agentic Termux smoke-test gate.

Purpose
-------
Verify that the *runtime surface* agents rely on is actually alive on a
Termux (or Termux-like) device / CI runner. This sits *after* the cheap
repo-gate (hygiene/portability/secrets) and *before* heavy provider or
Rust builds.

Design rules (same constitution as repo_gate):

  * stdlib only for the core path — no pip, no cargo, no node, no network
    required to pass the default checks
  * runs identically on-device and in CI
  * fail-fast on broken entrypoints; soft-skip optional components with NOTES
  * never mutates the repo or the device state

Usage:
  python3 scripts/ci/termux_smoke.py
  python3 scripts/ci/termux_smoke.py --strict          # treat NOTES as FAIL
  python3 scripts/ci/termux_smoke.py --json            # machine-readable
  python3 scripts/ci/termux_smoke.py --with-optional   # also probe deepcli etc.

Suites: see scripts/ci/termux_smoke/TRACKING.md

Exit codes:
  0  all required checks passed
  1  one or more required checks failed
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BOLD, RED, YELLOW, GREEN, DIM, RESET = (
    ("\033[1m", "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m")
    if sys.stdout.isatty()
    else ("", "", "", "", "", "")
)


@dataclass
class CheckResult:
    name: str
    status: str  # PASS | FAIL | SKIP | NOTE
    detail: str = ""
    required: bool = True


@dataclass
class SmokeReport:
    results: list[CheckResult] = field(default_factory=list)
    environment: dict = field(default_factory=dict)

    def add(self, r: CheckResult) -> None:
        self.results.append(r)

    @property
    def failed(self) -> list[CheckResult]:
        return [r for r in self.results if r.status == "FAIL" and r.required]

    @property
    def notes(self) -> list[CheckResult]:
        return [r for r in self.results if r.status in ("NOTE", "SKIP") or (r.status == "FAIL" and not r.required)]


def detect_environment() -> dict:
    prefix = os.environ.get("PREFIX", "")
    is_termux = (
        "com.termux" in prefix
        or os.path.isdir("/data/data/com.termux")
        or "TERMUX_VERSION" in os.environ
        or os.environ.get("TERMUX", "") == "1"
    )
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "is_termux": is_termux,
        "prefix": prefix or None,
        "home": str(Path.home()),
        "cwd": str(Path.cwd()),
        "repo_root": str(REPO_ROOT),
    }


def run_cmd(argv: list[str], timeout: float = 15.0) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"not found: {argv[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as exc:  # noqa: BLE001 — smoke must never crash itself
        return 1, "", str(exc)


def check_python_runtime(report: SmokeReport) -> None:
    v = sys.version_info
    if v < (3, 9):
        report.add(CheckResult("python-version", "FAIL", f"{v.major}.{v.minor} < 3.9", required=True))
    else:
        report.add(CheckResult("python-version", "PASS", f"{v.major}.{v.minor}.{v.micro}"))


def check_repo_layout(report: SmokeReport) -> None:
    required_paths = [
        "scripts/ci/repo_gate.py",
        "scripts/ci/termux_smoke.py",
        "docs/ARCHW1Z-GATE.md",
    ]
    missing = [p for p in required_paths if not (REPO_ROOT / p).exists()]
    if missing:
        report.add(CheckResult("repo-layout", "FAIL", f"missing: {', '.join(missing)}"))
    else:
        report.add(CheckResult("repo-layout", "PASS", "gate scripts + docs present"))


def check_repo_gate_importable(report: SmokeReport) -> None:
    path = REPO_ROOT / "scripts/ci/repo_gate.py"
    if not path.exists():
        report.add(CheckResult("repo-gate-present", "FAIL", "scripts/ci/repo_gate.py missing"))
        return
    rc, out, err = run_cmd([sys.executable, "-m", "py_compile", str(path)])
    if rc != 0:
        report.add(CheckResult("repo-gate-compile", "FAIL", err or out or f"rc={rc}"))
    else:
        report.add(CheckResult("repo-gate-compile", "PASS", "compiles clean"))


def check_self_compile(report: SmokeReport) -> None:
    path = REPO_ROOT / "scripts/ci/termux_smoke.py"
    rc, out, err = run_cmd([sys.executable, "-m", "py_compile", str(path)])
    if rc != 0:
        report.add(CheckResult("smoke-self-compile", "FAIL", err or out or f"rc={rc}"))
    else:
        report.add(CheckResult("smoke-self-compile", "PASS", "compiles clean"))


def check_git_available(report: SmokeReport) -> None:
    if shutil.which("git") is None:
        report.add(CheckResult("git", "FAIL", "git not on PATH (required for index-based gates)"))
        return
    rc, out, err = run_cmd(["git", "--version"])
    if rc != 0:
        report.add(CheckResult("git", "FAIL", err or out))
    else:
        report.add(CheckResult("git", "PASS", out or "ok"))


def check_bash_available(report: SmokeReport) -> None:
    bash = shutil.which("bash")
    if bash is None:
        env = report.environment
        if env.get("is_termux"):
            report.add(CheckResult("bash", "FAIL", "bash missing on Termux", required=True))
        else:
            report.add(CheckResult("bash", "NOTE", "bash not found — shell syntax checks in repo-gate will skip", required=False))
        return
    report.add(CheckResult("bash", "PASS", bash))


def check_writable_tmp(report: SmokeReport) -> None:
    tmp = Path(os.environ.get("TMPDIR") or os.environ.get("TMP") or "/tmp")
    try:
        probe = tmp / f".archwiz-smoke-{os.getpid()}"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink(missing_ok=True)
        report.add(CheckResult("writable-tmp", "PASS", str(tmp)))
    except OSError as exc:
        report.add(CheckResult("writable-tmp", "FAIL", f"{tmp}: {exc}"))


def check_connectors_suite(report: SmokeReport) -> None:
    """Run scripts/ci/termux_smoke/connectors offline suite (#70 tracking)."""
    entry = REPO_ROOT / "scripts/ci/termux_smoke/connectors/smoke_connectors.py"
    connectors_dir = REPO_ROOT / ".github" / "connectors"
    if not entry.is_file():
        if connectors_dir.is_dir():
            report.add(
                CheckResult(
                    "connectors-suite",
                    "FAIL",
                    "connectors present but scripts/ci/termux_smoke/connectors/smoke_connectors.py missing",
                )
            )
        else:
            report.add(CheckResult("connectors-suite", "NOTE", "no connectors tree and no suite entry", required=False))
        return
    rc, out, err = run_cmd([sys.executable, str(entry)], timeout=45.0)
    detail = (out or err or f"rc={rc}").replace("\n", " | ")[:240]
    if rc != 0:
        report.add(CheckResult("connectors-suite", "FAIL", detail))
    else:
        report.add(CheckResult("connectors-suite", "PASS", detail or "ok"))


def check_deepcli_surface(report: SmokeReport) -> None:
    candidates = [
        REPO_ROOT / "deepcli",
        REPO_ROOT / "deepcli-tui",
        REPO_ROOT / "multi-ai-cli",
        REPO_ROOT / "bin",
    ]
    found = [str(p.relative_to(REPO_ROOT)) for p in candidates if p.exists()]
    if not found:
        report.add(CheckResult("deepcli-surface", "NOTE", "no deepcli/multi-ai trees present", required=False))
        return

    launchers = []
    for root in candidates:
        if not root.is_dir():
            continue
        for name in ("__main__.py", "cli.py", "main.py"):
            candidate = root / name
            if candidate.exists():
                launchers.append(candidate)

    if not launchers:
        report.add(
            CheckResult(
                "deepcli-surface",
                "NOTE",
                f"trees present ({', '.join(found)}) but no obvious launcher",
                required=False,
            )
        )
        return

    ok = True
    details = []
    for launcher in launchers[:5]:
        rc, out, err = run_cmd([sys.executable, "-m", "py_compile", str(launcher)])
        rel = str(launcher.relative_to(REPO_ROOT))
        if rc != 0:
            ok = False
            details.append(f"{rel}: {err or out or rc}")
        else:
            details.append(f"{rel}: compile-ok")

    report.add(
        CheckResult(
            "deepcli-surface",
            "PASS" if ok else "FAIL",
            "; ".join(details),
            required=False,
        )
    )


def check_archwiz_surface(report: SmokeReport) -> None:
    archwiz = REPO_ROOT / "archwiz"
    if not archwiz.exists():
        report.add(CheckResult("archwiz-surface", "NOTE", "archwiz/ not present", required=False))
        return
    py_files = list(archwiz.rglob("*.py"))
    if not py_files:
        report.add(CheckResult("archwiz-surface", "NOTE", "archwiz/ has no .py files", required=False))
        return
    sample = sorted(py_files, key=lambda p: len(p.parts))[:8]
    failures = []
    for path in sample:
        rc, out, err = run_cmd([sys.executable, "-m", "py_compile", str(path)], timeout=10.0)
        if rc != 0:
            failures.append(f"{path.relative_to(REPO_ROOT)}: {err or out or rc}")
    if failures:
        report.add(CheckResult("archwiz-surface", "FAIL", "; ".join(failures[:3]), required=False))
    else:
        report.add(
            CheckResult(
                "archwiz-surface",
                "PASS",
                f"sampled {len(sample)}/{len(py_files)} modules compile-ok",
                required=False,
            )
        )


def check_termux_api_hint(report: SmokeReport) -> None:
    if shutil.which("termux-battery-status") or shutil.which("termux-info"):
        report.add(CheckResult("termux-api", "PASS", "termux-api binaries visible", required=False))
    elif report.environment.get("is_termux"):
        report.add(
            CheckResult(
                "termux-api",
                "NOTE",
                "Termux detected but termux-api not on PATH (optional for agents)",
                required=False,
            )
        )
    else:
        report.add(CheckResult("termux-api", "SKIP", "not on Termux", required=False))


def print_human(report: SmokeReport) -> None:
    env = report.environment
    print(f"{BOLD}termux smoke{RESET} — python {env.get('python')} — termux={env.get('is_termux')}")
    print(f"  {DIM}platform{RESET} {env.get('platform')}")
    print(f"  {DIM}repo{RESET}     {env.get('repo_root')}")
    print()
    for r in report.results:
        color = {
            "PASS": GREEN,
            "FAIL": RED,
            "NOTE": YELLOW,
            "SKIP": DIM,
        }.get(r.status, "")
        req = "" if r.required else f" {DIM}(optional){RESET}"
        detail = f" — {r.detail}" if r.detail else ""
        print(f"  {color}{r.status:4}{RESET}  {r.name}{req}{detail}")
    print()
    if report.failed:
        print(f"{RED}{BOLD}{len(report.failed)} required failure(s){RESET}")
    else:
        print(f"{GREEN}{BOLD}smoke passed{RESET}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat optional FAILs as required")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--with-optional", action="store_true", help="probe deepcli/archwiz surfaces")
    parser.add_argument("--light", action="store_true", help="run only fast, essential checks")
    args = parser.parse_args()

    report = SmokeReport()
    report.environment = detect_environment()

    check_python_runtime(report)
    check_repo_layout(report)
    check_repo_gate_importable(report)
    check_self_compile(report)

    if not args.light:
        check_git_available(report)
        check_bash_available(report)
        check_writable_tmp(report)
        check_connectors_suite(report)

    if args.with_optional:
        check_deepcli_surface(report)
        check_archwiz_surface(report)
        check_termux_api_hint(report)

    if args.strict:
        for r in report.results:
            if r.status == "FAIL":
                r.required = True

    if args.json:
        payload = {
            "environment": report.environment,
            "results": [asdict(r) for r in report.results],
            "ok": not report.failed,
        }
        print(json.dumps(payload, indent=2))
    else:
        print_human(report)

    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
