#!/usr/bin/env python3
"""live-1-wave-framing ledger auditor (DOE-FAMILY rule 5 automation).

Verifies a Jules dispatch against the campaign's pre-registered
assignment ledger (experiments/doe/live-1-wave-framing/records/
assignments.jsonl): the ledger line for the issue must exist BEFORE
dispatch and the dispatch stamp on the issue must match it (framing,
entry, entry_class, ledger slot). Any mismatch, a missing ledger
line, or a missing stamp makes the dispatch OBSERVATIONAL — flagged
in the emitted EXPERIMENT record, never a silent pass.

Input is an issue JSON object {number, title, body} (the workflow
exports it via `gh issue view --json`); the auditor is offline and
deterministic apart from the observed_at run stamp.

Exit code: 0 = designed_ok, 3 = observational (record still written).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

CAMPAIGN = "live-1-wave-framing"
STAMP_RE = re.compile(
    r"<!--\s*live-1-wave-framing\s*\|\s*framing:\s*([^|]+?)\s*\|"
    r"\s*entry:\s*([^|]+?)\s*\|\s*entry_class:\s*([^|]+?)\s*\|"
    r"\s*ledger slot:\s*(\d+)\s*-->")


def parse_stamp(body: str) -> dict | None:
    m = STAMP_RE.search(body or "")
    if not m:
        return None
    return {"framing": m.group(1).strip(), "entry": m.group(2).strip(),
            "entry_class": m.group(3).strip(), "slot": int(m.group(4))}


def load_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in
            path.read_text().splitlines() if line.strip()]


def audit(ledger: list[dict], issue: dict) -> dict:
    """Return {verdict, checks{...}, assignment|None, stamp|None}."""
    num = issue["number"]
    stamp = parse_stamp(issue.get("body") or "")
    lines = [l for l in ledger if l.get("issue") == num]
    checks = {"ledger_line_exists": bool(lines),
              "stamp_present": stamp is not None,
              "framing_matches": False, "entry_matches": False,
              "entry_class_matches": False, "slot_matches": False}
    assignment = lines[0] if lines else None
    if assignment and stamp:
        checks["framing_matches"] = \
            assignment.get("framing") == stamp["framing"]
        checks["entry_matches"] = \
            assignment.get("entry") == stamp["entry"]
        checks["entry_class_matches"] = \
            assignment.get("entry_class") == stamp["entry_class"]
        checks["slot_matches"] = \
            assignment.get("slot") == stamp["slot"]
    designed = all(checks.values())
    return {"verdict": "designed_ok" if designed else "observational",
            "checks": checks, "assignment": assignment, "stamp": stamp}


def build_record(issue: dict, result: dict, base_sha: str,
                 observed_at: str) -> dict:
    a = result["assignment"] or {}
    verdict = result["verdict"]
    failed = [k for k, v in result["checks"].items() if not v]
    return {
        "schema_version": "1.0",
        "experiment_id": f"live1-audit-{issue['number']}",
        "suite": f"doe-family:{CAMPAIGN}",
        "observed_at": observed_at,
        "baseline_sha": base_sha,
        "candidate_sha": base_sha,
        "treatment": {
            "manager_policy_id": "doe-mgr-live-builds/live-1-auditor/v1",
            "arm": a.get("framing") or "unassigned",
            "instance": None},
        "provenance": "github",
        "confidence": "high",
        "status": "passed" if verdict == "designed_ok" else "observed",
        "outcome": verdict,
        "metrics": {
            "issue": issue["number"],
            "entry": a.get("entry"),
            "entry_class": a.get("entry_class"),
            "framing_ledger": a.get("framing"),
            "framing_stamp": (result["stamp"] or {}).get("framing"),
            "checks_passed": sum(1 for v in result["checks"].values()
                                 if v),
            "checks_total": len(result["checks"]),
            "checks_failed": ",".join(failed) if failed else None,
            "observational_reason": (
                None if verdict == "designed_ok" else
                "ledger/stamp audit failed: " + ", ".join(failed)),
        },
        "evidence_refs": [
            "experiments/doe/live-1-wave-framing/records/"
            "assignments.jsonl",
            f"github issue #{issue['number']} (live-1 stamp comment)"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--issue-json", required=True)
    ap.add_argument("--records-dir", required=True)
    ap.add_argument("--base-sha", required=True)
    args = ap.parse_args()

    issue = json.loads(Path(args.issue_json).read_text())
    ledger = load_ledger(Path(args.ledger))
    result = audit(ledger, issue)
    observed = dt.datetime.now(dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    record = build_record(issue, result, args.base_sha, observed)
    records = Path(args.records_dir)
    records.mkdir(parents=True, exist_ok=True)
    name = f"{(result['assignment'] or {}).get('entry') or 'unassigned'}" \
           f"-{issue['number']}-audit.json"
    (records / name).write_text(json.dumps(record, indent=1))
    print(f"issue #{issue['number']}: {result['verdict']} "
          f"checks={result['checks']}")
    return 0 if result["verdict"] == "designed_ok" else 3


if __name__ == "__main__":
    sys.exit(main())
