#!/usr/bin/env python3
"""Offline smoke for .github/connectors/ (from #70).

stdlib core path — no network, no secrets required to PASS.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONNECTORS = REPO_ROOT / ".github" / "connectors"

REQUIRED_FILES = [
    "connector_manager.py",
    "health_check.sh",
    "llm_providers.yaml",
    "github.yaml",
    "webhooks.yaml",
    "exchanges.yaml",
]


@dataclass
class Result:
    name: str
    status: str  # PASS | FAIL | NOTE | SKIP
    detail: str = ""
    required: bool = True


@dataclass
class Report:
    results: list[Result] = field(default_factory=list)

    def add(self, r: Result) -> None:
        self.results.append(r)

    @property
    def failed(self) -> list[Result]:
        return [r for r in self.results if r.status == "FAIL" and r.required]


def check_dir(report: Report) -> None:
    if not CONNECTORS.is_dir():
        report.add(Result("connectors-dir", "FAIL", f"missing {CONNECTORS}"))
        return
    report.add(Result("connectors-dir", "PASS", str(CONNECTORS.relative_to(REPO_ROOT))))


def check_files(report: Report) -> None:
    missing = [f for f in REQUIRED_FILES if not (CONNECTORS / f).is_file()]
    if missing:
        report.add(Result("connectors-files", "FAIL", f"missing: {', '.join(missing)}"))
    else:
        report.add(Result("connectors-files", "PASS", f"{len(REQUIRED_FILES)} required files present"))


def check_manager_compile(report: Report) -> None:
    path = CONNECTORS / "connector_manager.py"
    if not path.is_file():
        report.add(Result("connector-manager-compile", "FAIL", "connector_manager.py missing"))
        return
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        report.add(Result("connector-manager-compile", "FAIL", (proc.stderr or proc.stdout or f"rc={proc.returncode}")[:300]))
    else:
        report.add(Result("connector-manager-compile", "PASS", "compiles clean"))


def check_health_script(report: Report) -> None:
    path = CONNECTORS / "health_check.sh"
    if not path.is_file():
        report.add(Result("health-check-syntax", "FAIL", "health_check.sh missing"))
        return
    bash = shutil.which("bash")
    if not bash:
        report.add(Result("health-check-syntax", "NOTE", "bash not on PATH — skip syntax check", required=False))
        return
    proc = subprocess.run([bash, "-n", str(path)], capture_output=True, text=True, timeout=15)
    if proc.returncode != 0:
        report.add(Result("health-check-syntax", "FAIL", (proc.stderr or proc.stdout or f"rc={proc.returncode}")[:300]))
    else:
        report.add(Result("health-check-syntax", "PASS", "bash -n clean"))


def check_list_optional(report: Report) -> None:
    """Attempt list_connectors if PyYAML is available; never network."""
    path = CONNECTORS / "connector_manager.py"
    if not path.is_file():
        report.add(Result("connectors-list", "SKIP", "no manager", required=False))
        return
    code = (
        "import sys; sys.path.insert(0, %r); "
        "from connector_manager import ConnectorManager; "
        "m = ConnectorManager(); "
        "c = m.list_connectors(); "
        "print(','.join(sorted(c.keys())) if isinstance(c, dict) else type(c).__name__)"
    ) % str(CONNECTORS)
    env = {**os.environ, "PYTHONPATH": str(CONNECTORS)}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        if "yaml" in err.lower() or "ModuleNotFoundError" in err:
            report.add(Result("connectors-list", "NOTE", "PyYAML/requests not installed — list skipped (ok for core)", required=False))
        else:
            report.add(Result("connectors-list", "NOTE", err[:200], required=False))
    else:
        report.add(Result("connectors-list", "PASS", proc.stdout.strip() or "ok", required=False))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = Report()
    check_dir(report)
    check_files(report)
    check_manager_compile(report)
    check_health_script(report)
    check_list_optional(report)
    if args.json:
        print(json.dumps({"results": [asdict(r) for r in report.results], "ok": not report.failed}, indent=2))
    else:
        for r in report.results:
            req = "" if r.required else " (optional)"
            detail = f" — {r.detail}" if r.detail else ""
            print(f"{r.status:4}  {r.name}{req}{detail}")
        print("connectors smoke PASSED" if not report.failed else f"connectors smoke FAILED ({len(report.failed)})")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
