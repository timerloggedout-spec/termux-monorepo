#!/usr/bin/env python3
"""cb-1-chronomancer-emission acceptance CI (DOE-FAMILY rule 5, WO-C).

Runs the campaign's deterministic acceptance A1-A6 against an arm
implementation, independently of the arm's own fixtures: the checker
builds the canonical fixture itself (per the cb-1 DESIGN task
contract), runs the emitter twice via its contract CLI
(`chronomancer_emitter.py <db> <out_dir> --baseline-sha <sha>`), and
verifies:

  A1 every emitted record validates against EXPERIMENT.schema.json
  A2 pairing exact: continuation count == paired-fork count; every
     continuation's metrics.pair_id matches exactly one fork; zero
     orphans; unpaired forks carry pairing=pending
  A3 fixture record count == 5 (2 pairs + 1 unpaired fork)
  A4 two runs byte-identical (file set + sha256 per file)
  A5 source DB sha256 unchanged by the runs
  A6 scope: PR files subset of the allowed paths, and the arm's own
     test file passes under pytest

Output: JSON report {checks: {A1..A6}, detail, verdict};
exit 0 iff verdict == pass. The workflow posts the report as a PR
comment; the job conclusion is the check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

# Canonical fixture (cb-1 DESIGN fixture_spec): fork rows carry the
# NEW forked session id (chronomancer.py insertion semantics).
# rowid: 1 s41 normal | 2 s42 normal | 3 fork->s43 | 4 s43 cont |
#        5 fork->s44 | 6 s44 cont | 7 fork->s45 (no continuation)
FIXTURE_ROWS = [
    ("session-41", "acct-a", "2026-10-01T10:00:00Z", 1,
     "src/a.py", 1, "patch-41", "accepted"),
    ("session-42", "acct-a", "2026-10-02T10:00:00Z", 1,
     "src/b.py", 1, "patch-42", "accepted"),
    ("session-43", "acct-a", "2026-10-03T10:00:00Z", 1,
     "chronomancer-fork", 1, "fork at session-42", "time_loop"),
    ("session-43", "acct-a", "2026-10-04T10:00:00Z", 1,
     "src/c.py", 1, "patch-43", "accepted"),
    ("session-44", "acct-b", "2026-10-05T10:00:00Z", 1,
     "chronomancer-fork", 1, "fork at session-43", "time_loop"),
    ("session-44", "acct-b", "2026-10-06T10:00:00Z", 1,
     "src/d.py", 1, "patch-44", "accepted"),
    ("session-45", "acct-b", "2026-10-07T10:00:00Z", 1,
     "chronomancer-fork", 1, "fork at session-44", "time_loop"),
]
EXPECTED_IDS = {"cb1-chrono-3-fork", "cb1-chrono-3-cont",
                "cb1-chrono-5-fork", "cb1-chrono-5-cont",
                "cb1-chrono-7-fork"}
ALLOWED_FILES = {"scripts/doe/chronomancer_emitter.py",
                 "tests/test_chronomancer_emitter.py"}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_fixture(db: Path) -> None:
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE run_history (session_id TEXT, "
                "account TEXT, timestamp TEXT, validated INTEGER, "
                "target_file TEXT, attempt_number INTEGER, "
                "patch_content TEXT, verdict TEXT)")
    con.executemany("INSERT INTO run_history VALUES (?,?,?,?,?,?,?,?)",
                    FIXTURE_ROWS)
    con.commit()
    con.close()


def run_emitter(emitter: Path, db: Path, out: Path,
                base_sha: str) -> int:
    return subprocess.run(
        [sys.executable, str(emitter), str(db), str(out),
         "--baseline-sha", base_sha], capture_output=True).returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emitter", required=True)
    ap.add_argument("--arm-tests", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--files", default="",
                    help="comma-separated PR file list (A6 scope)")
    ap.add_argument("--baseline-sha", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    checks: dict[str, str] = {}
    detail: dict[str, str] = {}
    emitter = Path(args.emitter)
    files = {f for f in args.files.split(",") if f}
    scope_ok = files <= ALLOWED_FILES
    detail["A6_scope"] = f"files={sorted(files)}"

    if not emitter.exists():
        checks = {k: "fail" for k in
                  ("A1", "A2", "A3", "A4", "A5", "A6")}
        detail["error"] = "emitter file missing"
    else:
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            db = tdp / "fixture.db"
            build_fixture(db)
            db_hash = sha256_file(db)
            out1, out2 = tdp / "run1", tdp / "run2"
            out1.mkdir()
            out2.mkdir()
            rc1 = run_emitter(emitter, db, out1, args.baseline_sha)
            rc2 = run_emitter(emitter, db, out2, args.baseline_sha)
            checks["A5"] = "pass" if sha256_file(db) == db_hash \
                else "fail"
            f1 = {p.name: p.read_bytes()
                  for p in sorted(out1.glob("*.json"))}
            f2 = {p.name: p.read_bytes()
                  for p in sorted(out2.glob("*.json"))}
            checks["A3"] = "pass" if (rc1 == 0
                                      and set(f1) == {i + ".json" for i
                                                      in EXPECTED_IDS}) \
                else "fail"
            detail["A3_files"] = f"rc={rc1} files={sorted(f1)}"
            checks["A4"] = "pass" if (rc2 == 0 and f1 == f2
                                      and len(f1) == 5) else "fail"
            recs = {}
            try:
                import jsonschema
                schema = json.loads(Path(args.schema).read_text())
                for name, blob in f1.items():
                    rec = json.loads(blob)
                    jsonschema.validate(rec, schema)
                    recs[rec["experiment_id"]] = rec
                checks["A1"] = "pass" if len(recs) == 5 else "fail"
            except Exception as e:
                checks["A1"] = "fail"
                detail["A1_error"] = f"{type(e).__name__}: {e}"[:300]
            try:
                forks = {i: r for i, r in recs.items()
                         if r["treatment"]["arm"] == "fork"}
                conts = {i: r for i, r in recs.items()
                         if r["treatment"]["arm"] == "continuation"}
                paired = {i: r for i, r in forks.items()
                          if r["metrics"].get("pairing") != "pending"}
                pair_ids = [r["metrics"]["pair_id"]
                            for r in conts.values()]
                a2 = (len(conts) == len(paired) == 2
                      and forks["cb1-chrono-7-fork"]["metrics"]
                      .get("pairing") == "pending"
                      and sorted(pair_ids) == ["cb1-pair-3",
                                               "cb1-pair-5"]
                      and all(forks[f"cb1-chrono-{pid.split('-')[-1]}"
                                    "-fork"]["metrics"]["pair_id"]
                              == pid for pid in pair_ids))
                checks["A2"] = "pass" if a2 else "fail"
            except Exception as e:
                checks["A2"] = "fail"
                detail["A2_error"] = f"{type(e).__name__}: {e}"[:300]
        tp = subprocess.run(
            [sys.executable, "-m", "pytest", args.arm_tests, "-q"],
            capture_output=True, text=True)
        checks["A6"] = "pass" if (scope_ok
                                  and tp.returncode == 0) else "fail"
        if tp.returncode != 0:
            detail["A6_tests"] = (tp.stdout + tp.stderr)[-300:]

    verdict = "pass" if all(v == "pass" for v in checks.values()) \
        else "fail"
    report = {"campaign_id": "cb-1-chronomancer-emission",
              "checks": checks, "detail": detail, "verdict": verdict,
              "baseline_sha": args.baseline_sha}
    Path(args.report).write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
