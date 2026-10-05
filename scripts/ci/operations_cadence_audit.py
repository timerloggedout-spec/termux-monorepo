#!/usr/bin/env python3
"""Operations cadence audit.

The Actions workflow id 362815777 (Operations Cadence Audit) stayed registered
after .github/workflows/operations-cadence-audit.yml left master. Last run
35548390883 (2026-09-21) failed on a NoneType schedule drift assertion.

This audit does not enforce a single cron. It fails only when a workflow file
declares a schedule block and never names a cron.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows"
CRON = re.compile(r"cron\s*:\s*['\"]([^'\"]+)['\"]")
SCHEDULE = re.compile(r"^\s*schedule\s*:", re.M)


def main() -> int:
    files = sorted(WF.glob("*.yml")) + sorted(WF.glob("*.yaml"))
    if not files:
        print("FAIL: no workflow files")
        return 1
    missing_cron = []
    cron_rows = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        crons = CRON.findall(text)
        if SCHEDULE.search(text) and not crons:
            missing_cron.append(path.name)
        for cron in crons:
            cron_rows.append((cron, path.name))
    print(f"workflows={len(files)} scheduled={len(cron_rows)}")
    for cron, name in cron_rows:
        print(f"  {cron}  {name}")
    if missing_cron:
        print("FAIL: schedule block without cron: " + ", ".join(missing_cron))
        return 1
    print("OK: cadence files name a cron when they declare schedule")
    return 0


if __name__ == "__main__":
    sys.exit(main())
