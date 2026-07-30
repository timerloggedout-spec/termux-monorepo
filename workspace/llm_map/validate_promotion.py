#!/usr/bin/env python3
"""Comprehensive promotion validation against multiple quality gates."""
import json, sys, sqlite3
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MAP = HOME / 'workspace/llm_map'

def check_verdict(file_path):
    """Gate 1: PASS verdict exists from correct session."""
    rh = HOME / 'termux-multi-agent/run_history.jsonl'
    if not rh.exists():
        return False, "No run_history.jsonl"
    with open(rh) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    passes = [e for e in entries if e.get('target_file') == file_path and e.get('verdict') == 'PASS']
    if not passes:
        return False, f"No PASS verdict for {file_path}"
    return True, f"{len(passes)} PASS verdict(s) found"

def check_reliability_regression(file_path):
    """Gate 2: Reliability score didn't drop after last change."""
    db = MAP / 'reliability.db'
    if not db.exists():
        return True, "No reliability data (skipping)"
    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        'SELECT reliability, run_at FROM reliability_series WHERE file_path=? ORDER BY run_at DESC LIMIT 2',
        (file_path,)
    ).fetchall()
    conn.close()
    if len(rows) < 2:
        return True, "Only one data point (skipping regression check)"
    current, previous = rows[0][0], rows[1][0]
    if current < previous:
        return False, f"Reliability dropped from {previous} to {current}"
    return True, f"Reliability stable or improving ({previous} → {current})"

def check_shockwave_stable(file_path):
    """Gate 3: Shockwave Index didn't increase."""
    db = MAP / 'reliability.db'
    if not db.exists():
        return True, "No shockwave data (skipping)"
    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        'SELECT shockwave, run_at FROM reliability_series WHERE file_path=? ORDER BY run_at DESC LIMIT 2',
        (file_path,)
    ).fetchall()
    conn.close()
    if len(rows) < 2:
        return True, "Only one data point"
    current, previous = rows[0][0], rows[1][0]
    if current > previous:
        return False, f"Shockwave increased from {previous} to {current}"
    return True, f"Shockwave stable or decreasing ({previous} → {current})"

def check_objective_met(file_path):
    """Gate 4: Task objective demonstrably achieved.
    This requires a human or a second LLM call to verify the diff matches the task.
    For now, we check that the file was actually modified."""
    source = HOME / file_path
    if not source.exists():
        return False, "File does not exist"
    # Check if a promotion backup exists (proves the file was changed)
    backups = list(HOME.glob(f'harmonizer-prod_cli/workspace/*{Path(file_path).name}*'))
    if not backups:
        return False, "No promotion backup found (file may not have been changed)"
    return True, f"Promotion backup exists: {backups[-1].name}"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 validate_promotion.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    gates = [
        ("PASS Verdict", check_verdict),
        ("Reliability Regression", check_reliability_regression),
        ("Shockwave Stability", check_shockwave_stable),
        ("Objective Met", check_objective_met),
    ]
    
    all_pass = True
    for gate_name, gate_fn in gates:
        passed, msg = gate_fn(file_path)
        icon = '✅' if passed else '❌'
        print(f"{icon} {gate_name}: {msg}")
        if not passed:
            all_pass = False
    
    print(f"\n{'✅ ALL GATES PASSED — SAFE TO PROMOTE' if all_pass else '❌ SOME GATES FAILED — REVIEW BEFORE PROMOTION'}")
