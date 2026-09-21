#!/usr/bin/env python3
"""Dependency-free audit of the repository-wide GitHub Actions cadence contract."""
from __future__ import annotations
import argparse, json, pathlib, re, sys
from dataclasses import asdict, dataclass

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"

@dataclass
class Finding:
    level: str
    path: str
    code: str
    message: str

CRON_RE = re.compile(r"""^\s*-\s*cron:\s*['"]([^'"]+)['"]\s*(?:#.*)?$""")
TIMEZONE_RE = re.compile(r"""^\s*timezone:\s*['"]?([^'"\s#]+)['"]?\s*(?:#.*)?$""")
GROUP_RE = re.compile(r"""^\s+group:\s*(.+?)\s*(?:#.*)?$""")
CANCEL_RE = re.compile(r"""^\s+cancel-in-progress:\s*(true|false)\s*(?:#.*)?$""")

def strip_yaml_comment(line: str) -> str:
    """Strip an unquoted YAML comment without touching # inside quotes."""
    quote = None
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and quote == '"':
            escaped = True
            continue
        if ch in ("'", '"'):
            quote = None if quote == ch else (ch if quote is None else quote)
        elif ch == "#" and quote is None and (i == 0 or line[i - 1].isspace()):
            return line[:i].rstrip()
    return line.rstrip()

def event_present(text: str, event: str) -> bool:
    active = "\n".join(strip_yaml_comment(line) for line in text.splitlines())
    return bool(re.search(rf"(?m)^\s{{2}}{re.escape(event)}:\s*$", active))
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mode", choices=("advisory", "enforce"), default="advisory")
    args = ap.parse_args()
    findings: list[Finding] = []
    inventory: list[dict] = []

    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        schedules = []
        generated_gh_aw = "# gh-aw-metadata:" in text
        in_schedule = False
        schedule_indent = 0
        for i, line in enumerate(lines):
            line = strip_yaml_comment(line)
            if re.match(r"^  schedule:\s*$", line):
                in_schedule, schedule_indent = True, 2
                continue
            if in_schedule:
                spaces = len(line) - len(line.lstrip())
                if line.strip() and spaces <= schedule_indent:
                    in_schedule = False
                    continue
                m = CRON_RE.match(line)
                if not m:
                    continue
                cron = m.group(1)
                tz = None
                for child in lines[i + 1:]:
                    if not child.strip():
                        continue
                    child_spaces = len(child) - len(child.lstrip())
                    if child_spaces <= schedule_indent + 2:
                        break
                    tm = TIMEZONE_RE.match(child)
                    if tm:
                        tz = tm.group(1)
                        break
                schedules.append({"cron": cron, "timezone": tz})
                if tz != "UTC" and not generated_gh_aw:
                    findings.append(Finding("error", str(path.relative_to(ROOT)), "schedule-timezone", f"{cron!r} must declare timezone: UTC"))
                elif tz != "UTC" and generated_gh_aw:
                    findings.append(Finding("warning", str(path.relative_to(ROOT)), "generated-schedule-source", f"{cron!r} is compiler-owned by gh-aw; validate the source workflow rather than editing the generated lock file"))
                minute = cron.split()[0] if cron.split() else ""
                if minute in {"0", "*"}:
                    findings.append(Finding("warning", str(path.relative_to(ROOT)), "top-of-hour", f"{cron!r} may concentrate load; prefer a staggered minute"))

        events = {e: event_present(text, e) for e in ("pull_request", "pull_request_target", "issues", "issue_comment")}
        response_event = any(events.values())
        active_text = "\n".join(strip_yaml_comment(line) for line in lines)
        group = GROUP_RE.search(active_text)
        cancel = CANCEL_RE.search(active_text)
        if response_event and not re.search(r"(?m)^\s{0,2}concurrency:\s*$", active_text):
            findings.append(Finding("error", str(path.relative_to(ROOT)), "event-concurrency", "issue/PR response workflow needs an explicit concurrency group"))
        if response_event and group and not any(k in group.group(1) for k in ("github.event.issue.number", "github.event.pull_request.number")):
            findings.append(Finding("warning", str(path.relative_to(ROOT)), "event-lease-key", "response concurrency should normally be keyed to issue/PR identity"))

        inventory.append({
            "workflow": str(path.relative_to(ROOT)),
            "schedules": schedules,
            "events": events,
            "concurrency_group": group.group(1).strip() if group else None,
            "cancel_in_progress": cancel.group(1) if cancel else None,
        })

    report = {
        "schema": "termux.operations-cadence-report/v1",
        "mode": args.mode,
        "workflow_count": len(inventory),
        "inventory": inventory,
        "findings": [asdict(f) for f in findings],
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Operations cadence audit: {len(inventory)} workflows")
        for f in findings:
            print(f"{f.level.upper()}: {f.path}: {f.code}: {f.message}")
    return 1 if args.mode == "enforce" and any(f.level == "error" for f in findings) else 0

if __name__ == "__main__":
    sys.exit(main())
