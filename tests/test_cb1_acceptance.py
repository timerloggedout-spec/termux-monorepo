"""Tests for the cb-1 acceptance checker (rule-5 automation, WO-C).

Uses a minimal reference emitter built to the cb-1 DESIGN contract
CLI + record shape, plus a deliberately unstable emitter, to pin
the A-checks' behavior.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/doe/cb1_acceptance.py"
BASE = "a" * 40

GOOD_EMITTER = '''
import json, sqlite3, sys
from pathlib import Path

def rec(rid, kind, row, base, pair_id, pairing=None):
    m = {"pair_id": pair_id, "session_id": row[1], "account": row[2],
         "verdict": row[8], "source_rowid": row[0],
         "fork_policy": "NOT ESTABLISHED",
         "injected_summary_sha256": "NOT ESTABLISHED"}
    if pairing is not None:
        m["pairing"] = pairing
    return {"schema_version": "1.0", "experiment_id": rid,
            "suite": "doe-family:cb-1-chronomancer-emission",
            "cohort": row[2], "observed_at": row[3],
            "baseline_sha": base, "candidate_sha": base,
            "treatment": {"manager_policy_id":
                          "chronomancer/time-loop-fork",
                          "arm": kind, "instance": None},
            "status": "observed", "outcome": None, "metrics": m,
            "provenance": "other", "confidence": "medium"}

def main():
    db, out, base = sys.argv[1], Path(sys.argv[2]), sys.argv[4]
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute("SELECT rowid,* FROM run_history ORDER BY "
                       "timestamp, rowid").fetchall()
    for r in rows:
        if r[5] != "chronomancer-fork":
            continue
        cont = None
        for q in rows:
            if (q[3], q[0]) > (r[3], r[0]) and q[1] == r[1] and \\
                    q[5] != "chronomancer-fork":
                cont = q
                break
        pid = f"cb1-pair-{r[0]}"
        fork = rec(f"cb1-chrono-{r[0]}-fork", "fork", r, base, pid,
                   pairing="paired" if cont else "pending")
        (out / (fork["experiment_id"] + ".json")).write_text(
            json.dumps(fork, indent=1, sort_keys=True))
        if cont:
            crec = rec(f"cb1-chrono-{r[0]}-cont", "continuation",
                       cont, base, pid)
            (out / (crec["experiment_id"] + ".json")).write_text(
                json.dumps(crec, indent=1, sort_keys=True))
    return 0

sys.exit(main())
'''

BAD_EMITTER = GOOD_EMITTER.replace(
    "import json, sqlite3, sys",
    "import json, sqlite3, sys, time").replace(
    '"verdict": row[8],',
    '"verdict": (row[8] or "") + str(time.time_ns()),')


def run_checker(tmp_path, emitter_src, files):
    emitter = tmp_path / "emitter.py"
    emitter.write_text(emitter_src)
    arm_tests = tmp_path / "arm_tests.py"
    arm_tests.write_text("def test_ok():\n    assert True\n")
    report = tmp_path / "report.json"
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--emitter", str(emitter),
         "--arm-tests", str(arm_tests), "--schema",
         str(ROOT / "docs/ops/corpus/EXPERIMENT.schema.json"),
         "--files", files, "--baseline-sha", BASE,
         "--report", str(report)],
        capture_output=True, text=True)
    return proc, json.loads(report.read_text())


def test_good_emitter_passes(tmp_path):
    proc, rep = run_checker(
        tmp_path, GOOD_EMITTER,
        "scripts/doe/chronomancer_emitter.py,"
        "tests/test_chronomancer_emitter.py")
    assert rep["verdict"] == "pass", rep
    assert all(v == "pass" for v in rep["checks"].values())
    assert proc.returncode == 0


def test_unstable_emitter_fails_a4(tmp_path):
    _, rep = run_checker(tmp_path, BAD_EMITTER,
                         "scripts/doe/chronomancer_emitter.py")
    assert rep["checks"]["A4"] == "fail"
    assert rep["verdict"] == "fail"


def test_scope_violation_fails_a6(tmp_path):
    _, rep = run_checker(tmp_path, GOOD_EMITTER,
                         "scripts/doe/chronomancer_emitter.py,"
                         "scripts/doe/other.py")
    assert rep["checks"]["A6"] == "fail"
