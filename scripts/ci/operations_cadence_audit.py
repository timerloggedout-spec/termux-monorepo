#!/usr/bin/env python3
"""Operations cadence audit.

The Actions workflow id 362815777 (Operations Cadence Audit) stayed registered
after .github/workflows/operations-cadence-audit.yml left master. Last run
35548390883 (2026-09-21) failed on a NoneType schedule drift assertion.

This audit does not enforce a single cron. It fails only when a workflow file
declares an on.schedule block and never names a non-empty cron.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows"
CRON = re.compile(r"cron\s*:\s*['\"]([^'\"]+)['\"]")
SCHEDULE = re.compile(r"^\s*schedule\s*:", re.M)


def _regex_schedule(text: str) -> tuple[bool, list[str]]:
    crons = [c for c in CRON.findall(text) if c.strip()]
    return bool(SCHEDULE.search(text)), crons


def _yaml_schedule(text: str) -> tuple[bool, list[str]] | None:
    try:
        import yaml
    except ImportError:
        return None
    try:
        doc = yaml.safe_load(text)
    except Exception:
        return None
    if not isinstance(doc, dict):
        return False, []
    # PyYAML 1.1 parses the bare key `on` as boolean True.
    trigger = doc.get(True, doc.get("on"))
    if trigger is None or isinstance(trigger, (str, list)):
        return False, []
    if not isinstance(trigger, dict):
        return False, []
    schedule = trigger.get("schedule")
    if not schedule:
        return False, []
    rows = schedule if isinstance(schedule, list) else [schedule]
    crons: list[str] = []
    for item in rows:
        if isinstance(item, dict) and str(item.get("cron") or "").strip():
            crons.append(str(item["cron"]).strip())
    return True, crons


def schedule_of(text: str) -> tuple[bool, list[str]]:
    parsed = _yaml_schedule(text)
    if parsed is not None:
        return parsed
    return _regex_schedule(text)


def main() -> int:
    files = sorted(WF.glob("*.yml")) + sorted(WF.glob("*.yaml"))
    if not files:
        print("FAIL: no workflow files")
        return 1
    missing_cron = []
    cron_rows = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        has_schedule, crons = schedule_of(text)
        if has_schedule and not crons:
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
